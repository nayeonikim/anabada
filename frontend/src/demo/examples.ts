// 검색 홈 예시 질문 칩. 목업의 시각 구조(pill + 화살표 + '예시 질문' 헤딩)를 따르되,
// demoMode가 결정적으로 동작하려면 rawText가 fixture 키와 정확히 일치해야 하므로(백엔드 out-of-scope)
// 칩은 실제 DEMO_PRESETS(rawText + role)를 사용한다. 클릭 시 해당 질문으로 자동 분석 실행.
import { DEMO_PRESETS, type DemoPreset } from './presets'

function byId(id: string): DemoPreset {
  const p = DEMO_PRESETS.find((x) => x.id === id)
  if (!p) throw new Error(`unknown preset: ${id}`)
  return p
}

// hero=REUSE, needs-review=검토 필요, develop=신규 개발 — 대표 3종.
export const EXAMPLE_PRESETS: DemoPreset[] = [
  byId('hero'),
  byId('needs-review'),
  byId('develop'),
]
