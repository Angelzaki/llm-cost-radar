from __future__ import annotations

# precios de referencia locales (USD / 1M tokens) — tabla estática offline
PRICES = {
    "haiku": {"in": 0.25, "out": 1.25},
    "sonnet": {"in": 3.0, "out": 15.0},
    "opus": {"in": 15.0, "out": 75.0},
    "local-small": {"in": 0.0, "out": 0.0},
    "local-large": {"in": 0.0, "out": 0.0},
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    price = PRICES.get(model, PRICES["sonnet"])
    return (tokens_in / 1_000_000) * price["in"] + (tokens_out / 1_000_000) * price["out"]


def estimate_tokens(text: str) -> int:
    # aproximación offline: ~4 chars/token
    return max(1, len(text) // 4)
