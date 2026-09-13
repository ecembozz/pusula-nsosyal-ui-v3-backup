"""Common labeling contract for PUSULA Semantic V2.

The ranking layer must not care whether a label came from the legacy
heuristic, a language model, an embedding classifier, or a hybrid. Every
labeler returns the same validated four-dimensional representation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Mapping, Protocol, Sequence

INTENT_DIMENSIONS = ("ogretici", "eglendirici", "haber", "sosyal")
SCHEMA_VERSION = "pusula-label-v2"


def _unit(value: float, name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {number}")
    return number


@dataclass(frozen=True)
class LabelResult:
    ogretici: float
    eglendirici: float
    haber: float
    sosyal: float
    clickbait: float
    method: str
    confidence: float | None = None
    model: str | None = None
    prompt_version: str | None = None
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (*INTENT_DIMENSIONS, "clickbait"):
            object.__setattr__(self, name, _unit(getattr(self, name), name))
        if self.confidence is not None:
            object.__setattr__(self, "confidence", _unit(self.confidence, "confidence"))
        if not self.method.strip():
            raise ValueError("method cannot be empty")

    @property
    def intent_vector(self) -> tuple[float, float, float, float]:
        return (self.ogretici, self.eglendirici, self.haber, self.sosyal)

    @property
    def dominant_intent(self) -> str:
        index = max(range(4), key=lambda i: self.intent_vector[i])
        return INTENT_DIMENSIONS[index]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["intent_vector"] = list(self.intent_vector)
        payload["dominant_intent"] = self.dominant_intent
        return payload

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "LabelResult":
        intent = payload.get("intent")
        if isinstance(intent, Mapping):
            dims = {name: intent[name] for name in INTENT_DIMENSIONS}
        else:
            vector = payload.get("intent_vector")
            if not isinstance(vector, Sequence) or isinstance(vector, (str, bytes)) or len(vector) != 4:
                raise ValueError("payload requires intent mapping or four-value intent_vector")
            dims = dict(zip(INTENT_DIMENSIONS, vector))
        return cls(
            ogretici=float(dims["ogretici"]),
            eglendirici=float(dims["eglendirici"]),
            haber=float(dims["haber"]),
            sosyal=float(dims["sosyal"]),
            clickbait=float(payload.get("clickbait", 0.0)),
            method=str(payload.get("method", "semantic")),
            confidence=(None if payload.get("confidence") is None else float(payload["confidence"])),
            model=(None if payload.get("model") is None else str(payload["model"])),
            prompt_version=(None if payload.get("prompt_version") is None else str(payload["prompt_version"])),
            schema_version=str(payload.get("schema_version", SCHEMA_VERSION)),
        )


class Labeler(Protocol):
    name: str

    def label(self, text: str) -> LabelResult:
        ...


def text_fingerprint(text: str) -> str:
    normalized = " ".join(str(text).strip().split())
    return sha256(normalized.encode("utf-8")).hexdigest()
