from pathlib import Path
from typing import Annotated, Any, Literal

import sax
from gdsfactory.read.from_yaml import from_yaml
from pydantic import BaseModel, BeforeValidator, Field
from sax.netlist import RecursiveNetlist as RecursiveNetlist

from gdsfactoryplus.core.shared import get_active_pdk

from .settings import SETTINGS as s
from .settings import Arange, Linspace


class ShowMessage(BaseModel):
    what: Literal["show"] = "show"  # do not override
    mime: (
        Literal[
            "html",
            "json",
            "yaml",
            "plain",
            "base64",
            "png",
            "gds",
            "netlist",
            "dict",
            "error",
        ]
        | None
    ) = None
    content: str


class ErrorMessage(BaseModel):
    what: Literal["error"] = "error"  # do not override
    category: str
    message: str
    path: str


Message = ShowMessage | ErrorMessage


class SimulationConfig(BaseModel):
    """Data model for simulation configuration."""

    pdk: str = s.pdk.name
    wls: Linspace | Arange = s.sim.wls
    op: str = "none"
    port_in: str = ""
    settings: dict[str, Any] = Field(default_factory=dict)


def ensure_recursive_netlist(obj: Any):
    if isinstance(obj, Path):
        obj = str(obj)

    if isinstance(obj, str):
        pdk = get_active_pdk()
        if "\n" in obj or obj.endswith(".pic.yml"):
            c = from_yaml(obj)
        else:
            c = pdk.get_component(obj)
        obj = c.get_netlist(recursive=True)

    if isinstance(obj, sax.Netlist):
        obj = {"top_level": obj.model_dump()}

    if isinstance(obj, sax.RecursiveNetlist):
        obj = obj.model_dump()

    if not isinstance(obj, dict):
        raise ValueError(f"Can't validate obj {obj} into RecursiveNetlist")

    obj = RecursiveNetlist.model_validate(obj)

    return obj


class SimulationData(BaseModel):
    """Data model for simulation."""

    netlist: Annotated[RecursiveNetlist, BeforeValidator(ensure_recursive_netlist)]
    config: SimulationConfig = Field(default_factory=SimulationConfig)
