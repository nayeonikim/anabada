"""Property-Based Tests for C6 DecisionClassifier (NFR-T1).

business-rules.md PBT 불변식 P1~P11 (§7.4 evaluationStatus 정합).
"""
from __future__ import annotations

from hypothesis import assume, given
from hypothesis import strategies as st

from app.components.decision_classifier import (
    classify_all,
    classify_candidate,
    derive_overall,
    rank_candidates,
)
from app.domain.models import (
    AssetType,
    Candidate,
    CandidateState,
    ClassificationConfig,
    EvaluationStatus,
    LifecycleStatus,
    OverallDecision,
    VerifiedCandidate,
)

_STATES = {CandidateState.REUSE, CandidateState.EXTEND_EXISTING, CandidateState.NEEDS_REVIEW}


def _candidate(cid: str, name: str) -> Candidate:
    return Candidate(
        id=cid,
        asset_name=name,
        type=AssetType.TOOL,
        summary="",
        capabilities=[],
        lifecycle_status=LifecycleStatus.ACTIVE,
        constraints=[],
        evidence=[],
        sources=[],
        relevance=0.5,
    )


@st.composite
def verified_candidates(draw, min_size=0, max_size=6):
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    out = []
    for i in range(n):
        cid = f"asset-{i:03d}"
        name = draw(st.text(alphabet="abcdefg", min_size=1, max_size=4))
        status = draw(st.sampled_from([EvaluationStatus.COMPLETED, EvaluationStatus.UNAVAILABLE]))
        if status == EvaluationStatus.COMPLETED:
            score = draw(st.floats(min_value=0.0, max_value=1.0))
            suff = draw(st.booleans())
            out.append(
                VerifiedCandidate.completed(
                    candidate=_candidate(cid, name),
                    reusability_score=score,
                    reasoning="r",
                    role_task_context_note="n",
                    evidence_sufficient=suff,
                )
            )
        else:
            out.append(
                VerifiedCandidate.unavailable(_candidate(cid, name), "tech")
            )
    return out


configs = st.builds(
    ClassificationConfig,
    reuse_threshold=st.floats(min_value=0.01, max_value=1.0),
    extend_threshold=st.floats(min_value=0.01, max_value=1.0),
    top_n=st.just(3),
)


# ── P1 ────────────────────────────────────────────────────────────
@given(vcs=verified_candidates(min_size=1), config=configs)
def test_p1_classify_range_and_unavailable_needs_review(vcs, config):
    for vc in vcs:
        state = classify_candidate(vc, config)
        assert state in _STATES  # 치역 불변
        if vc.evaluation_status == EvaluationStatus.UNAVAILABLE:
            assert state == CandidateState.NEEDS_REVIEW


# ── P2 (COMPLETED에만) ───────────────────────────────────────────
@given(
    score=st.floats(min_value=0.0, max_value=1.0),
    config=configs,
)
def test_p2_completed_insufficient_is_needs_review(score, config):
    vc = VerifiedCandidate.completed(
        _candidate("a", "a"), score, "r", "n", evidence_sufficient=False
    )
    assert classify_candidate(vc, config) == CandidateState.NEEDS_REVIEW


# ── P3 단조성 (COMPLETED, evidenceSufficient=true) ───────────────
@given(
    s1=st.floats(min_value=0.0, max_value=1.0),
    s2=st.floats(min_value=0.0, max_value=1.0),
    config=configs,
)
def test_p3_score_monotonic(s1, s2, config):
    lo, hi = min(s1, s2), max(s1, s2)
    order = {CandidateState.NEEDS_REVIEW: 0, CandidateState.EXTEND_EXISTING: 1, CandidateState.REUSE: 2}
    vlo = VerifiedCandidate.completed(_candidate("a", "a"), lo, "r", "n", True)
    vhi = VerifiedCandidate.completed(_candidate("a", "a"), hi, "r", "n", True)
    assert order[classify_candidate(vhi, config)] >= order[classify_candidate(vlo, config)]


# ── P4 (COMPLETED) ───────────────────────────────────────────────
@given(config=configs)
def test_p4_score_ge_reuse_is_reuse(config):
    reuse_t = config.reuse_threshold if 0 < config.extend_threshold <= config.reuse_threshold <= 1 else 0.75
    vc = VerifiedCandidate.completed(_candidate("a", "a"), 1.0, "r", "n", True)
    # score=1.0 >= 유효 reuse threshold
    assert classify_candidate(vc, config) == CandidateState.REUSE
    assert reuse_t <= 1.0


