"""SourceAdapterRegistry — config-driven adapter 목록 (NFR Design §4.1).

config에 선언된 Source 목록을 기준으로 adapter를 로드/보관한다.
코어(AssetSearch)는 registry.get_all()에만 의존한다.
"""
from __future__ import annotations

from app.adapters.base import SourceAdapter
from app.adapters.mock_source_adapter import MockSourceAdapter
from app.domain.models import SourceId
from app.infra.asset_repository import AssetRepository


class SourceAdapterRegistry:
    def __init__(self, adapters: list[SourceAdapter]):
        self._adapters = list(adapters)

    def get_all(self) -> list[SourceAdapter]:
        return list(self._adapters)

    @staticmethod
    def build_mock(
        repository: AssetRepository, sources: list[SourceId] | None = None
    ) -> "SourceAdapterRegistry":
        """mock adapter registry. sources 미지정 시 전 SourceId 등록(config-driven 확장 지점)."""
        source_list = sources if sources is not None else list(SourceId)
        adapters: list[SourceAdapter] = [
            MockSourceAdapter(src, repository) for src in source_list
        ]
        return SourceAdapterRegistry(adapters)
