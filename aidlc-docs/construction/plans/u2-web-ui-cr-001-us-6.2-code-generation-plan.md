# U2 Web UI — CR-001 US-6.2 Action Handoff 표시·Copy 코드 생성 계획

> **⚠️ 정합화 대기**: 본 계획은 **U2 UI Design(`CR-001-u2-ui-design.md`) 승인 후 정합화**된다. 초안(S1~S7)은 하단 별도 `ActionHandoffPanel` 배치를 전제했으나, **확정 설계는 최종 판정 배너 내 `✨ 추천 프롬프트` 단일 탭**이다. 정합화 시: S2 컴포넌트명 `ActionHandoffTab`(배너 내부 렌더), S3는 App 하단 배선 대신 `VerdictBanner`에 `handoff` prop 전달 + 배너 내 렌더로 교체, S4 스타일은 `.tabs`/`.tab`/`.tab-panel` 재사용 추가. 그 외(S1 types·S5 fixtures·S6 build·S7 summary)는 유지.

**Status**: DRAFT — UI Design 승인 후 정합화 예정 (PLAN ONLY, 실행 미착수)
**Unit**: U2 Web UI (frontend) · **Story**: US-6.2 (Action Prompt 표시 & Copy) · **Depends on**: US-6.1 백엔드 계약(기 구현)
**Design**: `aidlc-docs/change-requests/CR-001-u2-action-handoff-design-delta.md`
**원칙**: append-only 소비, 신규 config/의존성 0, 기존 시각 언어·a11y 패턴 재사용, 최소 증분.

---

## Part 1 — 실행 체크리스트 (승인 후 순서대로)

- [ ] **S1. 타입 추가** — `frontend/src/api/types.ts`
  - `ActionPromptDTO` 인터페이스 추가(`decisionState: string`, `promptText: string`, `targetAssetNames: string[]`).
  - `AdviceResponse`에 `actionHandoff?: ActionPromptDTO | null` 추가(camelCase, 백엔드 `schemas.py:77-91` 1:1 미러). 주석: CR-001, 실패/부재 시 null(비차단).

- [ ] **S2. 신규 컴포넌트** — `frontend/src/components/ActionHandoffPanel.tsx`
  - Props `{ handoff: ActionPromptDTO | null }`.
  - `handoff == null` → 부재 안내 `.block` 1줄 렌더(D3).
  - 값 존재 → `.block` 섹션: 제목 "다음 행동 · 실행 Prompt" + `badge badge--{variant}`(Decision 자기설명, 로컬 variant 맵) + `.ai-answer`/`.ai-answer-text`(pre-wrap) promptText 박스 + `targetAssetNames` 1줄(선택, Q2 확정 시).
  - Copy: 로컬 `useState<'idle'|'copied'|'failed'>`, `navigator.clipboard.writeText(handoff.promptText)`; 성공 → `.confirmation role="status"` "복사됨", 실패 → `.error-text role="alert"` + 수동 선택 안내(D5).
  - `<button className="btn btn--sm">` 재사용(포커스 아웃라인 기존 규칙 적용).

- [ ] **S3. App 결과 화면 배선** — `frontend/src/App.tsx`
  - `import ActionHandoffPanel from './components/ActionHandoffPanel'` 및 `ActionPromptDTO` 타입 import(필요 시).
  - `phase === 'done' && advice` 프래그먼트(`App.tsx:185-205`)에서 `<CandidateList/>` **뒤**에 `<ActionHandoffPanel handoff={advice.actionHandoff ?? null} />` 추가(D1).

- [ ] **S4. 스타일** — `frontend/src/styles.css`
  - 원칙: 기존 `.block`/`.ai-answer`/`.ai-answer-text`/`.badge`/`.btn`/`.confirmation`/`.error-text` 재사용.
  - 필요 시에만 소형 규칙 최대 1개(예: Copy 버튼 + 상태 배지 정렬용 `.handoff-actions { display:flex; gap:12px; align-items:center; margin-top:14px; }`). 신규 토큰/색상 추가 금지.

- [ ] **S5. 데모 확인(변경 없음 예상)** — `advisor-backend/data/demo_fixtures.json`
  - hero fixture가 이미 `actionHandoff`(REUSE, Customer 360 Dashboard) 포함 확인됨 → **fixture 편집 불필요**. needs-review/develop 프리셋의 actionHandoff 유무만 데모 스모크에서 관찰(부재 시 D3 안내 경로 자연 검증).

- [ ] **S6. 빌드·타입 검사 검증**
  - `cd frontend && npm run build` → tsc strict 0 오류 + vite build 성공(모듈 수 +1 예상).
  - (선택) demoMode ON 스모크: hero → 결과 하단에 Prompt 패널 + Copy "복사됨" 노출, null 경로 안내 문구 확인.

- [ ] **S7. code-summary 작성** — `aidlc-docs/construction/u2-web-ui/code/` 하위에 US-6.2 요약(변경 파일·검증 결과) 추가(신규 파일, 기존 요약 미수정).

---

## Part 2 — 검증 기준 (US-6.2 AC ↔ 구현 매핑)

| AC | 구현 | 검증 |
|---|---|---|
| Prompt 표시 + 어떤 Decision인지 자기설명 | `.ai-answer-text` 박스 + `badge badge--{variant}` | 데모 hero 렌더 |
| 전체 Prompt Copy + "복사됨" 알림 | `clipboard.writeText` + `.confirmation role=status` | 스모크 클릭 |
| Copy 실패 알림 + 수동 대안 | catch → `.error-text role=alert` + 선택 가능 텍스트 | 코드 리뷰(브라우저 거부 재현은 데모 범위 밖) |
| Prompt 부재 시 판단 결과 유지 + 부재 안내 | App이 Verdict/Candidate 독립 렌더 + Panel의 null 안내 | null 경로 스모크 |
| 비노출(NFR-8) | 받은 3필드만 표시(추가 필드 없음) | 계약상 자동 충족 |

---

## Part 3 — 오픈 이슈 (승인 시 결정)

- **Q1 (배치)**: Action Handoff 패널을 **CandidateList 다음(하단, 권장)** vs VerdictBanner 바로 아래 중 어디에? — 권장: 하단("판단→행동" 흐름).
- **Q2 (대상 자산 줄)**: `targetAssetNames`를 별도 1줄로 표시할지 여부(표시 안 해도 AC 충족). — 권장: 표시(최소 유용성).
- **Q3 (테스트 범위)**: frontend는 현재 유닛 테스트 하네스 없음 → 검증을 tsc+build+데모 스모크로 한정(NFR-minimization 준수)할지 확인. — 권장: 예.
