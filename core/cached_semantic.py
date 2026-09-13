"""Offline semantic label cache.

Competition/runtime code should not require a live language-model request for
every feed load. Semantic labels are generated in batch, validated, stored,
and then consumed through this adapter.
"""

from __future__ import annotations

import json
from pathlib import Path

from .labeling import LabelResult, text_fingerprint


class CachedSemanticLabeler:
    name = "semantic-cache-v2"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._cache: dict[str, LabelResult] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        for line_no, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            fingerprint = str(row.get("text_sha256") or "")
            if not fingerprint and row.get("text") is not None:
                fingerprint = text_fingerprint(str(row["text"]))
            if not fingerprint:
                raise ValueError(f"missing text fingerprint at line {line_no}")
            result = LabelResult.from_mapping(row)
            self._cache[fingerprint] = result

    def label(self, text: str) -> LabelResult:
        key = text_fingerprint(text)
        if key not in self._cache:
            raise KeyError(f"semantic label not found for text fingerprint {key[:12]}")
        return self._cache[key]
