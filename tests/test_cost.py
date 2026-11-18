from pathlib import Path

from cost_radar.pricing import estimate_cost, estimate_tokens
from cost_radar.store import CallStore


def test_pricing_and_store(tmp_path):
    assert estimate_tokens("abcd") == 1
    assert estimate_cost("sonnet", 1000, 1000) > 0
    store = CallStore(tmp_path / "calls.json")
    store.add("ask", "haiku", "hola mundo prueba", "respuesta corta", 90)
    s = store.summary()
    assert s["calls"] == 1
    assert s["p95_ms"] >= 90
