"""Explainable presentation-level clickbait scorer for PUSULA.

This module deliberately keeps clickbait separate from semantic intent.
It scores manipulative presentation cues (curiosity gaps, urgency/exclusivity,
overpromising, shouting/punctuation) and returns both a 0..1 score and reasons.

Important evaluation note:
The weights/patterns below were selected during development using
`data/dev_labels/v4_clickbait_pairs_24.jsonl`. They are now frozen before the
separate stress test and are not final human-gold evidence.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


PHRASE_WEIGHTS: tuple[tuple[str, float], ...] = (
    ("şok", 0.42),
    ("inanamayacaks", 0.50),
    ("kimsenin söylemediği", 0.55),
    ("gerçek ortaya çıktı", 0.48),
    ("dikkat", 0.34),
    ("herkes yanılıyor", 0.48),
    ("asıl sebep", 0.38),
    ("yapanlar dikkat", 0.52),
    ("bunu görmeden", 0.48),
    ("çoğu kişi bunu bilmiyor", 0.52),
    ("son şans", 0.52),
    ("son fırsat", 0.52),
    ("sakın", 0.42),
    ("tek bir ayrıntı", 0.34),
    ("tek bir değişiklik", 0.34),
    ("her şeyi değiştirdi", 0.36),
    ("hayatını değiştirecek", 0.55),
    ("sadece gerçek", 0.44),
    ("reklamlarda göstermedikleri", 0.52),
    ("interneti ikiye böldü", 0.46),
    ("kaçırırsan", 0.34),
    ("çok şey kaybeder", 0.38),
    ("şaşıracaks", 0.38),
    ("sonuç beklediğim gibi değildi", 0.30),
    ("gözden kaçırdığı", 0.30),
    ("tamamen değiştirebilir", 0.30),
    ("sebebi düşündüğünüz şey değil", 0.38),
    ("kritik ayrıntı sonda", 0.40),
    ("tahmin etmek zor", 0.22),
    ("asıl farkı yaratan", 0.24),
    ("sonunda buldum", 0.22),
)

AMPLIFIER_EMOJI = re.compile(r"[😱😳👀🔥⏰👇]")
CAPS_TOKEN = re.compile(r"\b[A-ZÇĞİÖŞÜ]{4,}\b")


@dataclass(frozen=True)
class ClickbaitResult:
    score: float
    reasons: tuple[str, ...]
    phrase_score: float
    caps_score: float
    punctuation_score: float
    emoji_score: float


def _normalize(text: str) -> str:
    text = text.replace("İ", "i").replace("I", "ı").casefold()
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


def analyze_clickbait(text: str) -> ClickbaitResult:
    text = str(text or "")
    norm = _normalize(text)
    reasons: list[str] = []

    phrase_score = 0.0
    for phrase, weight in PHRASE_WEIGHTS:
        if phrase in norm:
            phrase_score += weight
            reasons.append(f"phrase:{phrase}")

    caps = CAPS_TOKEN.findall(text)
    caps_score = min(0.30, 0.10 * len(caps))
    if caps_score:
        reasons.append(f"caps:{len(caps)}")

    punctuation_score = min(0.20, 0.07 * text.count("!"))
    if "!!!" in text or "???" in text:
        punctuation_score += 0.08
    punctuation_score = min(0.28, punctuation_score)
    if punctuation_score:
        reasons.append(f"punctuation:{text.count('!')}")

    subtotal = phrase_score + caps_score + punctuation_score
    emoji_score = 0.08 if subtotal >= 0.20 and AMPLIFIER_EMOJI.search(text) else 0.0
    if emoji_score:
        reasons.append("amplifier_emoji")

    score = min(1.0, subtotal + emoji_score)
    return ClickbaitResult(
        score=float(score),
        reasons=tuple(reasons),
        phrase_score=float(phrase_score),
        caps_score=float(caps_score),
        punctuation_score=float(punctuation_score),
        emoji_score=float(emoji_score),
    )


def score_clickbait(text: str) -> float:
    return analyze_clickbait(text).score
