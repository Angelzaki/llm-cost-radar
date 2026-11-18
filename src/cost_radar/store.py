from __future__ import annotations

import json
import statistics
import time
import uuid
from pathlib import Path

from cost_radar.pricing import estimate_cost, estimate_tokens


class CallStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, rows: list[dict]) -> None:
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(
        self,
        route: str,
        model: str,
        prompt: str,
        response: str,
        latency_ms: float,
    ) -> dict:
        tokens_in = estimate_tokens(prompt)
        tokens_out = estimate_tokens(response)
        row = {
            "id": uuid.uuid4().hex[:10],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "route": route,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": round(estimate_cost(model, tokens_in, tokens_out), 6),
            "latency_ms": round(latency_ms, 2),
        }
        rows = self._load()
        rows.append(row)
        self._save(rows)
        return row

    def all(self) -> list[dict]:
        return self._load()

    def summary(self) -> dict:
        rows = self._load()
        if not rows:
            return {
                "calls": 0,
                "cost_usd": 0.0,
                "tokens": 0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "by_route": {},
                "by_model": {},
            }
        lat = sorted(r["latency_ms"] for r in rows)
        p50 = statistics.median(lat)
        idx = max(0, int(0.95 * (len(lat) - 1)))
        p95 = lat[idx]
        by_route: dict[str, dict] = {}
        by_model: dict[str, dict] = {}
        for r in rows:
            br = by_route.setdefault(r["route"], {"calls": 0, "cost_usd": 0.0})
            br["calls"] += 1
            br["cost_usd"] = round(br["cost_usd"] + r["cost_usd"], 6)
            bm = by_model.setdefault(r["model"], {"calls": 0, "cost_usd": 0.0})
            bm["calls"] += 1
            bm["cost_usd"] = round(bm["cost_usd"] + r["cost_usd"], 6)
        return {
            "calls": len(rows),
            "cost_usd": round(sum(r["cost_usd"] for r in rows), 6),
            "tokens": sum(r["tokens_in"] + r["tokens_out"] for r in rows),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "by_route": by_route,
            "by_model": by_model,
        }
