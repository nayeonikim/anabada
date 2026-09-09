"""C1~C5, C7, C8 컴포넌트 예제 기반 단위 테스트 (LLM은 Fixture 주입)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.components.asset_search import AssetSearchComponent
from app.components.candidate_selection import CandidateSelectionComponent
from app.components.decision_classifier import classify_all
from app.components.evidence_builder import EvidenceBuilderComponent
from app.components.feedback import FeedbackComponent
from app.components.permission_filter import PermissionFilterComponent
from app.components.reverification import ReVerificationComponent
from app.components.structure import IntentStructuringComponent
from app.domain.errors import (
    DemoFixtureNotFoundError,
    EmptyIntentError,
    ReverificationUnavailableError,
)
from app.domain.models import (
    ClassificationConfig,
    EvaluationStatus,
    FeedbackVerdict,
    PermissionContext,
    StructuredIntent,
)
from app.infra.feedback_store import FeedbackStore
from app.infra.llm_client import FixtureLLMClient, LLMClient, ReverifyOutcome

_DATA = Path(__file__).resolve().parent.parent.parent / "data"
CFG = ClassificationConfig(0.75, 0.50, 3)


@pytest.fixture
def fixture_llm() -> FixtureLLMClient:
    return FixtureLLMClient.load(_DATA / "demo_fixtures.json")


# ── C1 structure ──────────────────────────────────────────────────
def test_structure_empty_raises(fixture_llm):
    c1 = IntentStructuringComponent(fixture_llm)
    with pytest.raises(EmptyIntentError):
        c1.structure("   ")


def test_structure_detect_missing_fields():
    intent = StructuredIntent(role="", goal="g", function="f", data="", output="o")
    missing = IntentStructuringComponent.detect_missing_fields(intent)
    assert set(missing) == {"role", "data"}
    clar = IntentStructuringComponent.build_clarification(missing)
    assert len(clar.questions) == 2


def test_structure_demo_unmatched_raises(fixture_llm):
    c1 = IntentStructuringComponent(fixture_llm)
    with pytest.raises(DemoFixtureNotFoundError):
        c1.structure("존재하지 않는 요청 텍스트")


def test_structure_hero(fixture_llm):
    c1 = IntentStructuringComponent(fixture_llm)
    intent = c1.structure(
        "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"
    )
    assert intent.role == "Sales"
    assert IntentStructuringComponent.detect_missing_fields(intent) == []


# ── C2 asset_search ───────────────────────────────────────────────
def test_search_drops_irrelevant(registry, repository):
    c2 = AssetSearchComponent(registry, repository)
    intent = StructuredIntent(
        role="Sales", goal="고객 현황", function="customer overview dashboard",
        data="customer forecast risk", output="dashboard",
    )
    cands = c2.search(intent)
    assert cands
    assert all(c.relevance > 0 for c in cands)
    # 다중 Source Evidence 동반
    top = max(cands, key=lambda c: c.relevance)
    assert len(top.sources) >= 1


# ── C3 permission_filter ──────────────────────────────────────────
def test_permission_filter_sales_excludes_dev(registry, repository):
    c2 = AssetSearchComponent(registry, repository)
    c3 = PermissionFilterComponent(repository)
    intent = StructuredIntent(
        role="Sales", goal="유사 코드", function="code search tool",
        data="repository code", output="tool",
    )
    cands = c2.search(intent)
    ctx = PermissionContext(user_id="mock-sales-user", role="Sales")
    result = c3.filter(cands, ctx)
    # Similar Code Finder(asset-005)/Issue&PR Agent(asset-006)는 Developer 전용 → 제외
    accessible_ids = {c.id for c in result.accessible}
    assert "asset-005" not in accessible_ids
    assert "asset-006" not in accessible_ids


# ── C4 candidate_selection ────────────────────────────────────────
def test_top_n_orders_by_relevance():
    from app.domain.models import AssetType, Candidate, LifecycleStatus

    def c(cid, rel, name):
        return Candidate(cid, name, AssetType.TOOL, "", [], LifecycleStatus.ACTIVE, [], [], [], rel)

    c4 = CandidateSelectionComponent()
    cands = [c("a", 0.3, "a"), c("b", 0.9, "b"), c("c", 0.6, "c")]
    top = c4.select_top_n(cands, 2)
    assert [x.id for x in top] == ["b", "c"]


# ── C5 reverification ─────────────────────────────────────────────
class _AllFailLLM(LLMClient):
    def structure_intent(self, raw_text):  # noqa: D102
        raise RuntimeError("n/a")

    def reverify(self, intent, candidate):  # noqa: D102
        raise RuntimeError("boom")


def test_reverify_all_fail_raises(registry, repository):
    c2 = AssetSearchComponent(registry, repository)
    c3 = PermissionFilterComponent(repository)
    c4 = CandidateSelectionComponent()
    intent = StructuredIntent("Sales", "고객 현황", "customer overview dashboard",
                              "customer forecast", "dashboard")
    ctx = PermissionContext("mock-sales-user", "Sales")
    top = c4.select_top_n(c3.filter(c2.search(intent), ctx).accessible, 3)
    c5 = ReVerificationComponent(_AllFailLLM())
    with pytest.raises(ReverificationUnavailableError):
        c5.reverify(top, intent)


class _PartialFailLLM(LLMClient):
    def structure_intent(self, raw_text):  # noqa: D102
        raise RuntimeError("n/a")

    def reverify(self, intent, candidate):  # noqa: D102
        if candidate.id.endswith("1"):
            raise RuntimeError("boom")
        return ReverifyOutcome(0.9, "r", "n", True, None)


def test_reverify_partial_fail_degrades():
    from app.domain.models import AssetType, Candidate, LifecycleStatus

    def c(cid):
        return Candidate(cid, cid, AssetType.TOOL, "", [], LifecycleStatus.ACTIVE, [], [], [], 0.5)

    intent = StructuredIntent()
    c5 = ReVerificationComponent(_PartialFailLLM())
    verified = c5.reverify([c("asset-001"), c("asset-002")], intent)
    by_id = {v.candidate.id: v for v in verified}
    assert by_id["asset-001"].evaluation_status == EvaluationStatus.UNAVAILABLE
    assert by_id["asset-001"].reusability_score is None
    assert by_id["asset-002"].evaluation_status == EvaluationStatus.COMPLETED


# ── C7 evidence_builder ───────────────────────────────────────────
def test_evidence_builder_unavailable_generic_rationale():
    from app.domain.models import AssetType, Candidate, LifecycleStatus, VerifiedCandidate

    cand = Candidate("asset-x", "X", AssetType.TOOL, "", [], LifecycleStatus.ACTIVE, [], [], [], 0.5)
    vc = VerifiedCandidate.unavailable(cand, "internal timeout detail")
    states = classify_all([vc], CFG)
    chains = EvidenceBuilderComponent().build([vc], states)
    # 내부 기술 사유 비노출
    assert "internal timeout detail" not in chains[0].state_rationale


# ── C8 feedback ───────────────────────────────────────────────────
def test_feedback_append(tmp_path):
    store = FeedbackStore(tmp_path / "fb.jsonl")
    c8 = FeedbackComponent(store)
    fid = c8.record("res-1", "asset-001", FeedbackVerdict.USEFUL)
    assert fid
    assert len(store.all()) == 1
    # 영속: 재로드
    store2 = FeedbackStore(tmp_path / "fb.jsonl")
    assert len(store2.all()) == 1
