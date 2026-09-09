"""Property-Based Tests for C11 ActionHandoff 순수 로직 (NFR-T1, CR-001).

CR-001 nfr-design-delta §2.4 PBT 배분: 순수·결정적 구조/선택 로직만 PBT 대상.
- INV-HANDOFF-1: ActionPrompt.decision_state == 요청 overallDecision.
- INV-HANDOFF-2: targetAssetNames 규칙(REUSE/EXTEND=[ranking[0]] ⊆ 접근가능명, 비어있지 않음;
  DEVELOP/NEEDS_REVIEW=[]; REUSE/EXTEND ∧ ranking 빈 → ValueError 정합 가드).
- INV-HANDOFF-5: '평가 미완료' 문구 게이팅(NEEDS_REVIEW ∧ ∃UNAVAILABLE 일 때만 True).
(문안 생성/비노출/비차단은 예제 기반 — tests/unit/test_action_handoff.py)
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.components.action_handoff import (
    ActionHandoffComponent,
    select_target_asset_names,
    should_note_unavailable,
)
from app.domain.models import (
    CandidateState,
    EvaluationStatus,
    LifecycleStatus,
    OverallDecision,
    RankedCandidate,
    StructuredIntent,
)
from app.infra.llm_client import ActionPromptRequest, LLMClient

_REUSE_EXTEND = (OverallDecision.REUSE, OverallDecision.EXTEND_EXISTING)


@st.composite
def ranked_candidates(draw, min_size=0, max_size=5):
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    out = []
    for i in range(n):
        status = draw(
            st.sampled_from([EvaluationStatus.COMPLETED, EvaluationStatus.UNAVAILABLE])
        )
        score = (
            draw(st.floats(min_value=0.0, max_value=1.0))
            if status == EvaluationStatus.COMPLETED
            else None  # UNAVAILABLE → score None (P11 정합)
        )
        out.append(
            RankedCandidate(
                candidate_id=f"asset-{i:03d}",
                sources=[],
                asset_name=draw(st.text(alphabet="abcdefg", min_size=1, max_size=4)),
                lifecycle_status=LifecycleStatus.ACTIVE,
                evaluation_status=status,
                reusability_score=score,
                candidate_state=CandidateState.REUSE,  # 순수 대상 로직과 무관
                capability_match="x",
                rank=i + 1,
            )
        )
    return out


# ── INV-HANDOFF-2: 대상 Asset 선택 규칙 ──────────────────────────────
@given(ranking=ranked_candidates(), overall=st.sampled_from(list(OverallDecision)))
def test_inv_handoff_2_target_asset_names(ranking, overall):
    if overall in _REUSE_EXTEND:
        if ranking:
            result = select_target_asset_names(overall, ranking)
            assert result == [ranking[0].asset_name]
            assert result  # 비어있지 않음
            assert set(result) <= {r.asset_name for r in ranking}  # 접근가능명 부분집합
        else:
            with pytest.raises(ValueError):  # 정합 가드(§2.2)
                select_target_asset_names(overall, ranking)
    else:  # DEVELOP / NEEDS_REVIEW
        assert select_target_asset_names(overall, ranking) == []


# ── INV-HANDOFF-5: §3.1 '평가 미완료' 문구 게이팅 ────────────────────
@given(ranking=ranked_candidates(), overall=st.sampled_from(list(OverallDecision)))
def test_inv_handoff_5_note_unavailable_gating(ranking, overall):
    result = should_note_unavailable(overall, ranking)
    has_unavail = any(
        r.evaluation_status == EvaluationStatus.UNAVAILABLE for r in ranking
    )
    if overall == OverallDecision.NEEDS_REVIEW:
        assert result == has_unavail
    else:
        assert result is False


# ── INV-HANDOFF-1: decisionState == overallDecision ─────────────────
class _StubLLM(LLMClient):
    """generate_action_prompt만 사용(고정 비어있지 않은 문자열). 나머지는 미사용."""

    def structure_intent(self, raw_text):  # pragma: no cover - 미사용
        raise NotImplementedError

    def reverify(self, intent, candidate):  # pragma: no cover - 미사용
        raise NotImplementedError

    def generate_action_prompt(self, req: ActionPromptRequest) -> str:
        return "고정 본문(non-empty)"


@given(ranking=ranked_candidates(min_size=1), overall=st.sampled_from(list(OverallDecision)))
def test_inv_handoff_1_decision_state(ranking, overall):
    comp = ActionHandoffComponent(_StubLLM())
    intent = StructuredIntent(role="r", goal="g", function="f", data="d", output="o")
    ap = comp.build(
        intent=intent,
        overall=overall,
        overall_rationale="rr",
        ranking=ranking,
        evidence_chains=[],
    )
    assert ap.decision_state == overall
    # REUSE/EXTEND ⇒ 대상명 존재, 그 외 ⇒ []
    if overall in _REUSE_EXTEND:
        assert ap.target_asset_names == [ranking[0].asset_name]
    else:
        assert ap.target_asset_names == []
