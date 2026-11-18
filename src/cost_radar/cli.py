from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn
from rich.console import Console
from rich.table import Table

from cost_radar.simulator import fake_call
from cost_radar.store import CallStore

console = Console()
ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cost-radar")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sim = sub.add_parser("simulate")
    sim.add_argument("--route", default="ask")
    sim.add_argument("--model", default="sonnet")
    sim.add_argument("--prompt", default="¿Cuál es el límite comercial?")
    sim.add_argument("--n", type=int, default=1)

    sub.add_parser("summary")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8010)

    args = parser.parse_args(argv)
    store = CallStore(ROOT / "results" / "calls.json")

    if args.cmd == "simulate":
        for _ in range(args.n):
            response, latency = fake_call(args.model, args.prompt)
            row = store.add(args.route, args.model, args.prompt, response, latency)
            console.print(json.dumps(row, ensure_ascii=False))
        return 0

    if args.cmd == "summary":
        s = store.summary()
        table = Table(title="Cost Radar")
        table.add_column("metric")
        table.add_column("value", justify="right")
        table.add_row("calls", str(s["calls"]))
        table.add_row("cost_usd", f"${s['cost_usd']:.4f}")
        table.add_row("tokens", str(s["tokens"]))
        table.add_row("p50_ms", str(s["p50_ms"]))
        table.add_row("p95_ms", str(s["p95_ms"]))
        console.print(table)
        return 0

    if args.cmd == "serve":
        uvicorn.run("cost_radar.app:app", host=args.host, port=args.port, reload=False)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