# ── P5 / P10 DEVELOP 조건 ────────────────────────────────────────
@given(vcs=verified_candidates(), config=configs)
def test_p5_p10_develop_only_when_no_unavailable(vcs, config):
    states = classify_all(vcs, config)
    overall = derive_overall(vcs, states, has_any_accessible=len(vcs) > 0)
    if overall == OverallDecision.DEVELOP:
        # DEVELOP ⇒ (검색0) ∨ (전 후보 COMPLETED ∧ REUSE/EXTEND 0)
        if vcs:
            assert all(vc.evaluation_status == EvaluationStatus.COMPLETED for vc in vcs)
            assert all(
                states[vc.candidate.id] == CandidateState.NEEDS_REVIEW for vc in vcs
            )
    # P10: UNAVAILABLE 존재 ∧ COMPLETED REUSE/EXTEND 없음 ⇒ NEEDS_REVIEW
    has_unavail = any(vc.evaluation_status == EvaluationStatus.UNAVAILABLE for vc in vcs)
    completed_re = [
        vc for vc in vcs
        if vc.evaluation_status == EvaluationStatus.COMPLETED
        and states[vc.candidate.id] in (CandidateState.REUSE, CandidateState.EXTEND_EXISTING)
    ]
    if vcs and has_unavail and not completed_re:
        assert overall == OverallDecision.NEEDS_REVIEW


# ── P6 ───────────────────────────────────────────────────────────
@given(vcs=verified_candidates(min_size=1), config=configs)
def test_p6_completed_reuse_extend_not_develop(vcs, config):
    states = classify_all(vcs, config)
    overall = derive_overall(vcs, states, has_any_accessible=True)
    completed_re = any(
        vc.evaluation_status == EvaluationStatus.COMPLETED
        and states[vc.candidate.id] in (CandidateState.REUSE, CandidateState.EXTEND_EXISTING)
        for vc in vcs
    )
    if completed_re:
        assert overall != OverallDecision.DEVELOP


# ── P7 ───────────────────────────────────────────────────────────
@given(vcs=verified_candidates(), config=configs)
def test_p7_classify_all_size(vcs, config):
    states = classify_all(vcs, config)
    assert len(states) == len({vc.candidate.id for vc in vcs})


# ── P8 랭킹: 순열 + 결정성 + 계층 ────────────────────────────────
@given(vcs=verified_candidates(), config=configs)
def test_p8_rank_permutation_deterministic_layered(vcs, config):
    states = classify_all(vcs, config)
    r1 = rank_candidates(vcs, states)
    r2 = rank_candidates(vcs, states)
    # 순열
    assert sorted(v.candidate.id for v in r1) == sorted(v.candidate.id for v in vcs)
    # 결정성
    assert [v.candidate.id for v in r1] == [v.candidate.id for v in r2]
    # 계층: 모든 UNAVAILABLE은 임의 COMPLETED보다 뒤
    statuses = [v.evaluation_status for v in r1]
    seen_unavail = False
    for s in statuses:
        if s == EvaluationStatus.UNAVAILABLE:
            seen_unavail = True
        elif seen_unavail:
            raise AssertionError("COMPLETED가 UNAVAILABLE 뒤에 위치")


# ── P9 임계값 폴백 ───────────────────────────────────────────────
@given(
    reuse=st.floats(min_value=0.0, max_value=2.0),
    extend=st.floats(min_value=0.0, max_value=2.0),
)
def test_p9_threshold_fallback(reuse, extend):
    assume(not (0 < extend <= reuse <= 1))  # 제약 위반 케이스
    config = ClassificationConfig(reuse_threshold=reuse, extend_threshold=extend, top_n=3)
    # 폴백(0.50/0.75) 후에도 P1~P4 성립: score=1.0 → REUSE, score=0.0 → NEEDS_REVIEW
    reuse_vc = VerifiedCandidate.completed(_candidate("a", "a"), 1.0, "r", "n", True)
    low_vc = VerifiedCandidate.completed(_candidate("b", "b"), 0.0, "r", "n", True)
    assert classify_candidate(reuse_vc, config) == CandidateState.REUSE
    assert classify_candidate(low_vc, config) == CandidateState.NEEDS_REVIEW


# ── P11 score-status 정합 ────────────────────────────────────────
@given(vcs=verified_candidates(min_size=1))
def test_p11_score_status_consistency(vcs):
    for vc in vcs:
        if vc.evaluation_status == EvaluationStatus.UNAVAILABLE:
            assert vc.reusability_score is None
        else:
            assert vc.reusability_score is not None
            assert 0.0 <= vc.reusability_score <= 1.0
