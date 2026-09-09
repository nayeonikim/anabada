"""S1 Orchestrator end-to-end — Hero + 3 Unhappy (Fixture 주입).

demoMode fixture(LLM) + 실제 mock 데이터(repository/registry)로 §3 흐름 검증.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.components.asset_search import AssetSearchComponent
from app.components.candidate_selection import CandidateSelectionComponent
from app.components.evidence_builder import EvidenceBuilderComponent
from app.components.feedback import FeedbackComponent
from app.components.permission_filter import PermissionFilterComponent
from app.components.reverification import ReVerificationComponent
from app.components.structure import IntentStructuringComponent
from app.domain.models import (
    ClarificationRequest,
    ClassificationConfig,
    EvaluationStatus,
    FeedbackVerdict,
    OverallDecision,
    PermissionContext,
    StructuredIntent,
)
from app.infra.feedback_store import FeedbackStore
from app.infra.llm_client import FixtureLLMClient
from app.services.orchestrator import AdvisorOrchestratorService

_DATA = Path(__file__).resolve().parent.parent.parent / "data"
CFG = ClassificationConfig(0.75, 0.50, 3)

_HERO_TEXT = "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"
_NEEDS_REVIEW_TEXT = "예전 프로젝트에서 쓰던 공통 기능 라이브러리를 재사용하고 싶어요"
_DEVELOP_TEXT = "릴리스 버전 체크와 아티팩트 검증을 자동화하는 스크립트가 필요해요"
_CLARIFY_TEXT = "대시보드 하나 만들어줘"


@pytest.fixture
def orchestrator(registry, repository, tmp_path) -> AdvisorOrchestratorService:
    llm = FixtureLLMClient.load(_DATA / "demo_fixtures.json")
    return AdvisorOrchestratorService(
        structuring=IntentStructuringComponent(llm),
        search=AssetSearchComponent(registry, repository),
        permission_filter=PermissionFilterComponent(repository),
        selection=CandidateSelectionComponent(),
        reverification=ReVerificationComponent(llm),
        evidence_builder=EvidenceBuilderComponent(),
        feedback=FeedbackComponent(FeedbackStore(tmp_path / "fb.jsonl")),
        config=CFG,
    )


def _advise(orchestrator, text, role):
    intent = orchestrator.submit_intent(text)
    assert isinstance(intent, StructuredIntent)
    ctx = PermissionContext(user_id=f"mock-{role.lower()}-user", role=role)
    return orchestrator.advise(intent, ctx)


# ── Hero: REUSE ───────────────────────────────────────────────────
def test_hero_reuse(orchestrator):
    result = _advise(orchestrator, _HERO_TEXT, "Sales")
    assert result.overall_decision == OverallDecision.REUSE
    assert result.is_recommendation is True
    # 최상위 랭킹 = Customer 360 Dashboard(asset-001), REUSE, score 0.92
    top = result.ranking[0]
    assert top.candidate_id == "asset-001"
    assert top.reusability_score == pytest.approx(0.92)
    assert top.evaluation_status == EvaluationStatus.COMPLETED
    assert top.rank == 1
    # Evidence Chain은 다중 Source
    chain = next(c for c in result.evidence_chains if c.candidate_id == "asset-001")
    assert len(chain.evidence_items) >= 1


# ── Unhappy 1: NEEDS_REVIEW (deprecated 근거부족 최고 Score) ─────────
def test_unhappy_needs_review(orchestrator):
    result = _advise(orchestrator, _NEEDS_REVIEW_TEXT, "Developer")
    assert result.overall_decision == OverallDecision.NEEDS_REVIEW
    # asset-007(deprecated)이 최고 Score COMPLETED이나 evidenceSufficient=false → NEEDS_REVIEW
    ids = {r.candidate_id for r in result.ranking}
    assert "asset-007" in ids


# ── Unhappy 2: DEVELOP (접근 가능 관련 자산 0) ───────────────────────
def test_unhappy_develop(orchestrator):
    # Sales는 Developer 전용 Release Task Script(asset-009)에 접근 불가 → accessible 0 → DEVELOP
    result = _advise(orchestrator, _DEVELOP_TEXT, "Sales")
    assert result.overall_decision == OverallDecision.DEVELOP
    assert result.ranking == []


# ── Unhappy 3: Clarify (role/data 누락) ─────────────────────────────
def test_unhappy_clarify(orchestrator):
    intent = orchestrator.submit_intent(_CLARIFY_TEXT)
    assert isinstance(intent, ClarificationRequest)
    assert set(intent.missing_fields) == {"role", "data"}
    assert len(intent.questions) == 2


# ── 피드백 기록 ────────────────────────────────────────────────────
def test_submit_feedback(orchestrator):
    fid = orchestrator.submit_feedback("res-1", "asset-001", FeedbackVerdict.USEFUL)
    assert fid
