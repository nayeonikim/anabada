import { useState } from 'react'
import { api, ApiError } from './api/client'
import type {
  AdviceResponse,
  ClarificationRequestDTO,
  FeedbackVerdict,
  PermissionContextDTO,
} from './api/types'
import { EXAMPLE_PRESETS } from './demo/examples'
import type { DemoPreset } from './demo/presets'
import Header from './components/Header'
import SearchHome from './components/SearchHome'
import ProgressSteps from './components/ProgressSteps'
import VerdictBanner from './components/VerdictBanner'
import CandidateList, { type FeedbackState } from './components/CandidateList'

type View = 'home' | 'result'
// 진행 phase — 실제 호출 경계에 매핑(D3). clarify/error 는 진행바 대신 전용 UI.
type Phase = 'understanding' | 'searching' | 'analyzing' | 'done' | 'clarify' | 'error'

// 로그인 persona 표시(장식). /advise 기능 role 은 아래 context.role(유효 role) 사용.
const ACCOUNT_PERSONA = 'DevRel'

// 향후 SSO 연동 시 이 기본값 대신 로그인 사용자 권한/role 을 주입(단일 지점, D4/NFR-6).
const DEFAULT_CONTEXT: PermissionContextDTO = { userId: 'demo-user', role: 'Sales' }

const EMPTY_FEEDBACK: FeedbackState = {
  submitting: false,
  confirmationId: null,
  confirmedCandidateId: null,
  error: null,
}

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

