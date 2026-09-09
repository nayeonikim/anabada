# CR-001 — U2 Action Handoff 표시·Copy 설계 델타 (US-6.2)

> **⚠️ SUPERSEDED (부분) — 초안 입력용**: 배치·표현의 authoritative 문서는 **`CR-001-u2-ui-design.md`(U2 UI Design 단계 산출물)** 이다.
> 본 문서의 **D1(결과 화면 하단 별도 `ActionHandoffPanel`)** 은 UI Design의 **탭 기반 배치**(최종 판정 배너 내 `✨ 추천 프롬프트` 단일 탭)로 대체됨(사용자 승인 2026-09-09).
> 계약 소비(§2)·null 처리(D3)·기존 시각언어/a11y 재사용(§3~§5)은 재사용된다. 남은 내용은 초안 참고용으로 보존.

**Status**: DRAFT INPUT — UI Design(`CR-001-u2-ui-design.md`)으로 승계됨. 단독 승인 대상 아님.
**Scope**: U2 Web UI frontend only. append-only 소비 — 기존 파이프라인/DTO/컴포넌트 계약 무변경.
**Base**: `integration/action-handoff-on-main` @ 최신 origin/main(`e4111ef`, Anabada 검색형 라이트 UI) 위 CR-001 백엔드 통합.
**근거**: US-6.2 (FR-12), US-6.1(생성) 계약 소비, NFR-8(비노출) 계승, NFR-minimization(신규 config/의존성 없음).

---

## 1. 승인된 US-6.2 Acceptance Criteria (원문, `stories.md:168-175`)

> ### US-6.2 Action Prompt 표시 & Copy [MVP] · Hero
> - **As a** 사용자(P1/P2), **I want** 생성된 Action Prompt를 결과 화면에서 보고 복사하고 싶다, **so that** 외부 AI 개발 도구에 바로 붙여넣어 쓴다. (FR-12)
> - Given Advisor 결과에 Action Prompt가 포함되면, When 결과 화면을 열면, Then Action Prompt를 표시하고 **어떤 Overall Decision에 대한 것인지** 자기설명적으로 드러낸다. (NFR-1 / NFR-6)
> - Given 표시된 Prompt, When Copy를 실행하면, Then 전체 Prompt를 클립보드에 복사하고 **복사 성공을 사용자에게 알린다("복사됨")**.
> - Given Copy가 실패하면(예: 클립보드 접근 거부), Then **복사 실패를 알리고** 사용자가 수동으로 선택·복사할 수 있는 대안을 제공한다.
> - Given Action Prompt가 결과에 없으면(생성 실패 등), Then 기존 판단 결과(랭킹·Decision·Evidence)는 그대로 표시하고 **Action Prompt 부재만 안내**한다.
> - **비고**: U1→U2 계약은 Advisor 결과의 Action Prompt를 소비. 구체 API 경로·필드명은 Application Design에서 확정하며, 본 AC는 특정 경로·필드를 전제하지 않는다.

---

## 2. 소비할 백엔드 계약 (기 구현, 무변경)

`advisor-backend/app/api/schemas.py:77-91` — `AdviceResponse.actionHandoff: Optional[ActionPromptDTO]`:

| 필드 | 타입 | 의미 |
|---|---|---|
| `decisionState` | `str` | = overallDecision (REUSE / EXTEND_EXISTING / NEEDS_REVIEW / DEVELOP). "어떤 판단에 대한 Prompt인지" 자기설명 근거 |
| `promptText` | `str` | Copy 대상 자연어 Prompt 전문(다행, `\n` 포함) |
| `targetAssetNames` | `string[]` | REUSE/EXTEND의 접근 가능 대상 Asset명; DEVELOP/NEEDS_REVIEW → `[]` |

- **null 조건**: 생성 실패(정합 가드 위반·LLM 오류/타임아웃)에만 `actionHandoff = null` — 비차단(`orchestrator.py:136-149`, `main.py:230-236`). 4개 Decision 모두 정상 시 값 존재.
- **비노출(NFR-8)**: 페이로드는 이미 공개 투영이라 미인가 자산·technicalFailureReason·제외 개수가 구조적으로 유입 불가 → U2는 받은 필드를 **그대로 표시만** 하면 계약 충족(추가 필터링 불필요).
- **demoMode 검증됨**: hero 프리셋(`고객의 Project, Forecast, Risk…`) → `actionHandoff={decisionState:"REUSE", promptText:<다행>, targetAssetNames:["Customer 360 Dashboard"]}` (`demo_fixtures.json:108`). **데모 시연 시 실제 Prompt가 렌더됨 → fixture 변경 불필요.**

---

## 3. 최신 UI 접점 (실제 파일 앵커)

