// 최종 판정 배너(FR-4.3) — 대형 원형 체크 + 판정 + 태그 + 요약 + AI 요약 답변 박스.
// 판정 색상 팔레트 불변(REUSE=초록 / EXTEND=파랑 / NEEDS REVIEW=앰버 / DEVELOP=보라).
import type { ActionPromptDTO } from '../api/types'
import ActionHandoffTab from './ActionHandoffTab'

interface VerdictBannerProps {
  decision: string
  rationale: string
  isRecommendation: boolean
  topCandidateName: string | null
  topScorePercent: number | null
  handoff: ActionPromptDTO | null
}

interface VerdictMeta {
  headline: string
  tag: string
  icon: string
  variant: string // reuse | extend | review | develop
  summary: (name: string | null) => string
}

const META: Record<string, VerdictMeta> = {
  REUSE: {
    headline: 'REUSE',
    tag: '기존 자산 재사용 추천',
    icon: '✓',
    variant: 'reuse',
    summary: (n) => `기존 ${n ?? '자산'}을(를) 재사용하는 것이 가장 적합합니다.`,
  },
  EXTEND_EXISTING: {
    headline: 'EXTENSION',
    tag: '기존 자산 확장 추천',
    icon: '✓',
    variant: 'extend',
    summary: (n) => `기존 ${n ?? '자산'}을(를) 확장하여 활용하는 것을 추천합니다.`,
  },
  NEEDS_REVIEW: {
    headline: 'NEED REVIEW',
    tag: '추가 검토 필요',
    icon: '!',
    variant: 'review',
    summary: () => '판단을 확정하기 전에 추가 검토가 필요합니다. 후보를 살펴보세요.',
  },
  DEVELOP: {
    headline: 'DEVELOP',
    tag: '신규 개발 권장',
    icon: '+',
    variant: 'develop',
    summary: () => '적합한 기존 자산이 없어 신규 개발을 권장합니다.',
  },
}

export default function VerdictBanner({
  decision,
  rationale,
  isRecommendation,
  topCandidateName,
  topScorePercent,
  handoff,
}: VerdictBannerProps) {
  const meta = META[decision] ?? META.NEEDS_REVIEW
  const showSub =
    (meta.variant === 'reuse' || meta.variant === 'extend') && topScorePercent != null

  return (
    <section className={`verdict verdict--${meta.variant}`} aria-label="최종 판정">
      <div className={`verdict-tagrow c-${meta.variant}`}>
        <span className={`dot bg-${meta.variant}`} aria-hidden="true">
          ✓
        </span>
        최종 판정
        {!isRecommendation && (
          <span className="clarify-hint" style={{ fontWeight: 400 }}>
            (참고용 · 확정 권고 아님)
          </span>
        )}
      </div>

      <div className="verdict-body">
        <span className={`verdict-check bg-${meta.variant}`} aria-hidden="true">
          {meta.icon}
        </span>
        <div className="verdict-main">
          <div className="verdict-headline">
            <span className={`verdict-decision c-${meta.variant}`}>{meta.headline}</span>
            <span className={`badge badge--${meta.variant}`}>{meta.tag}</span>
          </div>
          <p className="verdict-summary">{meta.summary(topCandidateName)}</p>
          {showSub && (
            <p className="verdict-sub">
              요구사항과의 높은 유사성({topScorePercent}%)으로 추가 개발 없이 기존 자산을
              활용할 수 있습니다.
            </p>
          )}

          <div className="ai-answer">
            <p className="ai-answer-label">AI 요약 답변</p>
            <p className="ai-answer-text">{rationale || '요약 정보가 없습니다.'}</p>
          </div>

          <ActionHandoffTab handoff={handoff} />
        </div>
      </div>
    </section>
  )
}
