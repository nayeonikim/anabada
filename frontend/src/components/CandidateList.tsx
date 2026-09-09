// 추천 후보 Top N(FR-4.4/4.5) — 카드(펼침) + 3탭 상세(판단 근거/적합도 분석/참고 자료) + 피드백.
import { useState } from 'react'
import type {
  EvidenceChainDTO,
  FeedbackVerdict,
  RankedCandidateDTO,
} from '../api/types'
import { stateBadge, lifecycleBadge, evaluationLabel } from './badges'

export interface FeedbackState {
  submitting: boolean
  confirmationId: string | null
  confirmedCandidateId: string | null
  error: string | null
}

interface CandidateListProps {
  ranking: RankedCandidateDTO[]
  chains: EvidenceChainDTO[]
  openCandidateId: string | null
  onToggle: (candidateId: string) => void
  onFeedback: (candidateId: string, verdict: FeedbackVerdict) => void
  feedback: FeedbackState
}

export default function CandidateList({
  ranking,
  chains,
  openCandidateId,
  onToggle,
  onFeedback,
  feedback,
}: CandidateListProps) {
  if (ranking.length === 0) {
    return (
      <section className="block">
        <div className="candidates-head">
          <h2 className="candidates-title">추천 후보</h2>
        </div>
        <div className="empty">
          적합한 재사용 후보가 없습니다. 신규 개발(DEVELOP)을 검토하세요.
        </div>
      </section>
    )
  }

  return (
    <section className="block">
      <div className="candidates-head">
        <h2 className="candidates-title">추천 후보 Top {ranking.length}</h2>
        <span className="candidates-sort">적합도 높은 순</span>
      </div>

      {ranking.map((c) => {
        const state = stateBadge(c.candidateState)
        const ev = evaluationLabel(c.evaluationStatus, c.reusabilityScore)
        const open = c.candidateId === openCandidateId
        const chain = chains.find((ch) => ch.candidateId === c.candidateId) ?? null
        const metaline = c.capabilityMatch || c.sources.join(' · ')
        const cls =
          'cand' + (open ? ' cand--open' : '') + (c.rank === 1 ? ' cand--rank1' : '')

        return (
          <div key={c.candidateId} className={cls}>
            <button
              type="button"
              className="cand-row"
              aria-expanded={open}
              onClick={() => onToggle(c.candidateId)}
            >
              <span className="cand-rank">{c.rank}</span>
              <span className="cand-info">
                <span className="cand-name">{c.assetName}</span>
                <span className="cand-metaline">{metaline}</span>
              </span>
              <span className={state.className}>{state.label}</span>
              {ev.unavailable ? (
                <span className="cand-score--na">{ev.label}</span>
              ) : (
                <span className="cand-score" aria-label={`재사용성 점수 ${ev.label}`}>
                  {ev.label}
                </span>
              )}
              <span className="cand-caret" aria-hidden="true">
                ▾
              </span>
            </button>

            {open && (
              <CandidateDetail
                candidate={c}
                chain={chain}
                onFeedback={onFeedback}
                feedback={feedback}
              />
            )}
          </div>
        )
      })}
    </section>
  )
}

type TabKey = 'reason' | 'fit' | 'refs'

function CandidateDetail({
  candidate: c,
  chain,
  onFeedback,
  feedback,
}: {
  candidate: RankedCandidateDTO
  chain: EvidenceChainDTO | null
  onFeedback: (candidateId: string, verdict: FeedbackVerdict) => void
  feedback: FeedbackState
}) {
  const [tab, setTab] = useState<TabKey>('reason')
  const state = stateBadge(c.candidateState)
  const ev = evaluationLabel(c.evaluationStatus, c.reusabilityScore)
  const items = chain?.evidenceItems ?? []
  const confirmed =
    feedback.confirmedCandidateId === c.candidateId ? feedback.confirmationId : null

  return (
    <div className="cand-detail">
      <div className="cand-detail-head">
        <span className={`badge badge--${badgeVariant(c.candidateState)}`}>{state.label}</span>
        <span className="cand-detail-title">{c.assetName}</span>
      </div>

      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'reason'}
          className={tab === 'reason' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('reason')}
        >
          판단 근거
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'fit'}
          className={tab === 'fit' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('fit')}
        >
          적합도 분석
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'refs'}
          className={tab === 'refs' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('refs')}
        >
          참고 자료
        </button>
      </div>

      <div className="tab-panel" role="tabpanel">
        {tab === 'reason' && (
          <>
            <h4>왜 {state.label}로 판단했나요?</h4>
            <p>{chain?.stateRationale ?? '판단 근거 정보가 없습니다.'}</p>
          </>
        )}

        {tab === 'fit' && (
          <div className="fit-grid">
            <div className="fit-item">
              <span className="fit-key">재사용성 점수</span>
              <span className="fit-val">{ev.unavailable ? '평가 미완료' : ev.label}</span>
            </div>
            <div className="fit-item">
              <span className="fit-key">판정</span>
              <span className="fit-val">{state.label}</span>
            </div>
            <div className="fit-item">
              <span className="fit-key">수명주기</span>
              <span className="fit-val">{lifecycleBadge(c.lifecycleStatus).label}</span>
            </div>
            <div className="fit-item">
              <span className="fit-key">평가 상태</span>
              <span className="fit-val">{c.evaluationStatus}</span>
            </div>
            <div className="fit-item" style={{ gridColumn: '1 / -1' }}>
              <span className="fit-key">적합도 요약</span>
              <span className="fit-val">{c.capabilityMatch || '정보 없음'}</span>
            </div>
          </div>
        )}

        {tab === 'refs' &&
          (items.length > 0 ? (
            items.map((item, idx) => (
              <div className="ref-item" key={idx}>
                <div className="ref-item-head">
                  <span className="ref-source">{item.source}</span>
                  <span className="ref-type">{item.evidenceType}</span>
                </div>
                <div className="ref-title">{item.title}</div>
                <div className="ref-ref">{item.sourceRef}</div>
              </div>
            ))
          ) : (
            <p>참고 자료가 없습니다.</p>
          ))}
      </div>

      <div className="feedback">
        <span className="feedback-q">이 추천이 도움이 되었나요?</span>
        <button
          type="button"
          className="btn btn--sm"
          onClick={() => onFeedback(c.candidateId, 'useful')}
          disabled={feedback.submitting}
          aria-busy={feedback.submitting}
        >
          <span aria-hidden="true">👍</span> 유용함
        </button>
        <button
          type="button"
          className="btn btn--sm"
          onClick={() => onFeedback(c.candidateId, 'notFit')}
          disabled={feedback.submitting}
          aria-busy={feedback.submitting}
        >
          <span aria-hidden="true">👎</span> 맞지 않음
        </button>
        {confirmed && (
          <span className="confirmation" role="status">
            기록됨 · {confirmed}
          </span>
        )}
        {feedback.error && feedback.confirmedCandidateId == null && (
          <span className="error-text" role="alert">
            {feedback.error}
          </span>
        )}
      </div>
    </div>
  )
}

function badgeVariant(state: string): string {
  switch (state) {
    case 'REUSE':
      return 'reuse'
    case 'EXTEND_EXISTING':
      return 'extend'
    case 'NEEDS_REVIEW':
      return 'review'
    case 'DEVELOP':
      return 'develop'
    default:
      return 'review'
  }
}
