// U1 demo_fixtures(structure) 에서 추출한 정확한 rawText 프리셋(자동 생성, 손수 편집 금지).
// demoMode ON일 때 결정적 fixture 응답을 유도. rawText가 fixture 키와 정확히 일치해야 함.

export interface DemoPreset {
  id: string
  label: string
  description: string
  rawText: string
  role: string
  userId: string
}

export const DEMO_PRESETS: DemoPreset[] = [
  {
    id: "hero",
    label: "Hero - 재사용(REUSE)",
    description: "Sales가 Customer 360 대시보드 요청 -> asset-001 REUSE",
    rawText: "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요",
    role: "Sales",
    userId: "demo-user",
  },
  {
    id: "needs-review",
    label: "Unhappy - 검토 필요(NEEDS REVIEW)",
    description: "Developer가 legacy 공통 라이브러리 요청 -> deprecated asset-007 근거부족",
    rawText: "예전 프로젝트에서 쓰던 공통 기능 라이브러리를 재사용하고 싶어요",
    role: "Developer",
    userId: "demo-user",
  },
  {
    id: "develop",
    label: "Unhappy - 신규 개발(DEVELOP)",
    description: "Sales가 릴리스 자동화 스크립트 요청 -> 적합 자산 없음",
    rawText: "릴리스 버전 체크와 아티팩트 검증을 자동화하는 스크립트가 필요해요",
    role: "Sales",
    userId: "demo-user",
  },
  {
    id: "clarify",
    label: "Unhappy - 명료화(CLARIFY)",
    description: "불완전 요청 -> 명료화 질문(role/data 누락)",
    rawText: "대시보드 하나 만들어줘",
    role: "Sales",
    userId: "demo-user",
  },
]

export const ROLE_OPTIONS: string[] = ["Sales", "Developer", "Sales / Marketing"]
