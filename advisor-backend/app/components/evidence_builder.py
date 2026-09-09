"""C7 EvidenceBuilder — 접근 가능 Evidence → EvidenceChain (US-4.2 / BR-EVIDENCE).

- evidenceItems는 후보 Asset의 실제 Evidence 레코드에서 투영(다중 Source).
- stateRationale:
    · COMPLETED NEEDS_REVIEW → insufficiencyReason
    · UNAVAILABLE → 일반적 '평가 미완료'만(내부 technicalFailureReason 비노출, §1.4)
    · REUSE/EXTEND → reasoning 요약
"""
from __future__ import annotations

from app.domain.models import (
    CandidateState,
    EvaluationStatus,
    EvidenceChain,
    EvidenceItem,
    VerifiedCandidate,
)

_UNAVAILABLE_RATIONALE = "재검증을 완료하지 못했습니다. 평가 미완료 상태입니다."


class EvidenceBuilderComponent:
    def build(
        self,
        verified: list[VerifiedCandidate],
        states: dict[str, CandidateState],
    ) -> list[EvidenceChain]:
        chains: list[EvidenceChain] = []
        for vc in verified:
            cand = vc.candidate
            items = [
                EvidenceItem(
                    source=ev.source,
                    evidence_type=ev.evidence_type,
                    title=ev.title,
                    source_ref=ev.source_ref,
                )
                for ev in cand.evidence
            ]
            chains.append(
                EvidenceChain(
                    candidate_id=cand.id,
                    evidence_items=items,
                    state_rationale=self._rationale(vc, states.get(cand.id)),
                )
            )
        return chains

    @staticmethod
    def _rationale(
        vc: VerifiedCandidate, state: CandidateState | None
    ) -> str:
        if vc.evaluation_status == EvaluationStatus.UNAVAILABLE:
            return _UNAVAILABLE_RATIONALE
        if state == CandidateState.NEEDS_REVIEW and vc.insufficiency_reason:
            return vc.insufficiency_reason
        return vc.reasoning or ""
