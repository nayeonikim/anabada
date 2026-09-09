# CR-001 Action Handoff — Story Generation Plan (증분) · PART 1 (Planning) — RESOLVED

> User Stories 규칙 `inception/user-stories.md`의 증분 계획서. 기본 `story-generation-plan.md`는 미수정, 본 파일은 CR-001 증분 전용.
> **Base**: `inception/user-stories/stories.md`(Epic 1~5, US-1.1~US-5.2) · `personas.md`(P1/P2). **미수정 append-only 증분**.
> **근거**: `change-requests/CR-001-requirements-delta.md` — FR-11 / FR-12 / NFR-8(+§3.1). Answers: `CR-001-requirement-verification-questions.md`(Q1~Q6=A).
>
> ✅ **GATE 통과 (2026-09-09)**: §3 질문 **Q1~Q7 = 모두 A** + 5가지 정제 반영(§0). 계획 승인으로 간주하여 Part 2(Generation) 실행 → `stories.md` Epic 6 생성 완료.

---

## 0. Resolved Answers & Refinements (2026-09-09)

**Answers**: Q1=A · Q2=A · Q3=A · Q4=A · Q5=A · Q6=A · Q7=A (전부 권장)

**사용자 정제 (Message, 2026-09-09) — Part 2 및 delta에 반영 완료**:
1. **Hero 확장**: Hero 흐름을 **Copy 성공까지** 포함하도록 확장(§48 갱신, stories.md Hero + US-6.2 AC).
2. **Copy 성공/실패 구분 AC**: US-6.2에 복사 **성공 알림("복사됨")** + **실패 알림 + 수동 복사 대안** AC 추가.
3. **생성 실패 시 결과 유지**: Action Prompt 생성 실패 시 **기존 Decision·Evidence·랭킹 결과 유지·정상 반환** — `delta`(FR-11 + §4 Non-Regression 비차단 격리) **및** stories(US-6.1·US-6.2 AC) 반영.
4. **API 경로·필드 AC 미전제**: US-6.2 AC에서 `/advise`·`actionHandoff` 등 구체 경로·필드명을 전제하지 않음(설계 확정 전). 대신 Prompt **최소 유용성**(목표·근거·다음 작업·확인 사항) + **REUSE/EXTEND 대상 Asset 명확성**을 AC로 검증.
5. **용어 정정**: "확정된 판단" → **"현재 산출된 Overall Decision"**(NEEDS REVIEW 포괄) — delta(FR-11/NFR-8/Summary) 및 stories(Epic 6/US-6.1/Hero) 반영.

---

## 1. Story Breakdown 접근 (Step 5 — options) → **확정: A (신규 Epic 6)**

기존 stories.md는 **Epic 그룹 + Epic 내부 User Journey 순서**를 쓴다. Action Handoff는 재사용 판단 흐름의 **Evidence 다음 단계**이므로 동일 방식이 자연스럽다.

| 접근 | 설명 | 트레이드오프 |
|---|---|---|
| **신규 Epic 6 "Action Handoff"** ✅ 확정 | Evidence(Epic 4) 다음의 독립 단계로 별도 Epic 신설 | 트레이스·비회귀 경계가 가장 명확. Epic 수 증가 |
| Epic 4 확장 | 기존 "Results, Comparison & Evidence"에 스토리 추가 | Epic 수 유지. 단계 경계가 덜 뚜렷 |

## 2. 생성된 스토리 (Part 2 결과 — `stories.md` Epic 6에 반영 완료)

### Epic 6 — Action Handoff
- **US-6.1 Action Prompt 생성 (U1, 백엔드) [MVP] · Hero** — FR-11. 근거=확정 Structured Intent·현재 산출된 Overall Decision 및 판단 근거·접근 가능한 Evidence·Candidate. AC: State별 단일 Prompt / 최소 유용성(목표·근거·다음 작업·확인) / REUSE·EXTEND 대상 Asset 명확 / DEVELOP=Structured Intent 핵심 / NEEDS REVIEW=Review Prompt(§3.1 후보 비식별 일반 문구 허용) / Gap=확인 질문 / 비노출(NFR-8) / **생성 실패 시 기존 결과 유지·비차단**.
- **US-6.2 Action Prompt 표시 & Copy (U2, 프론트) [MVP] · Hero** — FR-12. AC: 표시(어떤 Overall Decision인지 자기설명) / Copy **성공 알림** / Copy **실패 알림 + 수동 복사 대안** / Prompt 부재(생성 실패) 시 기존 결과 유지 안내. **API 경로·필드 미전제**(Application Design 확정).

