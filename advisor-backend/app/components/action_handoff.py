"""C11 ActionHandoffComponent — Evidence-grounded Action Prompt 생성 (CR-001).

NFR Design D3 = **하이브리드**:
- (a) 구조·선택 (순수·결정적, LLM 미사용): Decision→목적 매핑, 대상 Asset 선택
  (ranking[0]), §3.1 '평가 미완료' 문구 게이팅, grounding 페이로드 조립(접근 가능
  ranking/evidenceChains 공개 투영만). → PBT 대상(INV-HANDOFF-1/2/5).
- (b) 자연어 본문 (LLM): grounding-only 페이로드로 promptText 생성(LLMClient/Fixture).

grounding-only(NFR-8/INV-HANDOFF-3): 입력이 이미 공개 투영이라 미인가 자산·
technicalFailureReason·제외 개수/플래그가 구조적으로 유입 불가.

비차단(BR-HANDOFF-FAIL/INV-HANDOFF-4): 생성 실패(정합 가드 위반·LLM 오류/타임아웃)는
**예외**로 신호하며, orchestrator가 이를 잡아 actionPrompt=None 으로 처리(핵심 결과 정상).
"""
from __future__ import annotations

from app.domain.models import (
    ActionPrompt,
    EvaluationStatus,
    EvidenceChain,
    OverallDecision,
    RankedCandidate,
    StructuredIntent,
)
from app.infra.llm_client import ActionPromptRequest, LLMClient

_REUSE_EXTEND = (OverallDecision.REUSE, OverallDecision.EXTEND_EXISTING)


# ── (a) 순수 구조/선택 로직 (부작용 없음 → PBT 대상) ──────────────────
def select_target_asset_names(
    overall: OverallDecision, ranking: list[RankedCandidate]
) -> list[str]:
    """대상 Asset 선택 규칙(§2.2, INV-HANDOFF-2).

    - REUSE/EXTEND_EXISTING → [ranking[0].asset_name] (driving candidate).
      접근 가능 대상을 식별할 수 없으면(ranking 비어있음) 정합 가드 위반 → ValueError.
    - DEVELOP/NEEDS_REVIEW → [].
    ranking 은 접근 가능 후보만 포함하므로 대상 Asset명은 노출 가능.
    """
    if overall in _REUSE_EXTEND:
        if not ranking:
            raise ValueError(
                f"{overall.value}인데 접근 가능한 대상 후보를 식별할 수 없음(정합 가드 위반)"
            )
        return [ranking[0].asset_name]
    return []


def should_note_unavailable(
    overall: OverallDecision, ranking: list[RankedCandidate]
) -> bool:
    """§3.1 '평가 미완료' 일반 문구 허용 여부(INV-HANDOFF-5).

    NEEDS_REVIEW 이면서 ranking 에 UNAVAILABLE 후보가 존재할 때만 True.
    (technicalFailureReason·후보 식별정보는 배제 — evaluationStatus 로만 판정)
    """
    return overall == OverallDecision.NEEDS_REVIEW and any(
        r.evaluation_status == EvaluationStatus.UNAVAILABLE for r in ranking
    )


def _evidence_lines(
    overall: OverallDecision,
    ranking: list[RankedCandidate],
    evidence_chains: list[EvidenceChain],
) -> list[str]:
    """grounding 근거 라인(공개 투영만). "[Source/type] title" 포맷."""
    def fmt(chain: EvidenceChain) -> list[str]:
        return [
            f"[{it.source.value}/{it.evidence_type}] {it.title}"
            for it in chain.evidence_items
        ]

    if overall in _REUSE_EXTEND and ranking:
        target_id = ranking[0].candidate_id
        chain = next(
            (c for c in evidence_chains if c.candidate_id == target_id), None
        )
        return fmt(chain) if chain is not None else []
    if overall == OverallDecision.NEEDS_REVIEW:
        return [line for c in evidence_chains for line in fmt(c)]
    return []  # DEVELOP: intent + overallRationale 만 근거


# ── C11 컴포넌트 ─────────────────────────────────────────────────────
class ActionHandoffComponent:
    """(a) 순수 구조/선택 → (b) LLM 본문 생성 → ActionPrompt. 실패 시 예외."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def build(
        self,
        *,
        intent: StructuredIntent,
        overall: OverallDecision,
        overall_rationale: str,
        ranking: list[RankedCandidate],
        evidence_chains: list[EvidenceChain],
    ) -> ActionPrompt:
        # (a) 구조·선택 (순수) — 정합 가드 위반 시 여기서 ValueError
        target_asset_names = select_target_asset_names(overall, ranking)
        evidence_lines = _evidence_lines(overall, ranking, evidence_chains)
        note = should_note_unavailable(overall, ranking)

        # (b) LLM 자연어 본문 (grounding-only 페이로드) — 실패는 예외 전파
        req = ActionPromptRequest(
            decision_state=overall,
            intent=intent,
            overall_rationale=overall_rationale,
            target_asset_names=target_asset_names,
            evidence_lines=evidence_lines,
            note_unavailable=note,
        )
        prompt_text = self._llm.generate_action_prompt(req)
        if not prompt_text or not prompt_text.strip():
            raise ValueError("action prompt 본문 생성 실패(빈 응답)")

        return ActionPrompt(
            decision_state=overall,
            prompt_text=prompt_text,
            target_asset_names=target_asset_names,
        )
