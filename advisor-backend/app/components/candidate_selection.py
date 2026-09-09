"""C4 CandidateSelection — 접근 가능 후보 relevance 내림차순 Top-N (US-2.2 / BR-TOPN).

접근 가능 후보 0개 → 빈 리스트(DEVELOP 경로는 상위 orchestrator/BR-OVERALL에서 판정).
"""
from __future__ import annotations

from app.domain.models import Candidate


class CandidateSelectionComponent:
    def select_top_n(self, accessible: list[Candidate], top_n: int) -> list[Candidate]:
        if not accessible:
            return []
        # relevance 내림차순, 동점 시 결정성 위해 asset_name→id
        ordered = sorted(
            accessible,
            key=lambda c: (-c.relevance, c.asset_name, c.id),
        )
        return ordered[: max(top_n, 0)]
