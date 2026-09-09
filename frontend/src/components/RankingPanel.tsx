import type { RankingPanelProps } from './panel-props'
import { stateBadge, overallBadge, lifecycleBadge, evaluationLabel } from './badges'

export default function RankingPanel({
  ranking,
  overallDecision,
  overallRationale,
  isRecommendation,
  selectedCandidateId,
  onSelectCandidate,
  hasResult,
  loading,
}: RankingPanelProps) {
  if (loading) {
    return (
      <div className="panel">
        <h2 className="panel-title">후보 랭킹 & 종합 권고</h2>
        <p className="loading">분석 중…</p>
      </div>
    )
  }

  if (!hasResult) {
    return (
      <div className="panel">
        <h2 className="panel-title">후보 랭킹 & 종합 권고</h2>
        <div className="panel-empty">
          요청을 구조화한 뒤 ‘검색 · 자문 실행’을 눌러 주세요.
        </div>
      </div>
    )
  }

  const overall = overallBadge(overallDecision ?? '')

  return (
    <div className="panel">
      <h2 className="panel-title">후보 랭킹 & 종합 권고</h2>

      <div className="overall">
        <div className="overall-head">
          <span className="overall-label">종합 권고</span>
          <span className={overall.className}>{overall.label}</span>
          {!isRecommendation && <span className="panel-hint">(권고 아님)</span>}
        </div>
        <p className="overall-rationale">{overallRationale}</p>
      </div>

      {ranking.length === 0 ? (
        <div className="panel-empty">
          적합한 재사용 후보가 없습니다. 신규 개발(DEVELOP)을 검토하세요.
        </div>
      ) : (
        ranking.map((c) => {
          const state = stateBadge(c.candidateState)
          const lifecycle = lifecycleBadge(c.lifecycleStatus)
          const ev = evaluationLabel(c.evaluationStatus, c.reusabilityScore)
          const selected = c.candidateId === selectedCandidateId
          return (
            <div
              key={c.candidateId}
              className={selected ? 'card card--selected' : 'card'}
              onClick={() => onSelectCandidate(c.candidateId)}
            >
              <div className="card-head">
                <span className="card-rank">#{c.rank}</span>
                <span className="card-title">{c.assetName}</span>
                <span className={state.className}>{state.label}</span>
              </div>
              <div className="card-meta">
                {ev.unavailable ? (
                  <span className="score--unavailable">{ev.label}</span>
                ) : (
                  <span className="score">{ev.label}</span>
                )}
                <span className={lifecycle.className}>{lifecycle.label}</span>
                <span className="capability-match">{c.capabilityMatch}</span>
              </div>
              <div className="chip-row">
                {c.sources.map((s) => (
                  <span key={s} className="source-chip">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}
