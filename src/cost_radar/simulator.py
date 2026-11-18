from __future__ import annotations

import random
import time


def fake_call(model: str, prompt: str) -> tuple[str, float]:
    start = time.perf_counter()
    base = {
        "haiku": 80,
        "sonnet": 180,
        "opus": 320,
        "local-small": 40,
        "local-large": 120,
    }.get(model, 150)
    time.sleep(min(0.05, base / 5000))
    latency = base + random.uniform(-20, 40)
    response = f"[{model}] respuesta simulada a: {prompt[:80]}"
    _ = time.perf_counter() - start
    return response, max(1.0, latency)
