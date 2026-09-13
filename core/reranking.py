"""Transparent reranking utilities for PUSULA Semantic V2.

Ideas are intentionally small and explainable:
- remove already-seen posts,
- decay repeated authors,
- use MMR-style semantic diversity when embeddings are available.

This is inspired by public feed-ranking design patterns (including X's open
source author-diversity and reranking layers), but implemented independently
for PUSULA's intent-first objective.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from .ranking import cosine, pusula_parts


def filter_seen(
    posts: Iterable[Mapping[str, object]],
    seen_ids: set[object] | frozenset[object] | None,
) -> list[Mapping[str, object]]:
    if not seen_ids:
        return list(posts)
    return [post for post in posts if post.get("id") not in seen_ids]


def author_factor(prior_count: int, decay: float = 0.5, floor: float = 0.25) -> float:
    """First post=1.0, later posts decay to a configurable floor."""
    if prior_count <= 0:
        return 1.0
    return max(float(floor), float(decay) ** prior_count)


def _embedding(post: Mapping[str, object]) -> Sequence[float] | None:
    value = post.get("embedding")
    if isinstance(value, (list, tuple)) and value:
        return tuple(float(x) for x in value)
    return None


def max_similarity_to_selected(
    post: Mapping[str, object],
    selected: Sequence[Mapping[str, object]],
) -> float:
    candidate = _embedding(post)
    if candidate is None or not selected:
        return 0.0
    sims: list[float] = []
    for other in selected:
        emb = _embedding(other)
        if emb is None or len(emb) != len(candidate):
            continue
        sims.append(cosine(candidate, emb))
    return max(sims, default=0.0)


def rerank_feed(
    posts: Iterable[Mapping[str, object]],
    intent: str | Sequence[float],
    *,
    limit: int = 20,
    seen_ids: set[object] | frozenset[object] | None = None,
    author_decay: float = 0.5,
    author_floor: float = 0.25,
    mmr_alpha: float = 0.82,
) -> list[dict[str, object]]:
    """Greedy, deterministic PUSULA reranker with diagnostics.

    `mmr_alpha=1` disables semantic-diversity penalty while keeping author
    diversity. Missing embeddings also fall back cleanly to relevance only.
    """
    if limit < 1:
        return []
    if not 0.0 <= mmr_alpha <= 1.0:
        raise ValueError("mmr_alpha must be in [0, 1]")

    remaining = [dict(post) for post in filter_seen(posts, seen_ids)]
    selected: list[dict[str, object]] = []
    author_counts: defaultdict[str, int] = defaultdict(int)

    while remaining and len(selected) < limit:
        best_index = -1
        best_value = float("-inf")
        best_diag: dict[str, float] | None = None

        for index, post in enumerate(remaining):
            parts = pusula_parts(post, intent)
            author = str(post.get("author_id") or post.get("yazar") or "unknown")
            a_factor = author_factor(
                author_counts[author],
                decay=author_decay,
                floor=author_floor,
            )
            relevance_after_author = parts["score"] * a_factor
            similarity = max_similarity_to_selected(post, selected)
            mmr_value = (
                mmr_alpha * relevance_after_author
                - (1.0 - mmr_alpha) * similarity
            )

            # Stable tie break: earlier input wins when values are equal.
            if mmr_value > best_value:
                best_index = index
                best_value = mmr_value
                best_diag = {
                    **parts,
                    "author_factor": a_factor,
                    "semantic_similarity_penalty": similarity,
                    "rerank_score": mmr_value,
                }

        chosen = remaining.pop(best_index)
        author = str(chosen.get("author_id") or chosen.get("yazar") or "unknown")
        author_counts[author] += 1
        chosen["_ranking"] = {
            **(best_diag or {}),
            "final_rank": len(selected) + 1,
        }
        selected.append(chosen)

    return selected
