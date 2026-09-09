"""공용 테스트 fixture — repository, registry 등."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.registry import SourceAdapterRegistry
from app.infra.asset_repository import AssetRepository

_DATA = Path(__file__).resolve().parent.parent.parent / "data"


@pytest.fixture
def repository() -> AssetRepository:
    return AssetRepository.load(_DATA / "assets.json", _DATA / "evidence.json")


@pytest.fixture
def registry(repository) -> SourceAdapterRegistry:
    return SourceAdapterRegistry.build_mock(repository)
