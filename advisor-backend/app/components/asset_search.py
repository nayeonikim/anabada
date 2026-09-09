"""C2 AssetSearch — Multi-Source 검색 → asset 단위 Candidate 집계 (US-2.1).

SourceAdapterRegistry의 모든 Adapter를 순회하여 Evidence를 모으고, assetId로 묶어
asset 단위 Candidate를 만든다. relevance는 intent와 asset 텍스트의 토큰 겹침으로 계산.
relevance == 0(무관) 후보는 제외(검색 결과에서 미포함).
"""
from __future__ import annotations

import re

from app.adapters.registry import SourceAdapterRegistry
from app.domain.models import Candidate, Evidence, SourceId, StructuredIntent
from app.infra.asset_repository import AssetRepository

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+|[가-힣]+")


def _tokens(*texts: str) -> set[str]:
    out: set[str] = set()
    for t in texts:
        for m in _TOKEN_RE.findall(t or ""):
            tok = m.lower()
            if len(tok) >= 2:  # 1글자 토큰 잡음 제거
                out.add(tok)
    return out


class AssetSearchComponent:
    def __init__(self, registry: SourceAdapterRegistry, repository: AssetRepository):
        self._registry = registry
        self._repository = repository

    def search(self, intent: StructuredIntent) -> list[Candidate]:
        # 1) 모든 Adapter 순회 → Evidence 수집 → assetId로 그룹
        by_asset: dict[str, list[Evidence]] = {}
        for adapter in self._registry.get_all():
            for ev in adapter.search(intent):
                by_asset.setdefault(ev.asset_id, []).append(ev)

        intent_tokens = _tokens(
            intent.goal, intent.function, intent.data, intent.output
        )

        candidates: list[Candidate] = []
        for asset_id, evidence in by_asset.items():
            asset = self._repository.get_asset(asset_id)
            if asset is None:
                continue
            relevance = self._relevance(intent_tokens, asset)
            if relevance <= 0.0:
                continue  # 무관 자산은 검색 결과에서 제외
            sources = _distinct_sources(evidence)
            candidates.append(
                Candidate(
                    id=asset.id,
                    asset_name=asset.name,
                    type=asset.type,
                    summary=asset.summary,
                    capabilities=list(asset.capabilities),
                    lifecycle_status=asset.lifecycle_status,
                    constraints=list(asset.constraints),
                    evidence=evidence,
                    sources=sources,
                    relevance=relevance,
                )
            )
        return candidates

    @staticmethod
    def _relevance(intent_tokens: set[str], asset) -> float:
        asset_tokens = _tokens(
            asset.name,
            asset.summary,
            " ".join(asset.capabilities),
            " ".join(asset.keywords),
        )
        if not intent_tokens or not asset_tokens:
            return 0.0
        overlap = intent_tokens & asset_tokens
        # 관련도 = intent 토큰 중 매칭 비율(0~1)
        return len(overlap) / len(intent_tokens)


def _distinct_sources(evidence: list[Evidence]) -> list[SourceId]:
    seen: list[SourceId] = []
    for ev in evidence:
        if ev.source not in seen:
            seen.append(ev.source)
    return seen
