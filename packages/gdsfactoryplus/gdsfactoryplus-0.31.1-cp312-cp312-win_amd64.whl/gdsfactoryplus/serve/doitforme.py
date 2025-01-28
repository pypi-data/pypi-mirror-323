import json
import sys
from io import StringIO
from typing import Callable, Any

import pandas as pd
import websockets
from gdsfactory import Port
from gdsfactory.schematic import Netlist
from pydantic import BaseModel, ValidationError
from gdsfactory.read.from_yaml import from_yaml
from websockets.exceptions import ConnectionClosedError


from .app import app


def _get_port_dict(port: Port) -> dict:
    return {
        "name": port.name,
        "x": port.dcenter[0],
        "y": port.dcenter[1],
        "angle": port.angle,
        "port_type": port.port_type,
        "width": port.dwidth,
    }


def get_component_description(
    cell: Callable, with_port_summary: bool = True
) -> dict[str, str]:
    description = cell.__doc__ or "No description provided."

    port_summary = ""
    if with_port_summary:
        try:
            c = cell()

            port_info = [_get_port_dict(p) for p in c.ports]
            csv_string = StringIO()
            pd.DataFrame.from_records(port_info).to_csv(csv_string, index=False)

            port_summary = csv_string.getvalue()
        except:
            port_summary = "No port summary available."

    return {"description": description, "port_summary": port_summary}


def validate_netlist(msg: dict) -> dict:
    netlist = msg["netlist"]

    is_valid = True
    error = ""
    try:
        from_yaml(netlist)
    except Exception as e:
        error = str(e)
        is_valid = False

    return {
        "type": "validated",
        "is_valid": is_valid,
        "error": error,
    }

@app.get("/doitforme")
async def doitforme_get(prompt: str = "", url="wss://doitforme.gdsfactory.com/ws"):
    return await websocket_client(
        prompt=prompt,
        url=url,
    )


class DoItForMe(BaseModel):
    prompt: str = ""
    initial_circuit: str = ""
    url: str = "wss://doitforme.gdsfactory.com/ws"


@app.post("/doitforme")
async def doitforme_post(data: DoItForMe):
    print(data, file=sys.stderr)
    return await websocket_client(
        prompt=data.prompt,
        initial_circuit=data.initial_circuit,
        url=data.url,
    )


async def websocket_client(
    prompt: str = "",
    initial_circuit: str = "",
    api_key: str | None = None,
    pdk_name: str | None = None,
    url="wss://doitforme.gdsfactory.com/ws",
) -> dict[str, Any]:
    from gdsfactoryplus.core.shared import activate_pdk_by_name
    from gdsfactoryplus.settings import SETTINGS

    api_key = api_key or SETTINGS.api.key
    pdk_name = pdk_name or SETTINGS.pdk.name

    pdk = activate_pdk_by_name(pdk_name)
    print(f"Using PDK: {pdk.name}", file=sys.stderr)

    component_descriptions = {
        cell_name: get_component_description(cell)
        for cell_name, cell in pdk.cells.items()
    }

    async with websockets.connect(url) as websocket:
        msg = {
            "type": "prompt",
            "api_key": api_key,
            "pdk_name": pdk_name,
            "prompt": prompt,
            "initial_circuit": initial_circuit,
            "descriptions": component_descriptions,
            "api_version": "v1",
        }
        await websocket.send(json.dumps(msg))

        try:
            while True:
                raw = await websocket.recv()
                msg = json.loads(raw)
                msgtype = msg.get("type", "")

                if msgtype == "validate":
                    print("Validating...")
                    validation_result = validate_netlist(msg)
                    netlist = msg["netlist"]

                    await websocket.send(json.dumps(validation_result))

                elif msgtype == "result":
                    netlist_json = msg["netlist"]
                    try:
                        netlist = Netlist.model_validate_json(netlist_json)
                        netlist_dict = netlist.model_dump(
                            exclude_defaults=True, exclude_unset=True
                        )
                    except ValidationError:
                        netlist_dict = json.loads(netlist_json)
                    return netlist_dict
                else:
                    raise RuntimeError(f"Unexpected message type: {msgtype}")
        except ConnectionClosedError:
            raise
