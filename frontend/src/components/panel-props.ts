// 4개 presentational 패널의 props 계약. App(상태 소유)과 각 패널이 공유.
// 패널은 상태를 소유하지 않는다(순수 presentational + 콜백).
import type {
  ClarificationRequestDTO,
  EvidenceChainDTO,
  FeedbackVerdict,
  PermissionContextDTO,
  RankedCandidateDTO,
  StructuredIntentDTO,
} from '../api/types'
import type { DemoPreset } from '../demo/presets'

// ── IntentPanel (US-1.1 입력 / US-1.2 구조 표시·확인 / US-1.3 명료화) ──
export interface IntentPanelProps {
  rawText: string
  onRawTextChange: (value: string) => void
  onSubmitIntent: () => void
  intentLoading: boolean

  // 구조화 결과(편집 가능한 5필드). null이면 아직 구조화 전.
  intent: StructuredIntentDTO | null
  onIntentFieldChange: (field: keyof StructuredIntentDTO, value: string) => void

  // 명료화 필요 시 채워짐(누락 필드 + 질문).
  clarification: ClarificationRequestDTO | null

  // 권한 컨텍스트(/advise 에 전달).
  context: PermissionContextDTO
  onContextChange: (context: PermissionContextDTO) => void
  roleOptions: string[]

  // 데모 프리셋(정확한 rawText + role 프리필).
  presets: DemoPreset[]
  onSelectPreset: (preset: DemoPreset) => void

  // 검색/자문 실행(POST /advise).
  onAdvise: () => void
  adviseLoading: boolean
  canAdvise: boolean

  error: string | null
}

// ── RankingPanel (US-4.1 후보 랭킹 + Overall Decision) ────────────
export interface RankingPanelProps {
  ranking: RankedCandidateDTO[]
  overallDecision: string | null
  overallRationale: string
  isRecommendation: boolean
  selectedCandidateId: string | null
  onSelectCandidate: (candidateId: string) => void
  hasResult: boolean
  loading: boolean
}

// ── EvidencePanel (US-4.2 선택 후보 Evidence chain) ───────────────
export interface EvidencePanelProps {
  candidate: RankedCandidateDTO | null
  chain: EvidenceChainDTO | null
}

// ── FeedbackBar (US-4.3 피드백 입력) ──────────────────────────────
export interface FeedbackBarProps {
  candidate: RankedCandidateDTO | null
  onFeedback: (verdict: FeedbackVerdict) => void
  confirmationId: string | null
  submitting: boolean
  error: string | null
}
