"""PUSULA Semantic V2 core ranking primitives.

This module deliberately keeps the original PUSULA identity stable:

    base = 0.70 * intent_fit + 0.15 * freshness + 0.15 * engagement
    score = base * quality
    quality = 1 - clickbait

Semantic V2 improves the signals and adds a separate reranking stage; it does
not silently replace the formula used in the technical report.
"""

from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

INTENT_DIMENSIONS = ("ogretici", "eglendirici", "haber", "sosyal")

INTENTS: dict[str, tuple[float, float, float, float]] = {
    "ogrenmek": (1.00, 0.15, 0.15, 0.05),
    "eglenmek": (0.10, 1.00, 0.05, 0.25),
    "haberdar": (0.20, 0.05, 1.00, 0.10),
    "sosyallesmek": (0.10, 0.30, 0.05, 1.00),
    "dolasmak": (0.40, 0.55, 0.40, 0.45),
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity for non-negative intent/embedding vectors."""
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    dot = sum(float(x) * float(y) for x, y in zip(a, b))
    na = math.sqrt(sum(float(x) ** 2 for x in a))
    nb = math.sqrt(sum(float(y) ** 2 for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def canonical_intent_vector(intent: str | Sequence[float]) -> tuple[float, ...]:
    if isinstance(intent, str):
        if intent not in INTENTS:
            raise ValueError(f"unknown intent: {intent}")
        return INTENTS[intent]
    if len(intent) != 4:
        raise ValueError("intent vector must have four dimensions")
    return tuple(clamp(x) for x in intent)


def classic_score(post: Mapping[str, object]) -> float:
    """Fair baseline retained from the original project."""
    engagement = clamp(float(post.get("etkilesim_puani", 0.0)))
    freshness = clamp(float(post.get("tazelik", 0.0)))
    clickbait = clamp(float(post.get("clickbait", 0.0)))
    spam_filter = 1.0 - clickbait
    return 0.70 * engagement + 0.20 * freshness + 0.10 * spam_filter


def pusula_parts(
    post: Mapping[str, object],
    intent: str | Sequence[float],
) -> dict[str, float]:
    target = canonical_intent_vector(intent)
    post_vector = post.get("tahmin_niyet") or post.get("intent_vector")
    if not isinstance(post_vector, (list, tuple)) or len(post_vector) != 4:
        raise ValueError("post requires a four-dimensional intent vector")

    fit = clamp(cosine(tuple(float(x) for x in post_vector), target))
    freshness = clamp(float(post.get("tazelik", 0.0)))
    engagement = clamp(float(post.get("etkilesim_puani", 0.0)))
    clickbait = clamp(float(post.get("clickbait", 0.0)))
    quality = 1.0 - clickbait

    base = 0.70 * fit + 0.15 * freshness + 0.15 * engagement
    score = base * quality
    return {
        "fit": fit,
        "freshness": freshness,
        "engagement": engagement,
        "clickbait": clickbait,
        "quality": quality,
        "base": base,
        "score": score,
    }


def pusula_score(post: Mapping[str, object], intent: str | Sequence[float]) -> float:
    return pusula_parts(post, intent)["score"]


def rank_by_pusula(
    posts: Iterable[Mapping[str, object]],
    intent: str | Sequence[float],
) -> list[Mapping[str, object]]:
    return sorted(posts, key=lambda post: pusula_score(post, intent), reverse=True)
