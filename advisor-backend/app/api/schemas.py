"""API 요청 모델 + **공개 응답 DTO** (§3.2 Type-Enforced Non-Disclosure).

공개 DTO는 내부 도메인 타입을 그대로 노출하지 않는다:
- RankedCandidate DTO에 `evaluationStatus` + nullable `reusabilityScore`는 포함.
- **ExcludedCandidate / 제외 개수·플래그 / technicalFailureReason 필드는 부재**(FR-8/NFR-4/§1.4).
JSON 키는 camelCase(계약). 필드명을 camelCase로 직접 선언한다.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


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


class ActionPromptDTO(BaseModel):
    """CR-001 Action Handoff 공개 DTO. §3.2 계승 — 후보 id·내부 사유 필드 부재(grounding-only)."""
    decisionState: str                  # = overallDecision (INV-HANDOFF-1)
    promptText: str                     # Copy 대상 자연어 Prompt 전문
    targetAssetNames: List[str]         # REUSE/EXTEND의 접근 가능 대상 Asset명; DEVELOP/NEEDS_REVIEW → []


class AdviceResponse(BaseModel):
    resultId: str
    ranking: List[RankedCandidateDTO]
    overallDecision: str
    overallRationale: str
    isRecommendation: bool
    evidenceChains: List[EvidenceChainDTO]
    actionHandoff: Optional[ActionPromptDTO] = None  # CR-001; 생성 실패/부재 시 null(비차단)
    # ⚠️ excludedCount / excludedFlag / excludedCandidates 없음(FR-8/NFR-4)


# ── /feedback ────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    resultId: str = Field(..., min_length=1)
    candidateId: str = Field(..., min_length=1)
    verdict: Literal["useful", "notFit"]

    @field_validator("resultId", "candidateId")
    @classmethod
    def _reject_blank(cls, v: str) -> str:
        """공백만 있는 값 거부 → pydantic이 HTTP 422 반환 (입력 하드닝)."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace-only")
        return stripped


class FeedbackResponse(BaseModel):
    confirmationId: str
