// U1 공개 DTO 미러 (advisor-backend/app/api/schemas.py 와 1:1).
// JSON 키는 camelCase 계약. 미인가/제외 정보 필드는 백엔드에 구조적으로 부재(§3.2) → 여기에도 없음.

// ── enums (advisor-backend/app/domain/models.py) ──────────────────
export type CandidateState = 'REUSE' | 'EXTEND_EXISTING' | 'NEEDS_REVIEW'
export type OverallDecision = 'REUSE' | 'EXTEND_EXISTING' | 'NEEDS_REVIEW' | 'DEVELOP'
export type EvaluationStatus = 'COMPLETED' | 'UNAVAILABLE'
export type LifecycleStatus = 'active' | 'experimental' | 'deprecated' | 'unknown'
export type FeedbackVerdict = 'useful' | 'notFit'

// ── /intent ───────────────────────────────────────────────────────
export interface IntentRequest {
  rawText: string
}

export interface StructuredIntentDTO {
  role: string
  goal: string
  function: string
  data: string
  output: string
}

export interface ClarificationRequestDTO {
  missingFields: string[]
  questions: string[]
}

export interface IntentResponse {
  status: 'structured' | 'clarification'
  intent?: StructuredIntentDTO | null
  clarification?: ClarificationRequestDTO | null
}

// ── /advise ───────────────────────────────────────────────────────
export interface PermissionContextDTO {
  userId: string
  role: string
}

export interface AdviseRequest {
  intent: StructuredIntentDTO
  context: PermissionContextDTO
}

export interface RankedCandidateDTO {
  candidateId: string
  sources: string[]
  assetName: string
  lifecycleStatus: string
  evaluationStatus: string // COMPLETED | UNAVAILABLE
  reusabilityScore?: number | null // UNAVAILABLE → null
  candidateState: string
  capabilityMatch: string
  rank: number
}

export interface EvidenceItemDTO {
  source: string
  evidenceType: string
  title: string
  sourceRef: string
}

export interface EvidenceChainDTO {
  candidateId: string
  evidenceItems: EvidenceItemDTO[]
  stateRationale: string
}

export interface AdviceResponse {
  resultId: string
  ranking: RankedCandidateDTO[]
  overallDecision: string
  overallRationale: string
  isRecommendation: boolean
  evidenceChains: EvidenceChainDTO[]
}

// ── /feedback ─────────────────────────────────────────────────────
export interface FeedbackRequest {
  resultId: string
  candidateId: string
  verdict: FeedbackVerdict
}

export interface FeedbackResponse {
  confirmationId: string
}

// ── 공통 오류 모델 (advisor-backend/app/api/errors.py) ─────────────
// 공개 오류 응답: { error: { code, message, requestId } }
export interface ApiErrorDetail {
  code: string
  message: string
  requestId: string
}

export interface ApiErrorBody {
  error: ApiErrorDetail
}
