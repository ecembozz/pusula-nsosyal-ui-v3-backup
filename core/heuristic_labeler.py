"""Adapter around the pinned V1 heuristic labeler.

We intentionally do not copy/paste or silently tune the old dictionary here.
The adapter loads the exact upstream snapshot so benchmark results remain a
fair comparison against the original baseline.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from .labeling import LabelResult

LEGACY_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "upstream_snapshot"
    / "kod"
    / "niyet_etiketle.py"
)

_LEGACY: ModuleType | None = None


def _legacy_module() -> ModuleType:
    global _LEGACY
    if _LEGACY is not None:
        return _LEGACY
    if not LEGACY_PATH.exists():
        raise RuntimeError(f"Pinned heuristic snapshot not found: {LEGACY_PATH}")
    spec = importlib.util.spec_from_file_location("pusula_v1_heuristic", LEGACY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load pinned heuristic module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _LEGACY = module
    return module


class HeuristicLabeler:
    name = "heuristic-v1-pinned"

    def label(self, text: str) -> LabelResult:
        module = _legacy_module()
        vector = module.sezgisel_tahmin(text)
        clickbait = module.clickbait_puani(text)
        return LabelResult(
            ogretici=float(vector[0]),
            eglendirici=float(vector[1]),
            haber=float(vector[2]),
            sosyal=float(vector[3]),
            clickbait=float(clickbait),
            method="heuristic",
            confidence=None,
            model=self.name,
        )
