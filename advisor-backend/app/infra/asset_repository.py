"""In-memory Asset/Evidence 저장소 (NFR Design §4.2 DI 경계).

`data/assets.json` + `data/evidence.json`을 로드하여 read-only in-memory 보관.
실제 데이터 소스로 교체 가능(인터페이스 경계).
"""
from __future__ import annotations

import json
from pathlib import Path

from app.domain.models import (
    Asset,
    AssetType,
    Evidence,
    LifecycleStatus,
    SourceId,
)


class AssetRepository:
    def __init__(self, assets: list[Asset], evidence: list[Evidence]):
        self._assets = {a.id: a for a in assets}
        self._evidence = list(evidence)
        self._evidence_by_asset: dict[str, list[Evidence]] = {}
        for ev in self._evidence:
            self._evidence_by_asset.setdefault(ev.asset_id, []).append(ev)

    # ── 조회 ──
    def all_assets(self) -> list[Asset]:
        return list(self._assets.values())

    def get_asset(self, asset_id: str) -> Asset | None:
        return self._assets.get(asset_id)

    def evidence_for(self, asset_id: str) -> list[Evidence]:
        return list(self._evidence_by_asset.get(asset_id, []))

    def all_evidence(self) -> list[Evidence]:
        return list(self._evidence)

    # ── 로드 ──
    @staticmethod
    def load(assets_path: Path, evidence_path: Path) -> "AssetRepository":
        assets_raw = json.loads(Path(assets_path).read_text(encoding="utf-8"))
        evidence_raw = json.loads(Path(evidence_path).read_text(encoding="utf-8"))

        assets = [_parse_asset(a) for a in assets_raw]
        evidence = [_parse_evidence(e) for e in evidence_raw]
        return AssetRepository(assets, evidence)


def _parse_asset(d: dict) -> Asset:
    return Asset(
        id=d["id"],
        name=d["name"],
        type=AssetType(d["type"]),
        summary=d.get("summary", ""),
        capabilities=list(d.get("capabilities", [])),
        lifecycle_status=LifecycleStatus(d.get("lifecycleStatus", "unknown")),
        constraints=list(d.get("constraints", [])),
        keywords=list(d.get("keywords", [])),
        evidence_refs=list(d.get("evidenceRefs", [])),
        allowed_roles=list(d.get("allowedRoles", [])),
        allowed_users=list(d.get("allowedUsers", [])),
    )


def _parse_evidence(d: dict) -> Evidence:
    return Evidence(
        id=d["id"],
        asset_id=d["assetId"],
        source=SourceId(d["source"]),
        evidence_type=d.get("evidenceType", ""),
        title=d.get("title", ""),
        summary=d.get("summary", ""),
        source_ref=d.get("sourceRef", ""),
        last_updated=d.get("lastUpdated"),
    )
