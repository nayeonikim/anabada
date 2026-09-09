"""C5 ReVerification — LLM 재검증 → evaluationStatus 계약 (US-3.1, §1.3/§1.4/§7.1).

- 후보별 LLM 호출 성공 → COMPLETED VerifiedCandidate(score/근거/충분성).
- 후보별 기술 실패 → UNAVAILABLE(score=null, technicalFailureReason 내부 전용).
- 대상 ≥1인데 전부 실패 → ReverificationUnavailableError(§1.6, 502).
- demoMode 미매칭(DemoFixtureNotFoundError)은 그대로 전파(422).
"""
from __future__ import annotations

from app.domain.errors import (
    DemoFixtureNotFoundError,
    ReverificationUnavailableError,
)
from app.domain.models import (
    Candidate,
    EvaluationStatus,
    StructuredIntent,
    VerifiedCandidate,
)
from app.infra.llm_client import LLMClient
from app.logging_setup import audit


class ReVerificationComponent:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    def reverify(
        self,
        top_n: list[Candidate],
        intent: StructuredIntent,
        request_id: str = "",
    ) -> list[VerifiedCandidate]:
        if not top_n:
            return []

        verified: list[VerifiedCandidate] = []
        for cand in top_n:
            try:
                outcome = self._llm.reverify(intent, cand)
                verified.append(
                    VerifiedCandidate.completed(
                        candidate=cand,
                        reusability_score=outcome.reusability_score,
                        reasoning=outcome.reasoning,
                        role_task_context_note=outcome.role_task_context_note,
                        evidence_sufficient=outcome.evidence_sufficient,
                        insufficiency_reason=outcome.insufficiency_reason,
                    )
                )
            except DemoFixtureNotFoundError:
                # 데모 설정 오류는 은폐하지 않고 전파(§1.2)
                raise
            except Exception as e:  # noqa: BLE001 - 기술 실패 → UNAVAILABLE 강등
                # 내부 사유는 서버 로그에만, 공개 미노출(§1.4)
                audit(
                    "reverify_candidate_failed",
                    requestId=request_id,
                    candidateId=cand.id,
                    reason=str(e),
                )
                verified.append(
                    VerifiedCandidate.unavailable(cand, technical_failure_reason=str(e))
                )

        # 전체 실패(대상 ≥1 && 전부 UNAVAILABLE) → 공통 오류(§1.6)
        if all(
            vc.evaluation_status == EvaluationStatus.UNAVAILABLE for vc in verified
        ):
            audit(
                "reverify_all_failed",
                requestId=request_id,
                candidateIds=[vc.candidate.id for vc in verified],
            )
            raise ReverificationUnavailableError("전체 후보 재검증 실패")

        return verified
