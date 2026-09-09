import type { FeedbackBarProps } from './panel-props'

export default function FeedbackBar({
  candidate,
  onFeedback,
  confirmationId,
  submitting,
  error,
}: FeedbackBarProps) {
  return (
    <div className="panel">
      <h2 className="panel-title">피드백</h2>
      {!candidate ? (
        <div className="panel-empty">후보를 선택하면 피드백을 남길 수 있습니다.</div>
      ) : (
        <div className="feedback-bar">
          <span className="panel-hint">이 추천이 유용했나요? — {candidate.assetName}</span>
          <button
            type="button"
            className="btn btn--sm"
            onClick={() => onFeedback('useful')}
            disabled={submitting}
          >
            👍 유용함
          </button>
          <button
            type="button"
            className="btn btn--sm"
            onClick={() => onFeedback('notFit')}
            disabled={submitting}
          >
            👎 맞지 않음
          </button>
          {confirmationId && <span className="confirmation">기록됨 · {confirmationId}</span>}
          {error && <span className="error-text">{error}</span>}
        </div>
      )}
    </div>
  )
}