### Hero Scenario 갱신 (확정)
기존 Hero 흐름 끝(…→Decision→Evidence)을 **→ Action Handoff: 생성 + 표시 + Copy(성공까지)**로 확장. Hero 스토리에 **US-6.1, US-6.2** 추가.

### Non-Regression (스토리 차원)
- 기존 US-1.1~US-5.2 **변경 없음**. Action Handoff는 append-only.
- US-4.1(랭킹)·US-4.2(Evidence)·US-3.x(Decision) 산출물을 **소비**할 뿐 수정하지 않는다.

---

## 3. Clarifying Questions (Step 3 — 답변 게이트) — 모두 A로 확정

> 이미 확정된 요구 결정(Q1~Q6: 단일 Prompt·tool-agnostic·언어·NEEDS REVIEW·Extension·비노출)과 설계 이관 항목(API 형태·LLM vs 템플릿)은 여기서 다시 묻지 않는다.

### Q1. Story 구조(Epic 배치)
- **A) 신규 Epic 6 "Action Handoff" 신설** (Recommended)
- B) 기존 Epic 4(Results/Evidence)에 스토리 추가.

[Answer]: A

### Q2. 백엔드(U1) 스토리 분할 단위
- **A) Prompt 생성 스토리 1개** (Recommended)
- B) 생성 스토리 + NEEDS REVIEW Review Prompt 스토리 분리(2개).

[Answer]: A

### Q3. 프론트(U2) 스토리 분할 단위
- **A) "표시 + Copy" 한 스토리** (Recommended)
- B) 표시 / Copy 두 스토리로 분리.

[Answer]: A

### Q4. Hero Scenario 포함 범위
- **A) 백엔드 생성 + U2 표시를 Hero 흐름에 포함** (Recommended)
- B) Hero 흐름은 Evidence까지 유지, Action Handoff는 Hero 외 MVP 스토리로.

[Answer]: A — **정제**: Hero는 **Copy 성공까지** 포함(표시 후 Copy 성공 확인). (Refinement 1)

### Q5. Persona 매핑 & MVP 태그
- **A) 두 Persona(P1/P2) 공통 + 전부 [MVP]** (Recommended)
- B) 다르게(예: 일부 Later, Persona 차등).

[Answer]: A

### Q6. Copy 성공 피드백(UX 상세)
- **A) Copy 성공 시 간단한 확인 표시("복사됨")를 AC로 명시** (Recommended)
- B) Copy 동작만, 확인 표시 없음.

[Answer]: A — **정제**: 성공("복사됨") **및 실패(알림 + 수동 복사 대안)** 를 구분하는 AC 추가. (Refinement 2)

### Q7. MVP 범위 확인(편집/재생성 제외)
- **A) MVP는 생성+표시+Copy만** (Recommended) — Prompt 편집·재생성·자동 실행/수정/commit·PR은 범위 밖.
- B) Prompt 수동 편집/재생성 스토리도 MVP에 포함.

[Answer]: A

---

## 4. Mandatory Story Artifacts (Step 4 — Part 2 완료)

- [x] `stories.md`에 Action Handoff 증분 반영(INVEST 준수, append-only — 기존 스토리 미수정)
- [x] 각 신규 스토리에 AC(Given/When/Then) + [MVP] 태그
- [x] Hero Scenario·Persona↔Story Mapping·MVP/Later 요약 표에 신규 스토리 반영
- [x] `personas.md` 검토 — 신규 Persona 불필요(P1/P2 공통), **변경 없음**

## 5. Execution Checklist (Step 2 — Part 2 Generation) — 완료

- [x] S1. §3 답변(전부 A) + 정제 반영해 Epic 배치·스토리 분할·Hero·Persona·태그 확정
- [x] S2. `stories.md`에 Epic 6(US-6.1/US-6.2) append + Hero/Mapping/MVP요약 갱신 + CR-001 헤더 노트
- [x] S3. `personas.md` 검토(변경 불필요)
- [ ] S4. `unit-of-work-story-map.md` 매핑 갱신은 후속(Application Design/Units)에서 — 스토리 단계에서는 스토리 ID만 확정
- [x] S5. aidlc-state.md 갱신 + 완료 메시지(2-옵션)

## 6. Traceability (delta → 스토리)

| Delta 요구 | 스토리 |
|---|---|
| FR-11 (Prompt 생성 + 최소 유용성 + 생성 실패 시 결과 유지) | US-6.1 (U1) |
| FR-12 (표시·Copy 성공/실패) | US-6.2 (U2) |
| NFR-8 (+§3.1 UNAVAILABLE 경계) | US-6.1 AC(evidence-grounding + 후보 비식별 일반 문구) |
| Non-Regression (비차단 격리) | 기존 US 미수정 + US-6.1/US-6.2 생성 실패 시 결과 유지 AC |
