"""도메인 엔티티/열거 — 기술 중립 도메인 모델 (functional-design/domain-entities.md).

NFR Design §7.1 반영:
- VerifiedCandidate/RankedCandidate에 `evaluation_status(COMPLETED|UNAVAILABLE)`
- `reusability_score`는 nullable (UNAVAILABLE → None)
- `technical_failure_reason`은 **서버 내부 전용**(공개 DTO 미포함)
- ExcludedCandidate는 **서버 내부 전용**(공개 API 미노출)

이 모듈은 내부 도메인 타입이다. 공개 응답은 app/api/schemas.py의 DTO가 담당하며,
내부 타입을 그대로 노출하지 않는다(§3.2 Type-Enforced Non-Disclosure).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ── 열거 ─────────────────────────────────────────────────────────────

class SourceId(str, Enum):
    GITHUB = "GitHub"
    CONFLUENCE = "Confluence"
    JIRA = "Jira"
    IMS = "IMS"
    BIZFORCE = "BizForce"
    EDM = "EDM"


class AssetType(str, Enum):
    DASHBOARD = "dashboard"
    API = "api"
    REPOSITORY = "repository"
    TOOL = "tool"
    LIBRARY = "library"
    SCRIPT = "script"
    AGENT = "agent"
    SKILL = "skill"
    WORKFLOW = "workflow"
    CAPABILITY = "capability"


class LifecycleStatus(str, Enum):
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"


class CandidateState(str, Enum):
    """후보 단위 State — DEVELOP 없음."""
    REUSE = "REUSE"
    EXTEND_EXISTING = "EXTEND_EXISTING"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class OverallDecision(str, Enum):
    """요청 단위 권고 — DEVELOP 포함."""
    REUSE = "REUSE"
    EXTEND_EXISTING = "EXTEND_EXISTING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    DEVELOP = "DEVELOP"


class EvaluationStatus(str, Enum):
    """C5 재검증 상태 (§7.1). COMPLETED=정상, UNAVAILABLE=기술적 평가 실패."""
    COMPLETED = "COMPLETED"
    UNAVAILABLE = "UNAVAILABLE"


class ExclusionReason(str, Enum):
    NOT_ACCESSIBLE = "NOT_ACCESSIBLE"


class FeedbackVerdict(str, Enum):
    USEFUL = "useful"
    NOT_FIT = "notFit"


# ── Intent ──────────────────────────────────────────────────────────

REQUIRED_INTENT_FIELDS = ("role", "goal", "function", "data", "output")


@dataclass
class StructuredIntent:
    role: str = ""
    goal: str = ""
    function: str = ""
    data: str = ""
    output: str = ""


@dataclass
class ClarificationRequest:
    missing_fields: list[str]
    questions: list[str]


# ── Asset / Evidence (mock 원본) ────────────────────────────────────

@dataclass
class Evidence:
    id: str
    asset_id: str
    source: SourceId
    evidence_type: str
    title: str
    summary: str
    source_ref: str
    last_updated: Optional[str] = None


@dataclass
class Asset:
    id: str
    name: str
    type: AssetType
    summary: str
    capabilities: list[str] = field(default_factory=list)
    lifecycle_status: LifecycleStatus = LifecycleStatus.UNKNOWN
    constraints: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    allowed_users: list[str] = field(default_factory=list)


# ── Candidate (검색 결과 뷰, asset 단위) ────────────────────────────

@dataclass
class Candidate:
    id: str
    asset_name: str
    type: AssetType
    summary: str
    capabilities: list[str]
    lifecycle_status: LifecycleStatus
    constraints: list[str]
    evidence: list[Evidence]
    sources: list[SourceId]
    relevance: float


@dataclass
class PermissionContext:
    user_id: str
    role: str


@dataclass
class ExcludedCandidate:
    """⚠️ 서버 내부 전용 — 공개 API 미노출 (§2.6/FR-8/NFR-4)."""
    candidate: Candidate
    reason: ExclusionReason
    evidence_ref: str


# ── VerifiedCandidate (C5 산출) — evaluationStatus 계약 (§7.1) ───────

@dataclass
class VerifiedCandidate:
    candidate: Candidate
    evaluation_status: EvaluationStatus
    reusability_score: Optional[float]  # UNAVAILABLE → None (P11)
    reasoning: str = ""
    role_task_context_note: str = ""
    evidence_sufficient: bool = True
    insufficiency_reason: Optional[str] = None
    technical_failure_reason: Optional[str] = None  # ⚠️ 서버 내부 전용

    @staticmethod
    def completed(
        candidate: Candidate,
        reusability_score: float,
        reasoning: str,
        role_task_context_note: str,
        evidence_sufficient: bool,
        insufficiency_reason: Optional[str] = None,
    ) -> "VerifiedCandidate":
        return VerifiedCandidate(
            candidate=candidate,
            evaluation_status=EvaluationStatus.COMPLETED,
            reusability_score=reusability_score,
            reasoning=reasoning,
            role_task_context_note=role_task_context_note,
            evidence_sufficient=evidence_sufficient,
            insufficiency_reason=insufficiency_reason,
        )

    @staticmethod
    def unavailable(
        candidate: Candidate, technical_failure_reason: str
    ) -> "VerifiedCandidate":
        return VerifiedCandidate(
            candidate=candidate,
            evaluation_status=EvaluationStatus.UNAVAILABLE,
            reusability_score=None,
            reasoning="평가를 완료하지 못했습니다.",
            role_task_context_note="",
            evidence_sufficient=False,
            insufficiency_reason=None,
            technical_failure_reason=technical_failure_reason,
        )


# ── 랭킹/Evidence/결과 ──────────────────────────────────────────────

@dataclass
class RankedCandidate:
    candidate_id: str
    sources: list[SourceId]
    asset_name: str
    lifecycle_status: LifecycleStatus
    evaluation_status: EvaluationStatus
    reusability_score: Optional[float]
    candidate_state: CandidateState
    capability_match: str
    rank: int


@dataclass
class EvidenceItem:
    source: SourceId
    evidence_type: str
    title: str
    source_ref: str


@dataclass
class EvidenceChain:
    candidate_id: str
    evidence_items: list[EvidenceItem]
    state_rationale: str


@dataclass
class AdviceResult:
    result_id: str
    ranking: list[RankedCandidate]
    overall_decision: OverallDecision
    overall_rationale: str
    evidence_chains: list[EvidenceChain]
    is_recommendation: bool = True


@dataclass
class Feedback:
    result_id: str
    candidate_id: str
    verdict: FeedbackVerdict
    timestamp: datetime


@dataclass(frozen=True)
class ClassificationConfig:
    """C6 순수 로직에 주입되는 임계값 (제약: 0 < extend <= reuse <= 1)."""
    reuse_threshold: float = 0.75
    extend_threshold: float = 0.50
    top_n: int = 3
