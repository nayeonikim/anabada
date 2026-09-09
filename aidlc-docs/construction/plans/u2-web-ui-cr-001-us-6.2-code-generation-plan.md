# U2 Web UI — CR-001 US-6.2 Action Handoff 표시·Copy 코드 생성 계획 (탭 기반, 정합화 완료)

> **정합화 완료 (2026-09-09)**: U2 UI Design(`CR-001-u2-ui-design.md`) **APPROVED** + 열린 결정(Q-TARGET/Q-NULL/Q-LABEL/Q-TEST) 확정 후 본 계획을 확정 설계에 맞춰 정합화했다.
> 확정 배치 = **최종 판정 배너 내 `✨ 추천 프롬프트` 단일 탭**(초안의 하단 `ActionHandoffPanel` 배치는 폐기).

**Status**: Part 2 완료 — 빌드 PASS(tsc strict 0, vite 41 modules +1) + AC 10항목 검증 PASS. 스테이지 승인 게이트 대기.
**Unit**: U2 Web UI (frontend) · **Story**: US-6.2 (Action Prompt 표시 & Copy) · **Depends on**: US-6.1 백엔드 계약(기 구현)
**Design**: `aidlc-docs/change-requests/CR-001-u2-ui-design.md` (authoritative)
**원칙**: append-only 소비, 신규 config/의존성/테스트 프레임워크 0, 기존 시각 언어·a11y 패턴 재사용, 최소 증분.

---

## 0. 확정된 열린 결정 (설계 입력)

| Q | 확정 | 구현 반영 |
|---|---|---|
| **Q-TARGET** | 대상 자산 표시, **빈 배열이면 숨김** | `targetAssetNames.length > 0`일 때만 `.handoff-target` 렌더 |
| **Q-NULL** | **탭 내부 안내**, 판정·근거 유지 | null이어도 탭 스트립 유지 + 패널 안 `.handoff-note` 부재 안내 |
| **Q-LABEL** | 탭 제목 `✨ 추천 프롬프트` 통일 · 내부 라벨 '추천 프롬프트' · NEEDS_REVIEW는 검토용 명시 · **개발 실행 유도 문구 금지** | 아래 S2 note 로직 |
| **Q-TEST** | 신규 하네스 생략, build/tsc + 스모크(Decision 4종·Copy 성공/실패·null·모바일·키보드) | S6 검증 |

---

## 1. 주 에이전트 확정 계약 (LOCKED — 하위 에이전트 준수)

### 타입 (types.ts) — 백엔드 `schemas.py:77-91` camelCase 1:1
```ts
export interface ActionPromptDTO {
  decisionState: string        // = overallDecision (REUSE | EXTEND_EXISTING | NEEDS_REVIEW | DEVELOP)
  promptText: string           // Copy 대상 자연어 Prompt 전문(다행, \n 포함)
  targetAssetNames: string[]   // REUSE/EXTEND 대상 Asset명; 없으면 [] (비어있으면 숨김)
}
// AdviceResponse 에 추가:
//   actionHandoff?: ActionPromptDTO | null   // CR-001; 생성 실패/부재 시 null(비차단)
```

### 컴포넌트 계약
- `frontend/src/components/ActionHandoffTab.tsx` — **default export** `ActionHandoffTab`, props `{ handoff: ActionPromptDTO | null }`.
- `VerdictBanner` 는 `import ActionHandoffTab from './ActionHandoffTab'` 후 `.ai-answer` **다음**에 `<ActionHandoffTab handoff={handoff} />` 렌더.
- `App` 은 `<VerdictBanner ... handoff={advice.actionHandoff ?? null} />`.

### 공통 CSS (주 에이전트가 이미 추가 — 하위 에이전트 수정 금지)
`.handoff` / `.handoff .tabs` / `.handoff-meta` / `.handoff-target` / `.handoff-note` / `.handoff-actions` (+ `@media ≤720` 정렬). 그 외 `.tabs`/`.tab`/`.tab--active`/`.tab-panel`/`.ai-answer`/`.ai-answer-text`/`.badge badge--{variant}`/`.btn btn--sm`/`.confirmation`/`.error-text`/`:focus-visible` 는 기존 재사용.

---

## 2. 병렬 담당 & 파일 소유권 (동일 파일 동시수정 금지)

| 담당 | 파일(소유) | 내용 |
|---|---|---|
| **주 에이전트** | `styles.css`, `aidlc-state.md`, `audit.md`, 본 계획/설계 문서 | 계약 락 + 공통 CSS + state/audit/문서 갱신. 통합·commit·push. |
| **Agent 1** | `frontend/src/components/ActionHandoffTab.tsx` (**신규**) | UI 컴포넌트·Copy·부재 상태·접근성 (아래 S2). |
| **Agent 2** | `frontend/src/api/types.ts`, `frontend/src/components/VerdictBanner.tsx`, `frontend/src/App.tsx` | API 타입·prop 전달·배치 연결 (아래 S1/S3/S4). |
| **Agent 3** | (읽기 전용 + 빌드) | 승인 AC 기반 검증 준비 → 통합 후 스모크 검증 (아래 S6). |

