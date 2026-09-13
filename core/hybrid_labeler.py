"""Confidence-gated hybrid labeler."""

from __future__ import annotations

from .labeling import LabelResult, Labeler


class HybridLabeler:
    name = "hybrid-v2"

    def __init__(self, primary: Labeler, fallback: Labeler, min_confidence: float = 0.65):
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        self.primary = primary
        self.fallback = fallback
        self.min_confidence = min_confidence

    def label(self, text: str) -> LabelResult:
        try:
            result = self.primary.label(text)
        except (KeyError, FileNotFoundError, RuntimeError, ValueError):
            return self.fallback.label(text)

        if result.confidence is None or result.confidence < self.min_confidence:
            return self.fallback.label(text)
        return LabelResult(
            ogretici=result.ogretici,
            eglendirici=result.eglendirici,
            haber=result.haber,
            sosyal=result.sosyal,
            clickbait=result.clickbait,
            method="hybrid-semantic",
            confidence=result.confidence,
            model=result.model,
            prompt_version=result.prompt_version,
            schema_version=result.schema_version,
        )
