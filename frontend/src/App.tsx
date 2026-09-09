import { useMemo, useState } from 'react'
import { api, ApiError } from './api/client'
import type {
  AdviceResponse,
  ClarificationRequestDTO,
  FeedbackVerdict,
  PermissionContextDTO,
  StructuredIntentDTO,
} from './api/types'
import { DEMO_PRESETS, ROLE_OPTIONS, type DemoPreset } from './demo/presets'
import IntentPanel from './components/IntentPanel'
import RankingPanel from './components/RankingPanel'
import EvidencePanel from './components/EvidencePanel'
import FeedbackBar from './components/FeedbackBar'

const EMPTY_INTENT: StructuredIntentDTO = {
  role: '',
  goal: '',
  function: '',
  data: '',
  output: '',
}

export default function App() {
  // ── 입력 / 구조화 상태 ──────────────────────────────────────────
  const [rawText, setRawText] = useState('')
  const [intent, setIntent] = useState<StructuredIntentDTO | null>(null)
  const [clarification, setClarification] = useState<ClarificationRequestDTO | null>(null)
  const [context, setContext] = useState<PermissionContextDTO>({
    userId: 'demo-user',
    role: 'Sales',
  })
  const [intentLoading, setIntentLoading] = useState(false)

  // ── 자문 결과 상태 ──────────────────────────────────────────────
  const [advice, setAdvice] = useState<AdviceResponse | null>(null)
  const [adviseLoading, setAdviseLoading] = useState(false)
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // ── 피드백 상태 ─────────────────────────────────────────────────
  const [confirmationId, setConfirmationId] = useState<string | null>(null)
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false)
  const [feedbackError, setFeedbackError] = useState<string | null>(null)

  function resetResults() {
    setAdvice(null)
    setSelectedCandidateId(null)
    setConfirmationId(null)
    setFeedbackError(null)
  }

  // ── /intent ─────────────────────────────────────────────────────
  async function handleSubmitIntent() {
    if (!rawText.trim()) {
      setError('요청 내용을 입력하세요.')
      return
    }
    setIntentLoading(true)
    setError(null)
    setIntent(null)
    setClarification(null)
    resetResults()
    try {
      const res = await api.submitIntent(rawText)
      if (res.status === 'structured' && res.intent) {
        setIntent(res.intent)
      } else if (res.status === 'clarification' && res.clarification) {
        setClarification(res.clarification)
      } else {
        setError('요청을 구조화하지 못했습니다. 다시 시도해 주세요.')
      }
    } catch (e) {
      setError(messageOf(e))
    } finally {
      setIntentLoading(false)
    }
  }

  function handleIntentFieldChange(field: keyof StructuredIntentDTO, value: string) {
    setIntent((prev) => ({ ...(prev ?? EMPTY_INTENT), [field]: value }))
  }

  function handleSelectPreset(preset: DemoPreset) {
    setRawText(preset.rawText)
    setContext({ userId: preset.userId, role: preset.role })
    setIntent(null)
    setClarification(null)
    resetResults()
    setError(null)
  }

  // ── /advise ─────────────────────────────────────────────────────
  const canAdvise = useMemo(
    () => intent != null && context.userId.trim() !== '' && context.role.trim() !== '',
    [intent, context],
  )

  async function handleAdvise() {
    if (!intent) return
    setAdviseLoading(true)
    setError(null)
    setConfirmationId(null)
    setFeedbackError(null)
    try {
      const res = await api.advise({ intent, context })
      setAdvice(res)
      // rank 필드가 정렬 순서의 원천 → 배열 위치가 아닌 rank === 1 후보를 선택(폴백: 첫 요소).
      const top = res.ranking.find((c) => c.rank === 1) ?? res.ranking[0]
      setSelectedCandidateId(top?.candidateId ?? null)
    } catch (e) {
      setAdvice(null)
      setSelectedCandidateId(null)
      setError(messageOf(e))
    } finally {
      setAdviseLoading(false)
    }
  }

  // ── /feedback ───────────────────────────────────────────────────
  async function handleFeedback(verdict: FeedbackVerdict) {
    if (!advice || !selectedCandidateId) return
    setFeedbackSubmitting(true)
    setFeedbackError(null)
    try {
      const res = await api.submitFeedback({
        resultId: advice.resultId,
        candidateId: selectedCandidateId,
        verdict,
      })
      setConfirmationId(res.confirmationId)
    } catch (e) {
      setFeedbackError(messageOf(e))
    } finally {
      setFeedbackSubmitting(false)
    }
  }

  // ── 파생 값 ─────────────────────────────────────────────────────
  const selectedCandidate =
    advice?.ranking.find((c) => c.candidateId === selectedCandidateId) ?? null
  const selectedChain =
    advice?.evidenceChains.find((c) => c.candidateId === selectedCandidateId) ?? null

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Rebuild or Reuse Advisor</h1>
        <p className="app-subtitle">
          자연어 요청 → 검색 · 비교 · 결정 · 근거를 한 화면에서
        </p>
      </header>

      <main className="app-grid">
        <section className="col col--intent">
          <IntentPanel
            rawText={rawText}
            onRawTextChange={setRawText}
            onSubmitIntent={handleSubmitIntent}
            intentLoading={intentLoading}
            intent={intent}
            onIntentFieldChange={handleIntentFieldChange}
            clarification={clarification}
            context={context}
            onContextChange={setContext}
            roleOptions={ROLE_OPTIONS}
            presets={DEMO_PRESETS}
            onSelectPreset={handleSelectPreset}
            onAdvise={handleAdvise}
            adviseLoading={adviseLoading}
            canAdvise={canAdvise}
            error={error}
          />
        </section>

        <section className="col col--ranking">
          <RankingPanel
            ranking={advice?.ranking ?? []}
            overallDecision={advice?.overallDecision ?? null}
            overallRationale={advice?.overallRationale ?? ''}
            isRecommendation={advice?.isRecommendation ?? false}
            selectedCandidateId={selectedCandidateId}
            onSelectCandidate={setSelectedCandidateId}
            hasResult={advice != null}
            loading={adviseLoading}
          />
          <FeedbackBar
            candidate={selectedCandidate}
            onFeedback={handleFeedback}
            confirmationId={confirmationId}
            submitting={feedbackSubmitting}
            error={feedbackError}
          />
        </section>

        <section className="col col--evidence">
          <EvidencePanel candidate={selectedCandidate} chain={selectedChain} />
        </section>
      </main>
    </div>
  )
}

function messageOf(e: unknown): string {
  if (e instanceof ApiError) {
    return e.requestId
      ? `${e.message} (${e.code} · ${e.requestId})`
      : `${e.message} (${e.code})`
  }
  return '알 수 없는 오류가 발생했습니다.'
}
