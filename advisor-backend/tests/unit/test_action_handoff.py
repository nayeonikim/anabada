"""C11 ActionHandoff 예제 기반 단위 테스트 (CR-001, NFR-T1/T3).

CR-001 nfr-design-delta §2.4 배분: 예제(결정적 fixture) 대상.
- 최소 유용성: promptText 4요소(목표·근거·다음 작업·확인 사항) 존재.
- demoMode 재현(NFR-A3): 동일 입력 → 동일 promptText.
- INV-HANDOFF-3(비노출): promptText/targetAssetNames 에 미인가 자산 id·
  technicalFailureReason·excludedCount 등 미포함(grounding-only).
- INV-HANDOFF-4(비차단): generate_action_prompt 실패 → action_prompt=None ∧
  overall/ranking 등 핵심 결과 불변(BR-HANDOFF-FAIL).
(순수 구조/선택 로직 INV-HANDOFF-1/2/5 는 PBT — tests/pbt/test_action_handoff.py)
"""
from __future__ import annotations

import json
from pathlib import Path

from app.components.action_handoff import ActionHandoffComponent, _evidence_lines
from app.components.asset_search import AssetSearchComponent
from app.components.candidate_selection import CandidateSelectionComponent
from app.components.evidence_builder import EvidenceBuilderComponent
from app.components.feedback import FeedbackComponent
from app.components.permission_filter import PermissionFilterComponent
from app.components.reverification import ReVerificationComponent
from app.components.structure import IntentStructuringComponent
from app.domain.models import (
    ActionPrompt,
    CandidateState,
    ClassificationConfig,
    EvaluationStatus,
    EvidenceChain,
    EvidenceItem,
    LifecycleStatus,
    OverallDecision,
    PermissionContext,
    RankedCandidate,
    SourceId,
    StructuredIntent,
)
from app.infra.feedback_store import FeedbackStore
from app.infra.llm_client import ActionPromptRequest, FixtureLLMClient
from app.services.orchestrator import AdvisorOrchestratorService

_DATA = Path(__file__).resolve().parent.parent.parent / "data"
_FIXTURES = _DATA / "demo_fixtures.json"
CFG = ClassificationConfig(0.75, 0.50, 3)

_HERO_TEXT = "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"
_HERO_INTENT = StructuredIntent(
    role="Sales",
    goal="고객 현황 통합 조회 대시보드 구성",
    function="customer overview dashboard",  # actionHandoff fixture 키
    data="customer project forecast risk request",
    output="dashboard",
)
_REUSE_RATIONALE = "기존 자산을 그대로 재사용하도록 권고합니다."


def _hero_ranking() -> list[RankedCandidate]:
    return [
        RankedCandidate(
            candidate_id="asset-001",
            sources=[],
            asset_name="Customer 360 Dashboard",
            lifecycle_status=LifecycleStatus.ACTIVE,
            evaluation_status=EvaluationStatus.COMPLETED,
            reusability_score=0.92,
            candidate_state=CandidateState.REUSE,
            capability_match="fits",
            rank=1,
        )
    ]


def _component() -> ActionHandoffComponent:
    return ActionHandoffComponent(FixtureLLMClient.load(_FIXTURES))


def _build_hero() -> ActionPrompt:
    return _component().build(
        intent=_HERO_INTENT,
        overall=OverallDecision.REUSE,
        overall_rationale=_REUSE_RATIONALE,
        ranking=_hero_ranking(),
        evidence_chains=[],
    )


# ── 최소 유용성: 4요소 존재 ──────────────────────────────────────────
def test_min_utility_four_sections():
    ap = _build_hero()
    for marker in ("【목표】", "【근거】", "【다음 작업】", "【확인 사항】"):
        assert marker in ap.prompt_text


# ── demoMode 재현(결정성, NFR-A3) ────────────────────────────────────
def test_demo_mode_deterministic():
    assert _build_hero().prompt_text == _build_hero().prompt_text