export default function App() {
  const [view, setView] = useState<View>('home')
  const [question, setQuestion] = useState('')
  const [timestamp, setTimestamp] = useState('')
  const [phase, setPhase] = useState<Phase>('understanding')
  const [percent, setPercent] = useState(0)

  const [clarification, setClarification] = useState<ClarificationRequestDTO | null>(null)
  const [advice, setAdvice] = useState<AdviceResponse | null>(null)
  const [openCandidateId, setOpenCandidateId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<FeedbackState>(EMPTY_FEEDBACK)

  function goHome() {
    setView('home')
    setQuestion('')
    setClarification(null)
    setAdvice(null)
    setOpenCandidateId(null)
    setError(null)
    setFeedback(EMPTY_FEEDBACK)
    setPercent(0)
  }

  // 검색 제출 → /intent → /advise 자동 연속(D2). clarification 시에만 추가 질문 노출.
  async function runSearch(rawText: string, context: PermissionContextDTO) {
    setView('result')
    setQuestion(rawText)
    setTimestamp(formatNow())
    setClarification(null)
    setAdvice(null)
    setOpenCandidateId(null)
    setError(null)
    setFeedback(EMPTY_FEEDBACK)
    setPhase('understanding')
    setPercent(25)

    try {
      const intentRes = await api.submitIntent(rawText)

      if (intentRes.status === 'clarification' && intentRes.clarification) {
        setClarification(intentRes.clarification)
        setPhase('clarify')
        return
      }
      if (intentRes.status !== 'structured' || !intentRes.intent) {
        setError('요청을 구조화하지 못했습니다. 다시 시도해 주세요.')
        setPhase('error')
        return
      }

      const intent = intentRes.intent
      setPhase('searching')
      setPercent(55)
      await delay(500) // 4단계 진행감을 위한 짧은 시각 전이(D3)

      setPhase('analyzing')
      setPercent(90) // /advise 대기 중 90% 유지

      const adv = await api.advise({ intent, context })
      setAdvice(adv)
      const top = adv.ranking.find((c) => c.rank === 1) ?? adv.ranking[0]
      setOpenCandidateId(top?.candidateId ?? null)
      setPercent(100)
      setPhase('done')
    } catch (e) {
      setError(messageOf(e))
      setPhase('error')
    }
  }

  function handlePickExample(preset: DemoPreset) {
    const context: PermissionContextDTO = { userId: preset.userId, role: preset.role }
    void runSearch(preset.rawText, context)
  }

  async function handleFeedback(candidateId: string, verdict: FeedbackVerdict) {
    if (!advice) return
    setFeedback((f) => ({ ...f, submitting: true, error: null }))
    try {
      const res = await api.submitFeedback({ resultId: advice.resultId, candidateId, verdict })
      setFeedback({
        submitting: false,
        confirmationId: res.confirmationId,
        confirmedCandidateId: candidateId,
        error: null,
      })
    } catch (e) {
      setFeedback({
        submitting: false,
        confirmationId: null,
        confirmedCandidateId: null,
        error: messageOf(e),
      })
    }
  }

  const loading = phase === 'understanding' || phase === 'searching' || phase === 'analyzing'
  const topCandidate = advice?.ranking.find((c) => c.rank === 1) ?? advice?.ranking[0] ?? null

  return (
    <div className="app">
      <Header account={ACCOUNT_PERSONA} onBrandClick={goHome} />

      {view === 'home' ? (
        <SearchHome
          examples={EXAMPLE_PRESETS}
          onSearch={(text) => void runSearch(text, DEFAULT_CONTEXT)}
          onPickExample={handlePickExample}
        />
      ) : (
        <main className="result">
          <button type="button" className="back-btn" onClick={goHome}>
            <span aria-hidden="true">←</span> 새 질문하기
          </button>

          <p className="myquestion-label">내 질문</p>
          <div className="myquestion">
            <h1 className="myquestion-text">{question}</h1>
            {timestamp && <span className="myquestion-time">{timestamp}</span>}
          </div>

          {loading && <ProgressSteps activeStep={stepOf(phase)} percent={percent} />}

          {phase === 'clarify' && clarification && (
            <div className="clarify" role="status">
              <p className="clarify-title">요청 정보가 조금 더 필요합니다</p>
              {clarification.missingFields.length > 0 && (
                <p className="clarify-hint">
                  누락된 항목: {clarification.missingFields.join(', ')}
                </p>
              )}
              <ul className="clarify-q">
                {clarification.questions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
              <p className="clarify-hint">
                ‘새 질문하기’로 돌아가 위 내용을 보완해 다시 질문해 주세요.
              </p>
            </div>
          )}

          {phase === 'error' && error && (
            <div className="alert alert--error" role="alert">
              {error}
            </div>
          )}

          {phase === 'done' && advice && (
            <>
              <VerdictBanner
                decision={advice.overallDecision}
                rationale={advice.overallRationale}
                isRecommendation={advice.isRecommendation}
                topCandidateName={topCandidate?.assetName ?? null}
                topScorePercent={scorePercent(topCandidate)}
              />
              <CandidateList
                ranking={advice.ranking}
                chains={advice.evidenceChains}
                openCandidateId={openCandidateId}
                onToggle={(id) =>
                  setOpenCandidateId((cur) => (cur === id ? null : id))
                }
                onFeedback={handleFeedback}
                feedback={feedback}
              />
            </>
          )}
        </main>
      )}
    </div>
  )
}

function stepOf(phase: Phase): number {
  switch (phase) {
    case 'understanding':
      return 0
    case 'searching':
      return 1
    case 'analyzing':
      return 2
    default:
      return 3
  }
}

function scorePercent(c: { evaluationStatus: string; reusabilityScore?: number | null } | null) {
  if (!c || c.evaluationStatus === 'UNAVAILABLE' || c.reusabilityScore == null) return null
  return Math.round(c.reusabilityScore * 100)
}

function formatNow(): string {
  const d = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}. ${hh}:${mm}`
}

function messageOf(e: unknown): string {
  if (e instanceof ApiError) {
    return e.requestId ? `${e.message} (${e.code} · ${e.requestId})` : `${e.message} (${e.code})`
  }
  return '알 수 없는 오류가 발생했습니다.'
}
