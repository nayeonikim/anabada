"""SourceAdapter 인터페이스 (NFR Design §4.1 Adapter Pattern).

각 Adapter는 하나의 Source를 담당하며 intent에 대한 Evidence[]를 반환한다.
신규 Source는 이 인터페이스 구현 + registry 등록만으로 통합(코어 무변경, NFR-S2/NFR-3).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import Evidence, SourceId, StructuredIntent


class SourceAdapter(ABC):
    @property
    @abstractmethod
    def source_id(self) -> SourceId:
        ...

    @abstractmethod
    def search(self, intent: StructuredIntent) -> list[Evidence]:
        """intent 관련 Evidence를 이 Source에서 검색하여 반환."""
        ...
