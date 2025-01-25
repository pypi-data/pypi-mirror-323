import io

from fastapi.responses import HTMLResponse, PlainTextResponse
from rich.console import Console
from rich.traceback import Traceback

from ..core.simulate import plot as _plot
from ..core.simulate import simulate as _simulate
from ..models import SimulationData
from .app import app


@app.post("/sax/simulate")
def simulate(data: dict):
    console = Console(record=True)
    try:
        sim_data = SimulationData.model_validate(data)
        df = _simulate(sim_data)
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        csv = buf.getvalue()
    except Exception:
        console.print(Traceback(show_locals=False))
        return PlainTextResponse(export_html(console), status_code=422)
    return PlainTextResponse(csv)


@app.post("/sax/plot-json")
def plot_json(data: dict):
    console = Console(record=True)
    try:
        sim_data = SimulationData.model_validate(data)
        c = _plot(sim_data)
        dct = c.to_dict()
    except Exception:
        console.print(Traceback(show_locals=False))
        return PlainTextResponse(export_html(console), status_code=422)
    return dct


@app.post("/sax/plot-html")
def plot_html(data: dict):
    console = Console(record=True)
    try:
        sim_data = SimulationData.model_validate(data)
        c = _plot(sim_data)
        html = c.to_html()
    except Exception:
        console.print(Traceback(show_locals=False))
        return PlainTextResponse(export_html(console), status_code=422)
    return HTMLResponse(html)


def export_html(console: Console):
    body = console.export_html().split("<body>")[1].split("</body>")[0]
    html_traceback = f"""
    <html>
        <head>
            <style>
                .r1 {{color: #800000; text-decoration-color: #800000}}
                .r2 {{color: #800000; text-decoration-color: #800000; font-weight: bold}}
                .r3 {{color: #bf7f7f; text-decoration-color: #bf7f7f; font-weight: bold}}
                .r4 {{color: #bfbf7f; text-decoration-color: #bfbf7f}}
                .r5 {{color: #808000; text-decoration-color: #808000; font-weight: bold}}
                .r6 {{color: #0000ff; text-decoration-color: #0000ff}}
                .r7 {{color: #00ff00; text-decoration-color: #00ff00}}
                .r8 {{color: #7f7f7f; text-decoration-color: #7f7f7f}}
                .r9 {{color: #00ffff; text-decoration-color: #00ffff}}
                .r10 {{color: #808000; text-decoration-color: #808000}}
                .r11 {{color: #00ffff; text-decoration-color: #00ffff; font-weight: bold; text-decoration: underline}}
                .r12 {{font-weight: bold; text-decoration: underline}}
                .r13 {{color: #7f7f7f; text-decoration-color: #7f7f7f; font-weight: bold; text-decoration: underline}}
                .r14 {{color: #ff0000; text-decoration-color: #ff0000; font-weight: bold}}
                .r15 {{color: #008080; text-decoration-color: #008080; font-weight: bold}}
                .r16 {{color: #008000; text-decoration-color: #008000}}
                .r17 {{font-weight: bold}}
                .r18 {{color: #800080; text-decoration-color: #800080}}
                .r19 {{color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline}}
                body {{
                    color: #000000;
                    background-color: #3B3B3B;
                }}
            </style>
        </head>
        <body>
            {body}
        </body>
    </html>
    """
    return html_traceback
