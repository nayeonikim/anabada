"""C6 DecisionClassifier — 순수·결정적 로직 (business-rules BR-STATE/BR-OVERALL/BR-RANK).

NFR Design §7.3/§7.4 정제 반영:
- classify_candidate: UNAVAILABLE ⇒ 항상 NEEDS_REVIEW. COMPLETED만 Score/evidenceSufficient 판정.
- derive_overall: 기술 실패(UNAVAILABLE)↛DEVELOP. UNAVAILABLE 존재 ∧ COMPLETED REUSE/EXTEND 0 ⇒ NEEDS_REVIEW.
- rank_candidates: COMPLETED(State→Score→name) 먼저, UNAVAILABLE(name→candidateId) 뒤(점수 비교 제외).

부작용 없음 → Hypothesis PBT(P1~P11) 대상.
"""
from __future__ import annotations

from app.domain.models import (
    CandidateState,
    ClassificationConfig,
    EvaluationStatus,
    OverallDecision,
    VerifiedCandidate,
)

# State 우선순위(오름차순 = 상위). BR-RANK/동점 처리에 사용.
_STATE_PRIORITY = {
    CandidateState.REUSE: 0,
    CandidateState.EXTEND_EXISTING: 1,
    CandidateState.NEEDS_REVIEW: 2,
}

_DEFAULT_REUSE = 0.75
_DEFAULT_EXTEND = 0.50


def _effective_thresholds(config: ClassificationConfig) -> tuple[float, float]:
    """제약 `0 < extend <= reuse <= 1` 위반 시 기본값 폴백(P9)."""
    reuse, extend = config.reuse_threshold, config.extend_threshold
    if 0 < extend <= reuse <= 1:
        return reuse, extend
    return _DEFAULT_REUSE, _DEFAULT_EXTEND


def classify_candidate(
    vc: VerifiedCandidate, config: ClassificationConfig
) -> CandidateState:
    """후보 단위 State 판정 (BR-STATE). 반환은 항상 {REUSE, EXTEND_EXISTING, NEEDS_REVIEW}."""
    # P1: 기술 실패(UNAVAILABLE, score=null)는 항상 NEEDS_REVIEW
    if vc.evaluation_status == EvaluationStatus.UNAVAILABLE:
        return CandidateState.NEEDS_REVIEW

    # 이하 COMPLETED 후보에만 적용
    if not vc.evidence_sufficient:
        return CandidateState.NEEDS_REVIEW

    reuse_t, extend_t = _effective_thresholds(config)
    score = vc.reusability_score if vc.reusability_score is not None else 0.0
    if score >= reuse_t:
        return CandidateState.REUSE
    if score >= extend_t:
        return CandidateState.EXTEND_EXISTING
    return CandidateState.NEEDS_REVIEW


def classify_all(
    verified: list[VerifiedCandidate], config: ClassificationConfig
) -> dict[str, CandidateState]:
    """P7: 결과 크기 = 입력 후보 수(누락/중복 없음)."""
    return {vc.candidate.id: classify_candidate(vc, config) for vc in verified}


def _best_completed(
    completed: list[VerifiedCandidate], states: dict[str, CandidateState]
) -> VerifiedCandidate:
    """최고 score COMPLETED 후보(동점 시 State 우선순위 → assetName)."""
    def key(vc: VerifiedCandidate):
        score = vc.reusability_score if vc.reusability_score is not None else 0.0
        return (
            -score,
            _STATE_PRIORITY[states[vc.candidate.id]],
            vc.candidate.asset_name,
        )

    return sorted(completed, key=key)[0]


def derive_overall(
    verified: list[VerifiedCandidate],
    states: dict[str, CandidateState],
    has_any_accessible: bool,
) -> OverallDecision:
    """요청 단위 권고 산출 (BR-OVERALL, §7.3)."""
    # 진짜 '적합 자산 없음': 접근 가능 0 또는 검색 0
    if not has_any_accessible or not verified:
        return OverallDecision.DEVELOP

    completed = [
        vc for vc in verified if vc.evaluation_status == EvaluationStatus.COMPLETED
    ]
    completed_reuse_extend = [
        vc
        for vc in completed
        if states[vc.candidate.id]
        in (CandidateState.REUSE, CandidateState.EXTEND_EXISTING)
    ]

    if completed_reuse_extend:
        # COMPLETED 후보만으로 기존 규칙: 최고 score COMPLETED 후보의 State 채택
        best = _best_completed(completed, states)
        return OverallDecision(states[best.candidate.id].value)

    # COMPLETED 중 REUSE/EXTEND 없음
    has_unavailable = any(
        vc.evaluation_status == EvaluationStatus.UNAVAILABLE for vc in verified
    )
    if has_unavailable:
        # P5/P10: 아직 평가 못한 후보 존재 → DEVELOP 금지
        return OverallDecision.NEEDS_REVIEW
    # 전 후보 COMPLETED ∧ REUSE/EXTEND 0 → DEVELOP
    return OverallDecision.DEVELOP


def rank_candidates(
    verified: list[VerifiedCandidate], states: dict[str, CandidateState]
) -> list[VerifiedCandidate]:
    """BR-RANK 2계층 정렬 (§7.3). 입력의 순열, 결정적(P8)."""
    completed = [
        vc for vc in verified if vc.evaluation_status == EvaluationStatus.COMPLETED
    ]
    unavailable = [
        vc for vc in verified if vc.evaluation_status == EvaluationStatus.UNAVAILABLE
    ]

    def completed_key(vc: VerifiedCandidate):
        score = vc.reusability_score if vc.reusability_score is not None else 0.0
        return (
            _STATE_PRIORITY[states[vc.candidate.id]],  # State 오름차순
            -score,                                     # Score 내림차순
            vc.candidate.asset_name,                    # name 사전순
        )

    def unavailable_key(vc: VerifiedCandidate):
        return (vc.candidate.asset_name, vc.candidate.id)

    completed.sort(key=completed_key)
    unavailable.sort(key=unavailable_key)
    return completed + unavailable
