// 추천 프롬프트(CR-001 US-6.2) — 최종 판정 배너 내 단일 탭.
// Decision 배지 + 대상 자산(있으면) + promptText(pre-wrap) + Copy(성공/실패) + 부재(null) 안내.
import { useState } from 'react'
import type { ActionPromptDTO } from '../api/types'

export default function ActionHandoffTab({ handoff }: { handoff: ActionPromptDTO | null }) {
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'failed'>('idle')

  async function handleCopy() {
    if (!handoff) return
    try {
      await navigator.clipboard.writeText(handoff.promptText)
      setCopyStatus('copied')
    } catch {
      setCopyStatus('failed')
    }
  }

  const note =
    handoff?.decisionState === 'NEEDS_REVIEW'
      ? '판단 확정을 위한 검토용 프롬프트입니다. 후보와 근거를 먼저 검토하세요.'
      : '복사해 외부 AI 도구에 붙여넣어 사용할 수 있습니다.'

  return (
    <div className="handoff">
      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={true}
          aria-controls="handoff-panel"
          id="handoff-tab"
          className="tab tab--active"
        >
          <span aria-hidden="true">✨</span> 추천 프롬프트
        </button>
      </div>

      <div
        className="tab-panel"
        role="tabpanel"
        id="handoff-panel"
        aria-labelledby="handoff-tab"
      >
        {handoff == null ? (
          <p className="handoff-note">
            실행 프롬프트를 생성하지 못했습니다. 위 판단 결과(판정·후보·근거)는 그대로 유효합니다.
          </p>
        ) : (
          <>
            <div className="handoff-meta">
              <span className={`badge badge--${badgeVariant(handoff.decisionState)}`}>
                {handoff.decisionState}
              </span>
              {handoff.targetAssetNames.length > 0 && (
                <span className="handoff-target">
                  대상 자산: {handoff.targetAssetNames.join(' · ')}
                </span>
              )}
            </div>

            <p className="handoff-note">{note}</p>

            <div className="ai-answer">
              <p className="ai-answer-label">추천 프롬프트</p>
              <p className="ai-answer-text">{handoff.promptText}</p>
            </div>

            <div className="handoff-actions">
              <button type="button" className="btn btn--sm" onClick={handleCopy}>
                <span aria-hidden="true">📋</span> 복사
              </button>
              {copyStatus === 'copied' && (
                <span className="confirmation" role="status">
                  복사됨
                </span>
              )}
              {copyStatus === 'failed' && (
                <span className="error-text" role="alert">
                  복사에 실패했습니다. 아래 프롬프트를 직접 선택해 복사해 주세요.
                </span>
              )}
            </div>
          </>
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
