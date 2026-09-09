"""C3 PermissionFilter — per-asset 권한 필터 (US-2.2 / FR-8 / NFR-4 / §3.1).

per-asset 판정: role ∈ allowedRoles OR userId ∈ allowedUsers (BR-PERMISSION).
파이프라인 초기 단일 스테이지. 미인가 후보는 ExcludedCandidate(내부 전용)로 분리하고
감사 로그에만 기록(공개 응답 미노출).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import (
    Candidate,
    ExcludedCandidate,
    ExclusionReason,
    PermissionContext,
)
from app.infra.asset_repository import AssetRepository
from app.logging_setup import audit


@dataclass
class FilterResult:
    accessible: list[Candidate]
    excluded: list[ExcludedCandidate]  # ⚠️ 서버 내부 전용


class PermissionFilterComponent:
    def __init__(self, repository: AssetRepository):
        self._repository = repository

    def filter(
        self, candidates: list[Candidate], ctx: PermissionContext, request_id: str = ""
    ) -> FilterResult:
        accessible: list[Candidate] = []
        excluded: list[ExcludedCandidate] = []
        for cand in candidates:
            if self._is_accessible(cand.id, ctx):
                accessible.append(cand)
            else:
                excluded.append(
                    ExcludedCandidate(
                        candidate=cand,
                        reason=ExclusionReason.NOT_ACCESSIBLE,
                        evidence_ref="permission: role/user not permitted",
                    )
                )
        if excluded:
            # 서버 내부 감사 로그만 (공개 응답 미노출, §3.4)
            audit(
                "permission_excluded",
                requestId=request_id,
                userId=ctx.user_id,
                role=ctx.role,
                excludedAssetIds=[e.candidate.id for e in excluded],
            )
        return FilterResult(accessible=accessible, excluded=excluded)

    def _is_accessible(self, asset_id: str, ctx: PermissionContext) -> bool:
        asset = self._repository.get_asset(asset_id)
        if asset is None:
            return False
        # 권한 확장 금지: 규칙에 명시된 접근만 허용
        return ctx.role in asset.allowed_roles or ctx.user_id in asset.allowed_users