> 하위 에이전트는 commit/push/rebase 금지. 소유 파일 외 편집 금지.

---

## 3. 실행 체크리스트

- [x] **S1. 타입 추가 (Agent 2)** — `types.ts`: 위 §1 계약대로 `ActionPromptDTO` + `AdviceResponse.actionHandoff` 추가.

- [x] **S2. 신규 컴포넌트 (Agent 1)** — `frontend/src/components/ActionHandoffTab.tsx`
  - Props `{ handoff: ActionPromptDTO | null }`. Copy 상태 로컬 `useState<'idle'|'copied'|'failed'>`.
  - 로컬 `badgeVariant(state)` 맵(reuse/extend/review/develop, default review — `CandidateList.tsx:246-259`와 동일 4줄).
  - 루트 `<div className="handoff">` → 항상 `.tabs`(role=tablist) + 단일 `.tab tab--active`(role=tab, aria-selected, id=handoff-tab, aria-controls=handoff-panel) `✨ 추천 프롬프트` + `.tab-panel`(role=tabpanel, id=handoff-panel, aria-labelledby=handoff-tab).
  - `handoff == null` → 패널 안 `.handoff-note` "실행 프롬프트를 생성하지 못했습니다. 위 판단 결과(판정·후보·근거)는 그대로 유효합니다."
  - `handoff != null` → `.handoff-meta`(badge `badge--{variant}` = decisionState + `targetAssetNames.length>0`일 때만 `.handoff-target` "대상 자산: …") → `.handoff-note`(NEEDS_REVIEW: "판단 확정을 위한 검토용 프롬프트입니다. 후보와 근거를 먼저 검토하세요." / else: "복사해 외부 AI 도구에 붙여넣어 사용할 수 있습니다.") → `.ai-answer`(label '추천 프롬프트' + `.ai-answer-text` pre-wrap promptText) → `.handoff-actions`(`.btn btn--sm` 📋 복사 + 상태).
  - Copy: `navigator.clipboard.writeText(handoff.promptText)` → `copied`(`.confirmation` role=status "복사됨") / catch → `failed`(`.error-text` role=alert 실패+수동 선택 안내). 이모지 `aria-hidden`.
  - **개발 실행 유도(명령형 CTA) 문구 금지.**

- [x] **S3. VerdictBanner 배선 (Agent 2)** — `VerdictBanner.tsx`: props에 `handoff: ActionPromptDTO | null` 추가, `import ActionHandoffTab from './ActionHandoffTab'` + `import type { ActionPromptDTO } from '../api/types'`, `.ai-answer` 블록 다음(`verdict-main` 내부)에 `<ActionHandoffTab handoff={handoff} />` 렌더. 그 외 로직 무변경.

- [x] **S4. App 배선 (Agent 2)** — `App.tsx`: `<VerdictBanner ... />`(185-193)에 `handoff={advice.actionHandoff ?? null}` prop 추가. 신규 import 불필요.

- [x] **S5. 데모 확인(변경 없음)** — `demo_fixtures.json` 3 시나리오(REUSE/NEEDS_REVIEW/DEVELOP) 기 존재 → fixture 편집 불필요.

- [x] **S6. 검증 (Agent 3 + 주 에이전트 통합)**
  - `cd frontend && npm run build` → tsc strict 0 오류 + vite build 성공(모듈 +2 예상: ActionHandoffTab).
  - 스모크(코드/픽스처 기반): Decision 4종 배지·note 분기, Copy 성공/실패 상태, null 탭 내부 안내, 모바일(≤720 flex-wrap/column), 키보드(.tab/.btn `:focus-visible`, role 시맨틱).

- [x] **S7. code-summary (주 에이전트)** — `aidlc-docs/construction/u2-web-ui/code/` 하위에 US-6.2 요약(변경 파일·검증 결과) 추가.

---

## 4. 검증 기준 (US-6.2 AC ↔ 구현 매핑)

| AC | 구현 | 검증 |
|---|---|---|
| Prompt 표시 + 어떤 Decision인지 자기설명 | `.ai-answer-text` + `badge badge--{variant}`(decisionState) | 데모 4종 렌더 |
| 전체 Prompt Copy + "복사됨" | `clipboard.writeText` + `.confirmation role=status` | 스모크 클릭 |
| Copy 실패 알림 + 수동 대안 | catch → `.error-text role=alert` + 선택 가능 텍스트 | 코드 리뷰 |
| Prompt 부재 시 판단 결과 유지 + 부재 안내 | App이 Verdict/Candidate 독립 렌더 + 탭 내부 `.handoff-note` | null 스모크 |
| 비노출(NFR-8) | 받은 3필드만 표시 | 계약상 자동 충족 |

---

## 5. 남은 AI-DLC 승인 게이트
1. **U2 Code Generation(증분) 스테이지 완료 게이트** — 통합 + 빌드/스모크 후 표준 2옵션.
2. **Build and Test 게이트** — 제품 전체 회귀 포함.
