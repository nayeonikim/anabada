// AI 진행 스텝바(FR-3) — 4단계 + 진행률. 실제 호출 경계에 매핑(App), % 는 부드러운 애니메이션.
const STEPS = ['질문 이해', '자료 탐색', '후보 분석', '판단 생성']

interface ProgressStepsProps {
  activeStep: number // 0..3 (현재 진행 단계)
  percent: number // 0..100
}

export default function ProgressSteps({ activeStep, percent }: ProgressStepsProps) {
  const allDone = percent >= 100
  return (
    <div className="block" role="status" aria-live="polite">
      <p className="progress-head">AI가 검토하고 있습니다…</p>

      <div className="steps">
        {STEPS.map((label, i) => {
          const done = allDone || i < activeStep
          const active = !allDone && i === activeStep
          const cls = done ? 'step step--done' : active ? 'step step--active' : 'step'
          return (
            <div className="step-group" key={label} style={{ display: 'contents' }}>
              <div className={cls}>
                <span className="step-icon" aria-hidden="true">
                  {done ? '✓' : i + 1}
                </span>
                <span className="step-label">{label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <span className={done ? 'step-line step-line--filled' : 'step-line'} />
              )}
            </div>
          )
        })}
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${Math.min(100, Math.max(0, percent))}%` }} />
      </div>

      <div className="progress-meta">
        <p className="progress-note">
          Confluence, JIRA, 내부 자료를 분석하여 최적의 답을 찾고 있습니다.
        </p>
        <span className="progress-percent">{Math.round(percent)}%</span>
      </div>
    </div>
  )
}
