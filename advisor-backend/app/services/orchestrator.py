"""S1 AdvisorOrchestratorService — 동기 순차 오케스트레이션 (business-logic-model §2~§4).

3개 논리 엔드포인트를 담당:
- submit_intent(rawText)      → StructuredIntent | ClarificationRequest (C1)
- advise(intent, ctx)         → AdviceResult (C2~C7 + 조립)
- submit_feedback(...)        → 확인 id (C8)

실패 매트릭스(§1.3):
- C1 실패/타임아웃 → 오류 전파(폴백 없음)
- C5 일부 실패    → 후보 UNAVAILABLE 강등(정상 응답 포함)
- C5 전체 실패    → ReverificationUnavailableError(공통 오류)

조립(§3.7): BR-RANK 정렬 + rank 부여 + capabilityMatch, excluded는 내부 감사만.
"""
from __future__ import annotations

import uuid
from typing import Union

from app.components.asset_search import AssetSearchComponent
from app.components.candidate_selection import CandidateSelectionComponent
from app.components.decision_classifier import (
    classify_all,
    derive_overall,
    rank_candidates,
)
from app.components.evidence_builder import EvidenceBuilderComponent
from app.components.feedback import FeedbackComponent
from app.components.permission_filter import PermissionFilterComponent
from app.components.reverification import ReVerificationComponent
from app.components.structure import IntentStructuringComponent
from app.domain.models import (
    AdviceResult,
    CandidateState,
    ClarificationRequest,
    ClassificationConfig,
    EvaluationStatus,
    FeedbackVerdict,
    OverallDecision,
    PermissionContext,
    RankedCandidate,
    StructuredIntent,
    VerifiedCandidate,
)
from app.logging_setup import audit

IntentResult = Union[StructuredIntent, ClarificationRequest]

_OVERALL_RATIONALE = {
    OverallDecision.REUSE: "기존 자산을 그대로 재사용하도록 권고합니다.",
    OverallDecision.EXTEND_EXISTING: "기존 자산을 확장/보완하여 활용하도록 권고합니다.",
    OverallDecision.NEEDS_REVIEW: "추가 검토가 필요합니다. 근거가 충분하지 않거나 평가를 완료하지 못한 후보가 있습니다.",
    OverallDecision.DEVELOP: "적합한 재사용 자산을 찾지 못했습니다. 신규 개발을 권고합니다.",
}


class AdvisorOrchestratorService:
    def __init__(
        self,
        structuring: IntentStructuringComponent,
        search: AssetSearchComponent,
        permission_filter: PermissionFilterComponent,
        selection: CandidateSelectionComponent,
        reverification: ReVerificationComponent,
        evidence_builder: EvidenceBuilderComponent,
        feedback: FeedbackComponent,
        config: ClassificationConfig,
    ):
        self._structuring = structuring
        self._search = search
        self._permission_filter = permission_filter
        self._selection = selection
        self._reverification = reverification
        self._evidence_builder = evidence_builder
        self._feedback = feedback
        self._config = config

    # ── C1: submitIntent (§2) ────────────────────────────────────
    def submit_intent(self, raw_text: str, request_id: str = "") -> IntentResult:
        """5필드 구조화 → 누락 있으면 ClarificationRequest, 없으면 StructuredIntent."""
        intent = self._structuring.structure(raw_text)  # 실패는 예외 전파(§1.3)
        missing = IntentStructuringComponent.detect_missing_fields(intent)
        if missing:
            audit("intent_clarification", requestId=request_id, missing=missing)
            return IntentStructuringComponent.build_clarification(missing)
        return intent

    # ── advise (§3) ──────────────────────────────────────────────
    def advise(
        self,
        intent: StructuredIntent,
        ctx: PermissionContext,
        request_id: str = "",
    ) -> AdviceResult:
        # 1) Multi-Source 검색
        all_candidates = self._search.search(intent)

        # 2) per-asset 권한 필터 (excluded는 내부 감사만)
        filtered = self._permission_filter.filter(all_candidates, ctx, request_id)
        has_any_accessible = bool(filtered.accessible)

        # 3) Top-N 선별 (접근 가능 0 → 빈 리스트 → DEVELOP 경로)
        top_n = self._selection.select_top_n(filtered.accessible, self._config.top_n)

        # 4) LLM 재검증 (전체 실패는 예외 전파; 일부 실패는 UNAVAILABLE 강등)
        verified = self._reverification.reverify(top_n, intent, request_id)

        # 5) 순수 분류 + 요청 단위 권고 (§7.3)
        states = classify_all(verified, self._config)
        overall = derive_overall(verified, states, has_any_accessible)

        # 6) Evidence Chain (UNAVAILABLE은 '평가 미완료'만)
        evidence_chains = self._evidence_builder.build(verified, states)

        # 7) 조립: BR-RANK 정렬 + rank + capabilityMatch
        ranked_source = rank_candidates(verified, states)
        ranking = [
            self._to_ranked(vc, states[vc.candidate.id], idx + 1)
            for idx, vc in enumerate(ranked_source)
        ]

        result_id = uuid.uuid4().hex
        audit(
            "advise_completed",
            requestId=request_id,
            resultId=result_id,
            overall=overall.value,
            rankedCount=len(ranking),
            excludedCount=len(filtered.excluded),  # 내부 감사만
        )
        return AdviceResult(
            result_id=result_id,
            ranking=ranking,
            overall_decision=overall,
            overall_rationale=_OVERALL_RATIONALE[overall],
            evidence_chains=evidence_chains,
            is_recommendation=True,
        )

    # ── C8: submitFeedback (§4) ──────────────────────────────────
    def submit_feedback(
        self, result_id: str, candidate_id: str, verdict: FeedbackVerdict
    ) -> str:
        return self._feedback.record(result_id, candidate_id, verdict)

    # ── 내부 조립 헬퍼 ────────────────────────────────────────────
    @staticmethod
    def _to_ranked(
        vc: VerifiedCandidate, state: CandidateState, rank: int
    ) -> RankedCandidate:
        cand = vc.candidate
        return RankedCandidate(
            candidate_id=cand.id,
            sources=list(cand.sources),
            asset_name=cand.asset_name,
            lifecycle_status=cand.lifecycle_status,
            evaluation_status=vc.evaluation_status,
            reusability_score=vc.reusability_score,
            candidate_state=state,
            capability_match=_capability_match(vc),
            rank=rank,
        )


def _capability_match(vc: VerifiedCandidate) -> str:
    """intent.function 대비 적합 서술 요약(공개 가능; 내부 기술사유 미포함)."""
    if vc.evaluation_status == EvaluationStatus.UNAVAILABLE:
        return "평가 미완료"
    return vc.reasoning or ""
