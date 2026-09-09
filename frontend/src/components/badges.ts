// enum → 배지 표시(label + CSS 클래스) 매핑. 모든 패널이 공유해 일관된 시각 표현을 보장.
// CSS 클래스는 styles.css 에 정의됨(.badge, .badge--*).

export function stateBadge(state: string): { label: string; className: string } {
  switch (state) {
    case 'REUSE':
      return { label: '재사용 (REUSE)', className: 'badge badge--reuse' }
    case 'EXTEND_EXISTING':
      return { label: '확장 (EXTEND)', className: 'badge badge--extend' }
    case 'NEEDS_REVIEW':
      return { label: '검토 필요 (NEEDS REVIEW)', className: 'badge badge--review' }
    default:
      return { label: state, className: 'badge' }
  }
}

export function overallBadge(decision: string): { label: string; className: string } {
  // REUSE/EXTEND_EXISTING/NEEDS_REVIEW 는 stateBadge 와 동일 → 위임하고 DEVELOP 만 특수 처리.
  if (decision === 'DEVELOP') {
    return { label: '신규 개발 (DEVELOP)', className: 'badge badge--develop' }
  }
  return stateBadge(decision)
}

export function lifecycleBadge(status: string): { label: string; className: string } {
  const map: Record<string, string> = {
    active: 'badge badge--lifecycle-active',
    experimental: 'badge badge--lifecycle-experimental',
    deprecated: 'badge badge--lifecycle-deprecated',
    unknown: 'badge badge--lifecycle-unknown',
  }
  return { label: status, className: map[status] ?? 'badge badge--lifecycle-unknown' }
}

/** COMPLETED는 점수 표시, UNAVAILABLE은 '평가 미완료'. */
export function evaluationLabel(
  evaluationStatus: string,
  reusabilityScore?: number | null,
): { label: string; unavailable: boolean } {
  if (evaluationStatus === 'UNAVAILABLE' || reusabilityScore == null) {
    return { label: '평가 미완료', unavailable: true }
  }
  return { label: `${Math.round(reusabilityScore * 100)}%`, unavailable: false }
}
