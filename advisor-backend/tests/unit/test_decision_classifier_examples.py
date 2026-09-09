"""예제 기반 경계 케이스 — C6 DecisionClassifier."""
from __future__ import annotations

from app.components.decision_classifier import (
    classify_candidate,
    classify_all,
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

CFG = ClassificationConfig(reuse_threshold=0.75, extend_threshold=0.50, top_n=3)


def _c(cid, name="asset"):
    return Candidate(cid, name, AssetType.TOOL, "", [], LifecycleStatus.ACTIVE, [], [], [], 0.5)


def test_reuse_boundary():
    vc = VerifiedCandidate.completed(_c("a"), 0.75, "r", "n", True)
    assert classify_candidate(vc, CFG) == CandidateState.REUSE


def test_extend_boundary():
    vc = VerifiedCandidate.completed(_c("a"), 0.50, "r", "n", True)
    assert classify_candidate(vc, CFG) == CandidateState.EXTEND_EXISTING


def test_below_extend_is_needs_review():
    vc = VerifiedCandidate.completed(_c("a"), 0.49, "r", "n", True)
    assert classify_candidate(vc, CFG) == CandidateState.NEEDS_REVIEW


def test_insufficient_evidence_overrides_high_score():
    vc = VerifiedCandidate.completed(_c("a"), 0.99, "r", "n", evidence_sufficient=False)
    assert classify_candidate(vc, CFG) == CandidateState.NEEDS_REVIEW


def test_unavailable_is_needs_review():
    vc = VerifiedCandidate.unavailable(_c("a"), "timeout")
    assert classify_candidate(vc, CFG) == CandidateState.NEEDS_REVIEW


def test_overall_develop_when_no_accessible():
    assert derive_overall([], {}, has_any_accessible=False) == OverallDecision.DEVELOP


def test_overall_develop_all_completed_needs_review():
    vcs = [VerifiedCandidate.completed(_c("a"), 0.2, "r", "n", True)]
    states = classify_all(vcs, CFG)
    assert derive_overall(vcs, states, True) == OverallDecision.DEVELOP


def test_overall_needs_review_when_unavailable_present_no_reuse_extend():
    vcs = [
        VerifiedCandidate.completed(_c("a"), 0.2, "r", "n", True),  # NEEDS_REVIEW
        VerifiedCandidate.unavailable(_c("b"), "timeout"),          # NEEDS_REVIEW
    ]
    states = classify_all(vcs, CFG)
    # 기술 실패↛DEVELOP
    assert derive_overall(vcs, states, True) == OverallDecision.NEEDS_REVIEW


def test_overall_reuse_picks_best_completed():
    vcs = [
        VerifiedCandidate.completed(_c("a"), 0.92, "r", "n", True),  # REUSE
        VerifiedCandidate.completed(_c("b"), 0.55, "r", "n", True),  # EXTEND
    ]
    states = classify_all(vcs, CFG)
    assert derive_overall(vcs, states, True) == OverallDecision.REUSE


def test_rank_unavailable_last():
    vcs = [
        VerifiedCandidate.unavailable(_c("u", "zzz"), "t"),
        VerifiedCandidate.completed(_c("r", "mmm"), 0.9, "r", "n", True),
    ]
    states = classify_all(vcs, CFG)
    ranked = rank_candidates(vcs, states)
    assert ranked[0].candidate.id == "r"
    assert ranked[-1].candidate.id == "u"
