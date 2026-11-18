from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cost_radar.simulator import fake_call
from cost_radar.store import CallStore

ROOT = Path(__file__).resolve().parents[2]
STORE = CallStore(ROOT / "results" / "calls.json")
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="llm-cost-radar")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "summary": STORE.summary(),
            "rows": list(reversed(STORE.all()))[:50],
        },
    )


@app.post("/simulate")
def simulate(
    route: str = Form(...),
    model: str = Form(...),
    prompt: str = Form(...),
):
    response, latency = fake_call(model, prompt)
    STORE.add(route=route, model=model, prompt=prompt, response=response, latency_ms=latency)
    return RedirectResponse("/", status_code=303)


@app.get("/api/summary")
def api_summary():
    return STORE.summary()
