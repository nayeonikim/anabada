"""데모 fixture 커버리지 회귀 테스트 (#2 방어).

demo_fixtures.json의 각 structure 시나리오를 실제 파이프라인(search→permission→top-N)에
통과시켜, 선별된 Top-N 후보가 reverify fixture로 100% 커버됨을 보장한다.

커버되지 않은 후보가 Top-N에 들어오면 /advise가 DemoFixtureNotFoundError(422)로 깨지므로,
mock 데이터(assets/evidence)나 keyword/권한 변경에 대한 조기 경보 역할을 한다.
"""
from __future__ import annotations

import json
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
    PermissionContext,
    StructuredIntent,
)
from app.infra.feedback_store import FeedbackStore
from app.infra.llm_client import FixtureLLMClient
from app.services.orchestrator import AdvisorOrchestratorService

_DATA = Path(__file__).resolve().parent.parent.parent / "data"
_FIXTURES = json.loads((_DATA / "demo_fixtures.json").read_text(encoding="utf-8"))
CFG = ClassificationConfig(0.75, 0.50, 3)

_STRUCTURE_KEYS = list(_FIXTURES["structure"].keys())


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


def _intent_from_structure(struct: dict) -> StructuredIntent:
    return StructuredIntent(
        role=struct.get("role") or "",
        goal=struct.get("goal") or "",
        function=struct.get("function") or "",
        data=struct.get("data") or "",
        output=struct.get("output") or "",
    )


# ── 회귀 가드 1: 모든 데모 시나리오가 fixture 공백 없이 advise 성공 ────
@pytest.mark.parametrize("raw_text", _STRUCTURE_KEYS)
def test_demo_scenarios_advise_without_fixture_gaps(orchestrator, raw_text):
    intent = orchestrator.submit_intent(raw_text)
    if isinstance(intent, ClarificationRequest):
        pytest.skip("clarification 시나리오는 advise 대상 아님")
    ctx = PermissionContext(user_id="regression-user", role=intent.role)
    # 커버되지 않은 Top-N 후보가 있으면 여기서 DemoFixtureNotFoundError가 발생한다.
    result = orchestrator.advise(intent, ctx)
    assert result is not None


# ── 회귀 가드 2: Top-N ⊆ reverify fixture (진단용 명시 검증) ─────────
@pytest.mark.parametrize("raw_text", _STRUCTURE_KEYS)
def test_top_n_candidates_are_covered_by_reverify_fixture(
    raw_text, registry, repository
):
    struct = _FIXTURES["structure"][raw_text]
    role = struct.get("role") or ""
    if not role:  # clarify 시나리오(role 누락) → advise 미수행
        pytest.skip("role 누락 시나리오")

    intent = _intent_from_structure(struct)
    search = AssetSearchComponent(registry, repository)
    pfilter = PermissionFilterComponent(repository)
    selection = CandidateSelectionComponent()

    accessible = pfilter.filter(
        search.search(intent), PermissionContext("regression-user", role)
    ).accessible
    top_n = selection.select_top_n(accessible, CFG.top_n)

    covered = set(_FIXTURES["reverify"].get(intent.function, {}).keys())
    selected = {c.id for c in top_n}
    missing = selected - covered
    assert not missing, (
        f"시나리오 '{intent.function}'의 Top-N 후보 {sorted(missing)}가 "
        f"reverify fixture에 없음 → /advise가 422로 깨진다"
    )


# ── 회귀 가드 3: reverify 시나리오 키가 structure.function과 정합 ────
def test_reverify_scenario_keys_align_with_structure_functions():
    functions = {(v.get("function") or "") for v in _FIXTURES["structure"].values()}
    for scenario_key in _FIXTURES["reverify"].keys():
        assert scenario_key in functions, (
            f"reverify 시나리오 '{scenario_key}'가 어떤 structure.function과도 "
            f"매칭되지 않아 데모에서 도달 불가"
        )
