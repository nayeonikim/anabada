import type { IntentPanelProps } from './panel-props'
import type { StructuredIntentDTO } from '../api/types'

const FIELD_LABELS: { key: keyof StructuredIntentDTO; label: string }[] = [
  { key: 'role', label: '역할' },
  { key: 'goal', label: '목표' },
  { key: 'function', label: '기능' },
  { key: 'data', label: '데이터' },
  { key: 'output', label: '산출물' },
]

export default function IntentPanel({
  rawText,
  onRawTextChange,
  onSubmitIntent,
  intentLoading,
  intent,
  onIntentFieldChange,
  clarification,
  context,
  onContextChange,
  roleOptions,
  presets,
  onSelectPreset,
  onAdvise,
  adviseLoading,
  canAdvise,
  error,
}: IntentPanelProps) {
  return (
    <div className="panel">
      <h2 className="panel-title">요청 & 의도</h2>

      <div className="preset-list">
        {presets.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className="btn btn--ghost btn--sm preset-btn"
            onClick={() => onSelectPreset(preset)}
          >
            {preset.label}
            <span className="preset-desc">{preset.description}</span>
          </button>
        ))}
      </div>

      <div className="field-row">
        <div className="field">
          <label className="field-label">사용자 ID</label>
          <input
            className="input"
            value={context.userId}
            onChange={(e) => onContextChange({ ...context, userId: e.target.value })}
          />
        </div>
        <div className="field">
          <label className="field-label">역할</label>
          <select
            className="select"
            value={context.role}
            onChange={(e) => onContextChange({ ...context, role: e.target.value })}
          >
            {roleOptions.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field">
        <label className="field-label">자연어 요청</label>
        <textarea
          className="textarea"
          value={rawText}
          onChange={(e) => onRawTextChange(e.target.value)}
          placeholder="예: 고객 현황을 한 화면에서 보는 대시보드를 만들고 싶어요"
        />
      </div>

      <div className="btn-row">
        <button
          type="button"
          className="btn btn--primary"
          onClick={onSubmitIntent}
          disabled={intentLoading}
        >
          {intentLoading ? '구조화 중…' : '구조화하기'}
        </button>
      </div>

      {error && <div className="alert alert--error">{error}</div>}

      {clarification && (
        <div className="clarify">
          <p>요청 정보가 부족합니다. 아래를 보완해 다시 제출하세요.</p>
          {clarification.missingFields.length > 0 && (
            <p className="panel-hint">누락된 항목: {clarification.missingFields.join(', ')}</p>
          )}
          <ul className="clarify-q">
            {clarification.questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}

      {intent && (
        <div className="section-gap">
          <h3 className="panel-title">구조화된 의도</h3>
          {FIELD_LABELS.map(({ key, label }) => (
            <div className="field" key={key}>
              <label className="field-label">{label}</label>
              <input
                className="input"
                value={intent[key]}
                onChange={(e) => onIntentFieldChange(key, e.target.value)}
              />
            </div>
          ))}
          <div className="btn-row">
            <button
              type="button"
              className="btn btn--primary"
              onClick={onAdvise}
              disabled={!canAdvise || adviseLoading}
            >
              {adviseLoading ? '자문 실행 중…' : '검색 · 자문 실행'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