- 결과 화면 렌더 지점: `App.tsx:185-205` — `phase === 'done' && advice` 블록에서 `<VerdictBanner/>` 다음 `<CandidateList/>` 렌더. **여기에 Action Handoff를 append**.
- 상태 모델: `App.tsx:36-47` — `advice: AdviceResponse | null`. `actionHandoff`는 `advice.actionHandoff`로 접근(타입 추가만 필요).
- 재사용 가능한 시각 언어(무변경 참조):
  - `.block` (`styles.css:330`) — 결과 섹션 카드 래퍼 (VerdictBanner/CandidateList와 동일 리듬).
  - `.ai-answer` / `.ai-answer-text` (`styles.css:543-563`) — 테두리 박스 + `white-space: pre-wrap` (다행 promptText에 그대로 적합).
  - `.badge badge--{reuse|extend|review|develop}` (`styles.css:853-885`) — Decision 자기설명 태그.
  - `.btn` / `.btn--sm` (`styles.css:904-925`) — Copy 버튼 (피드백 버튼과 동일 스타일).
  - `.confirmation` (`styles.css:846`, `role="status"`) — "복사됨" 성공 알림 (CandidateList 피드백 `confirmation` 패턴과 동일: `CandidateList.tsx:231-235`).
  - `.error-text` (`role="alert"`) — 복사 실패 알림 (피드백 오류 패턴과 동일: `CandidateList.tsx:236-240`).
  - `:focus-visible` 아웃라인은 `.btn`에 이미 적용(`styles.css:991`) → Copy 버튼 키보드 포커스 자동 충족.

---

## 4. 설계 결정 (최소 증분)

### D1. 배치 — VerdictBanner·CandidateList **다음**(결과 화면 하단)
Epic 6 목적("재사용 판단 → 다음 행동")과 흐름상, 판정·후보 검토를 마친 뒤 "다음 행동" 단계로 배치. `App.tsx`의 `phase==='done'` 프래그먼트에서 `<CandidateList/>` 뒤에 `<ActionHandoffPanel/>` 추가. **(→ 오픈 이슈 Q1: VerdictBanner 바로 아래 배치 대안)**

### D2. 신규 컴포넌트 1개 — `frontend/src/components/ActionHandoffPanel.tsx`
VerdictBanner/CandidateList와 동일한 "작은 프레젠테이셔널 컴포넌트" 패턴. 기존 컴포넌트 확장 대신 신규 1개가 관심사 분리·리스크 최소.
- Props: `{ handoff: ActionPromptDTO | null }` (단일 prop, App은 `advice.actionHandoff` 전달).
- Copy 상태는 **컴포넌트 로컬** `useState<'idle'|'copied'|'failed'>` — App 전역 상태 오염 없음(피드백과 달리 서버 왕복 없음).
- Decision→variant 매핑은 `CandidateList.tsx:246-259 badgeVariant`와 동일한 소형 로컬 맵(공유 리팩터링은 증분 확대 → 지양, 4줄 중복 허용).

### D3. null 처리 — 부재 안내(AC 5)
`handoff == null` → **아무것도 안 하지 않고**, 최소 안내 1줄 렌더: "실행 Prompt를 생성하지 못했습니다. 위 판단 결과(판정·후보·근거)는 그대로 유효합니다." (`.block` + 흐린 텍스트). 판단 결과 렌더(VerdictBanner/CandidateList)는 App에서 이미 독립적으로 표시되므로 비차단 유지. AC "Action Prompt 부재만 안내" 충족.

### D4. 표시 내용
- 헤더: 섹션 제목 "다음 행동 · 실행 Prompt" + `badge badge--{variant}` 로 Decision 자기설명(예: `REUSE`).
- 본문: `promptText`를 `.ai-answer-text`(pre-wrap) 박스로 렌더 → 다행 서식 보존.
- (선택) `targetAssetNames.length > 0`이면 "대상 자산: Customer 360 Dashboard" 1줄. 최소 유용성 보강, 미표시해도 AC 충족 → **오픈 이슈 Q2**.

### D5. Copy 동작 + 접근성
- `<button className="btn btn--sm" onClick={copy}>` → `navigator.clipboard.writeText(handoff.promptText)`.
- 성공: 로컬 상태 `copied` → `<span className="confirmation" role="status">복사됨</span>` (green, role=status = 라이브 영역, 기존 피드백 확인과 동일 a11y).
- 실패(clipboard 거부/미지원): 로컬 상태 `failed` → `<span className="error-text" role="alert">복사에 실패했습니다. 아래 내용을 직접 선택해 복사해 주세요.</span>` + promptText 박스는 이미 텍스트 선택 가능 → 수동 대안 제공(AC 4 충족).
- 신규 의존성 없음(브라우저 Clipboard API, secure context=localhost 데모 OK). 버튼 `:focus-visible` 기존 규칙 재사용.

### D6. 타입 추가 — `frontend/src/api/types.ts`
백엔드 camelCase 계약 1:1 미러:
```ts
export interface ActionPromptDTO {
  decisionState: string          // = overallDecision
  promptText: string
  targetAssetNames: string[]
}
// AdviceResponse 에 추가:
//   actionHandoff?: ActionPromptDTO | null   // CR-001; 생성 실패/부재 시 null(비차단)
```

---

## 5. 영향 범위 / 비회귀

- 변경 파일: `types.ts`(필드 1 + 인터페이스 1), `App.tsx`(import + 렌더 1줄), 신규 `ActionHandoffPanel.tsx`. CSS는 **원칙적으로 기존 클래스 재사용**(신규 규칙 0~1개, §6-4 참조).
- API/DTO/기존 컴포넌트 계약 무변경 → U1 회귀 없음, 기존 U2 흐름(home↔result, clarify, error, feedback) 무영향.
- NFR-minimization 준수: 신규 config/flag/의존성 0, 신규 테스트 프레임워크 0(검증=tsc+build+데모 스모크).
