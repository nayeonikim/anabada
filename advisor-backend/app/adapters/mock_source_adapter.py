"""Mock SourceAdapter — repository의 Evidence를 Source별로 반환.

MVP mock: 해당 Source에 속한 모든 Evidence를 반환한다(관련도 계산·집계는 C2 담당).
실제 통합 시 이 클래스를 실제 Source API 클라이언트로 교체한다.
"""
from __future__ import annotations

from app.adapters.base import SourceAdapter
from app.domain.models import Evidence, SourceId, StructuredIntent
from app.infra.asset_repository import AssetRepository


class MockSourceAdapter(SourceAdapter):
    def __init__(self, source_id: SourceId, repository: AssetRepository):
        self._source_id = source_id
        self._repository = repository

    @property
    def source_id(self) -> SourceId:
        return self._source_id

    def search(self, intent: StructuredIntent) -> list[Evidence]:
        # mock: 이 Source의 전 Evidence 반환. 관련도/집계는 AssetSearch(C2)에서 수행.
        return [
            ev for ev in self._repository.all_evidence() if ev.source == self._source_id
        ]
