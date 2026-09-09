"""API 요청 모델 + **공개 응답 DTO** (§3.2 Type-Enforced Non-Disclosure).

공개 DTO는 내부 도메인 타입을 그대로 노출하지 않는다:
- RankedCandidate DTO에 `evaluationStatus` + nullable `reusabilityScore`는 포함.
- **ExcludedCandidate / 제외 개수·플래그 / technicalFailureReason 필드는 부재**(FR-8/NFR-4/§1.4).
JSON 키는 camelCase(계약). 필드명을 camelCase로 직접 선언한다.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ── /intent ──────────────────────────────────────────────────────
class IntentRequest(BaseModel):
    rawText: str = Field(..., description="사용자 자연어 요청")


class StructuredIntentDTO(BaseModel):
    role: str
    goal: str
    function: str
    data: str
    output: str


class ClarificationRequestDTO(BaseModel):
    missingFields: List[str]
    questions: List[str]


class IntentResponse(BaseModel):
    """구조화 완료 시 intent, 명료화 필요 시 clarification 중 하나만 채워짐."""
    status: Literal["structured", "clarification"]
    intent: Optional[StructuredIntentDTO] = None
    clarification: Optional[ClarificationRequestDTO] = None


# ── /advise ──────────────────────────────────────────────────────
class PermissionContextDTO(BaseModel):
    userId: str
    role: str


class AdviseRequest(BaseModel):
    intent: StructuredIntentDTO
    context: PermissionContextDTO


class RankedCandidateDTO(BaseModel):
    candidateId: str
    sources: List[str]
    assetName: str
    lifecycleStatus: str
    evaluationStatus: str                       # COMPLETED | UNAVAILABLE (§7.1)
    reusabilityScore: Optional[float] = None    # UNAVAILABLE → null (P11)
    candidateState: str
    capabilityMatch: str
    rank: int
    # ⚠️ technicalFailureReason / 제외 정보 필드 없음(§1.4/§3.2)


class EvidenceItemDTO(BaseModel):
    source: str
    evidenceType: str
    title: str
    sourceRef: str


class EvidenceChainDTO(BaseModel):
    candidateId: str
    evidenceItems: List[EvidenceItemDTO]
    stateRationale: str


class AdviceResponse(BaseModel):
    resultId: str
    ranking: List[RankedCandidateDTO]
    overallDecision: str
    overallRationale: str
    isRecommendation: bool
    evidenceChains: List[EvidenceChainDTO]
    # ⚠️ excludedCount / excludedFlag / excludedCandidates 없음(FR-8/NFR-4)


# ── /feedback ────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    resultId: str
    candidateId: str
    verdict: Literal["useful", "notFit"]


class FeedbackResponse(BaseModel):
    confirmationId: str
