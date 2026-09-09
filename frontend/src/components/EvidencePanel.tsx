import type { EvidencePanelProps } from './panel-props'
import { stateBadge, evaluationLabel } from './badges'

export default function EvidencePanel({ candidate, chain }: EvidencePanelProps) {
  if (!candidate) {
    return (
      <div className="panel">
        <h2 className="panel-title">근거 (Evidence Chain)</h2>
        <div className="panel-empty">
          후보를 선택하면 결정 근거와 출처를 확인할 수 있습니다.
        </div>
      </div>
    )
  }

  const state = stateBadge(candidate.candidateState)
  const ev = evaluationLabel(candidate.evaluationStatus, candidate.reusabilityScore)
  const items = chain?.evidenceItems ?? []

  return (
    <div className="panel">
      <h2 className="panel-title">근거 (Evidence Chain)</h2>

      <div className="card-head">
        <span className="card-title">{candidate.assetName}</span>
        <span className={state.className}>{state.label}</span>
      </div>

      <div className="card-meta">
        {ev.unavailable ? (
          <span className="score--unavailable">{ev.label}</span>
        ) : (
          <span className="score">재사용성 {ev.label}</span>
        )}
      </div>

      <div className="rationale">
        {chain?.stateRationale ?? '근거 정보를 불러오는 중입니다.'}
      </div>

      {items.length > 0 ? (
        items.map((item, idx) => (
          <div className="evidence-item" key={idx}>
            <div className="evidence-item-head">
              <span className="evidence-source">{item.source}</span>
              <span className="evidence-type">{item.evidenceType}</span>
            </div>
            <div className="evidence-title">{item.title}</div>
            <div className="evidence-ref">{item.sourceRef}</div>
          </div>
        ))
      ) : (
        <div className="panel-empty">
          평가가 미완료되어 표시할 근거가 없습니다.
        </div>
      )}
    </div>
  )
}