# ── 참조 표기: grounding 근거 라인이 source_ref 포함 ─────────────────
def test_evidence_lines_include_source_ref():
    """프롬프트 본문이 대상 자산의 참조(source_ref)를 표기할 수 있도록 grounding 에 노출."""
    chain = EvidenceChain(
        candidate_id="asset-001",  # _hero_ranking()[0].candidate_id 와 일치
        evidence_items=[
            EvidenceItem(
                source=SourceId.JIRA,
                evidence_type="feature_history",
                title="Customer 360 Risk / Request Enhancement",
                source_ref="SALES-2841",
            )
        ],
        state_rationale="",
    )
    lines = _evidence_lines(OverallDecision.REUSE, _hero_ranking(), [chain])
    assert any("SALES-2841" in line for line in lines)


# ── INV-HANDOFF-3: 비노출(grounding-only) ────────────────────────────
def test_inv_handoff_3_non_disclosure():
    ap = _build_hero()
    haystack = ap.prompt_text + " " + " ".join(ap.target_asset_names)
    for forbidden in (
        "technicalFailureReason",
        "technical_failure_reason",
        "excludedCount",
        "asset-",  # 후보 내부 id 접두
    ):
        assert forbidden not in haystack
    assert ap.target_asset_names == ["Customer 360 Dashboard"]


# ── 오케스트레이터 배선 헬퍼(conftest registry/repository 사용) ──────
def _orchestrator(llm, registry, repository, tmp_path) -> AdvisorOrchestratorService:
    return AdvisorOrchestratorService(
        structuring=IntentStructuringComponent(llm),
        search=AssetSearchComponent(registry, repository),
        permission_filter=PermissionFilterComponent(repository),
        selection=CandidateSelectionComponent(),
        reverification=ReVerificationComponent(llm),
        evidence_builder=EvidenceBuilderComponent(),
        feedback=FeedbackComponent(FeedbackStore(tmp_path / "fb.jsonl")),
        config=CFG,
        action_handoff=ActionHandoffComponent(llm),
    )


class _FailingActionLLM(FixtureLLMClient):
    """structure/reverify는 정상 fixture, generate_action_prompt만 실패."""

    def generate_action_prompt(self, req: ActionPromptRequest) -> str:
        raise RuntimeError("action handoff boom")


# ── INV-HANDOFF-4: 비차단(실패 → None, 핵심 결과 불변) ───────────────
def test_inv_handoff_4_non_blocking(registry, repository, tmp_path):
    failing = _FailingActionLLM(json.loads(_FIXTURES.read_text(encoding="utf-8")))
    orch = _orchestrator(failing, registry, repository, tmp_path)

    intent = orch.submit_intent(_HERO_TEXT)
    assert isinstance(intent, StructuredIntent)
    ctx = PermissionContext(user_id="mock-sales-user", role="Sales")
    result = orch.advise(intent, ctx)

    assert result.action_prompt is None  # 비차단(실패 흡수)
    assert result.overall_decision == OverallDecision.REUSE  # 핵심 결과 불변
    assert result.ranking  # 랭킹 불변(비어있지 않음)
    assert result.is_recommendation is True


# ── demoMode e2e: 정상 경로 REUSE → action_prompt 채워짐 ─────────────
def test_demo_mode_e2e_reuse(registry, repository, tmp_path):
    llm = FixtureLLMClient.load(_FIXTURES)
    orch = _orchestrator(llm, registry, repository, tmp_path)

    intent = orch.submit_intent(_HERO_TEXT)
    ctx = PermissionContext(user_id="mock-sales-user", role="Sales")
    result = orch.advise(intent, ctx)

    assert result.action_prompt is not None
    assert result.action_prompt.decision_state == OverallDecision.REUSE  # INV-HANDOFF-1
    assert result.action_prompt.target_asset_names == ["Customer 360 Dashboard"]
    for marker in ("【목표】", "【근거】", "【다음 작업】", "【확인 사항】"):
        assert marker in result.action_prompt.prompt_text
    # 프롬프트 본문이 대상 자산의 참조(source_ref)를 포함
    assert "SALES-2841" in result.action_prompt.prompt_text
