# CR-001 — Action Handoff (Product Scope Change)

> **문서 성격**: AI-DLC 워크플로우 진행 중(Construction) 발생한 **Product Scope Change** 요청 기록.
> 이 변경은 최초 Discovery Input(`docs/aidlc/discovery-input.md`)에 없던 신규 요구이며,
> **discovery-input.md를 수정해 원래 요구였던 것처럼 만들지 않는다.** 별도 산출물인 본 문서에
> 요청·출처·기준 커밋·영향 분석을 기록한다. (근거: `common/workflow-changes.md` — Adding functionality mid-workflow)

---

## 1. 변경 요청 (Request)

**Rebuild or Reuse Advisor**의 재사용 판단 흐름 마지막에 **Action Handoff** 단계를 추가한다.

- **기존 흐름**: Intent → Asset Discovery → Reusability Verification → Decision → Evidence
- **변경 흐름**: Intent → Asset Discovery → Reusability Verification → Decision → Evidence → **Action Handoff**

> 주: 위 5단계는 사용자가 제시한 추상 흐름이다. 실제 U1 파이프라인 컴포넌트에 대응하면
> C1 IntentStructuring → (C2 AssetSearch → C3 PermissionFilter → C4 CandidateSelection) → C5 ReVerification → C6 DecisionClassifier → C7 EvidenceBuilder 이며,
> **Action Handoff는 C7 EvidenceBuilder 직후**에 새 단계로 삽입된다.

### 1.1 목적
Action Handoff는 확정된 **Decision과 Evidence를 근거로**, 사용자가 다음 AI-assisted development workflow에서
**즉시 사용할 수 있는 실행 가능한 Prompt**를 제공한다. (재사용 판단 → 다음 행동으로의 연결)

### 1.2 Decision별 Prompt 목적
| Decision | Action Prompt 목적 |
|---|---|
| **REUSE** | 선택된 기존 Asset을 그대로 활용·통합하기 위한 Prompt |
| **EXTEND EXISTING** | 기존 Asset과 요구사항의 **Gap**을 기반으로 수정·확장하기 위한 Prompt |
| **DEVELOP** | Structured Intent와 신규 개발 판단 근거를 기반으로 개발을 **시작**하기 위한 Prompt |
| **NEEDS REVIEW** | 개발을 시작하지 않고, 판단 확정에 필요한 **추가 Evidence와 질문**을 정리하는 Review Prompt |

### 1.3 MVP 범위
- Evidence-grounded Action Prompt 생성 (결과에 실제로 존재하는 Decision/Evidence/Candidate만 근거로 사용)
- 결과 화면에 표시
- Copy 가능

### 1.4 범위 밖 (Out of Scope)
- Coding Agent 자동 실행
- 코드 자동 수정
- Commit / PR 자동 생성

---

## 2. 출처 (Source)

| 항목 | 내용 |
|---|---|
| 요청 유형 | Product Scope Change (Construction 진행 중 발생) |
| 요청 출처 | 사용자 요청 (본 대화). Discovery Input에 존재하지 않던 신규 요구. |
| Discovery Input 반영 여부 | **반영하지 않음** — `docs/aidlc/discovery-input.md`는 원본 Evidence로 보존(불변). |
| 최초 Discovery 대비 | 최초 4개 Decision State(REUSE/EXTEND EXISTING/DEVELOP/NEEDS REVIEW)는 존재하나, Decision을 실행 Prompt로 연결하는 **Action Handoff 단계는 최초 입력·요구사항·스토리·설계·코드 어디에도 없음** (신규). |
| 전제 | MVP 완료나 결과 검토를 전제로 하지 않는 순수 추가 개발. |

---

## 3. 기준 커밋 (Reference Checkpoint)

| 항목 | 값 |
|---|---|
| 저장소 | `C:\Users\kimna\anabada` (origin: https://github.com/nayeonikim/anabada.git) |
| 기준 브랜치 | `docs/aidlc-inception-requirements` |
| 기준 커밋 | `f347c2c15ec24f92784648e33317f7610f44960b` |
| 커밋 메시지 | `feat: complete U1 advisor-backend API layer and orchestrator` |
| 체크포인트 상태 | U1 Code Generation Step 0~11 완료(12/12), **단계 승인 대기**. Build and Test 미완. U2 Web UI 미구현. |
| 신규 브랜치 | `codex/action-handoff` (위 커밋에서 분기) |
| 신규 워크트리 | `C:\Users\kimna\anabada-action-handoff` |

### 3.1 분기 시점 관찰 사항 (중요)
기준 커밋 확인 시점에는 로컬 HEAD와 원격이 동일하고 작업 트리가 clean이었다.
워크트리 생성 **직후** 기존 워크트리(`C:\Users\kimna\anabada`)에서 커밋되지 않은 변경이 관찰되었다:
`aidlc-docs/audit.md` 수정 + `aidlc-docs/construction/build-and-test/` 신규 디렉터리 —
이는 **기존 워크트리의 병행(진행 중) 세션이 U1 Code Generation을 승인하고 Build and Test로 진입하는 작업**으로 판단된다.

- 본 브랜치 `codex/action-handoff`는 **커밋된 상태(`f347c2c`)에서 분기**했으므로 위 미커밋 변경과 완전히 격리된다.
- 기존 워크트리의 진행 중 작업은 **변경하지 않는다**(관찰만 기록). (근거: 사용자 지시 5)

---

## 4. 영향 분석 (Impact Analysis)

기준 상태에서 U1(Advisor Backend)은 코드 생성 완료, U2(Web UI)는 미구현이다.
Action Handoff는 **U1(Prompt 생성) + U2(표시·Copy)** 에 걸쳐 있다.

### 4.1 Inception 산출물
| 산출물 | 영향 | 비고 |
|---|---|---|
| `requirements.md` | 신규 FR/NFR 후보 발생 | Open Decision C 원칙상 `requirements.md` 미수정 유지 가능, **분기 시 stories.md가 authoritative**. 신규 요구는 스토리로 반영. |
| `stories.md` | **신규 스토리 필요** | 신규 Epic(예: "Action Handoff") 또는 Epic 4 확장. 제안: 백엔드 Prompt 생성 스토리 + U2 표시/Copy 스토리. **번호는 User Stories 재진입 시 확정.** |
| `personas.md` | 영향 없음(추정) | 두 Persona 공통 이득. |
| `application-design/*` | **컴포넌트/서비스 추가** | U1에 신규 컴포넌트(예: C11 ActionHandoffBuilder) 추가; `component-methods.md`, `services.md`, `unit-of-work-story-map.md` 갱신. U2 책임에 "Action Prompt 표시·Copy" 추가. |
| `unit-of-work.md` | U1·U2 책임 확장 | U1 파이프라인 끝에 Action Handoff, U2 화면에 표시/Copy. 유닛 경계(2 units)는 유지. |

### 4.2 Construction 산출물 — U1 (Advisor Backend, 코드 존재)
| 영역 | 영향 |
|---|---|
| Functional Design | 신규 도메인 엔티티 `ActionPrompt`(가칭: decisionState, promptText, groundingRefs→Evidence/Candidate). 신규 규칙 BR-HANDOFF(Decision별 목적), Evidence-grounding 규칙(결과에 존재하는 Evidence/Candidate만 참조), NEEDS_REVIEW=개발 미시작+추가 Evidence/질문. business-logic-model에 C7 이후 신규 step. |
| NFR Design | Evidence-grounded(근거 외 환각 금지), 공개 DTO에 `actionHandoff`/`actionPrompt` 추가(내부 필드 비노출 원칙 유지), demoMode 결정성 유지, Copy는 U2 관심사. |
| Infrastructure Design | 영향 없음(기존과 동일하게 SKIP — mock/로컬). |
| Code | 신규 컴포넌트 `app/components/action_handoff.py`(가칭 C11), `orchestrator`에서 C7 직후 호출, 공개 응답 DTO 확장(`/advise` 응답에 actionHandoff 포함; MVP는 신규 엔드포인트 불요), 신규/보강 테스트(Decision 4종 × Prompt 목적, evidence-grounding 불변식). |
| `code-summary.md` | 갱신 필요. |

### 4.3 Construction 산출물 — U2 (Web UI, 미구현)
- U2는 아직 코드가 없다. Action Handoff MVP의 "결과 화면 표시 + Copy"는 **U2 신규 구현 시 반영해야 할 요구**로 추가된다(신규 화면 요소 + Copy 인터랙션).
- U2 → U1 계약: `/advise` 응답의 `actionHandoff` 필드 소비.

### 4.4 회귀/불변식 (Regression Guardrails)
- 기존 Non-Disclosure(§3.2): Action Prompt는 **사용자가 접근 가능한 Evidence/Candidate만** 근거로 삼는다. 미인가 자산/제외 후보/내부 기술사유는 Prompt에 노출 금지.
- evaluationStatus 계약: UNAVAILABLE(평가 미완료) 후보는 REUSE/EXTEND Prompt의 근거가 될 수 없다.
- 기존 U1 파이프라인/랭킹/Overall 규칙(BR-STATE/BR-OVERALL/BR-RANK, PBT P1~P11)은 **변경 없이** 동작해야 한다(Action Handoff는 append-only 단계).

---

## 5. 워크플로우 재진입 계획 (Re-entry) — **승인됨 (2026-09-09, 정정)**

Action Handoff는 새 user-facing 기능이므로 **INCEPTION 단계부터 재진입**한다(초기 프레이밍의 "CONSTRUCTION 계속"은 부정확 — 정정). CLAUDE.md의 조건부 실행 기준을 적용한 스테이지별 판정:

| 스테이지 | 이 delta | 판정 근거 |
|---|---|---|
| Workspace Detection | 재실행 불필요 | Greenfield 1회 확정 |
| Reverse Engineering | N/A | Greenfield |
| **Requirements Analysis** | **실행 (Minimal)** | 신규 FR/NFR 발생. 단 Open Decision C로 `requirements.md` 동결 → stories.md authoritative. FR/NFR delta는 본 CR의 requirements-delta 산출물에 문서화 |
| **User Stories** | **실행 (증분)** | 새 user-facing 기능 → High Priority |
| **Workflow Planning** | **실행 (경량 재계획)** | delta가 건드리는 스테이지·깊이 확정 |
| **Application Design** | **실행 (증분)** | 신규 컴포넌트 C11 ActionHandoffBuilder + `/advise` DTO 계약 + U2 표시 책임 |
| **Units Generation** | **SKIP** | 새 유닛 없음 — 기존 U1/U2 재사용, `unit-of-work-story-map.md` 매핑만 갱신 |
| **U1 Functional → NFR → Code Generation** | **실행 (증분)** | ActionPrompt 엔티티·BR-HANDOFF·evidence-grounding·C7 이후 흐름·C11·DTO·테스트 |
| **U2** | 착수 시 반영 | 미구현 — Action Handoff 표시/Copy 포함 |
| **Build and Test** | 실행 | U1(Action Handoff 포함) |

**정정된 재진입 순서**:
`Requirements Analysis(Minimal) → User Stories(증분) → Workflow Planning(재계획) → Application Design(증분) → [Units Generation SKIP] → U1 Functional/NFR/Code(증분) → U2(표시/Copy) → Build & Test`

**각 스테이지는 표준 승인 게이트(Request Changes / Continue to Next Stage)를 거친다.** 모든 입력·응답은 `audit.md`에 로깅한다.

### 5.1 Requirements Analysis (Minimal delta) — 진행 중
- 산출물: `aidlc-docs/change-requests/CR-001-requirements-delta.md` (requirements.md는 Decision C로 미수정).
- Clarifying questions: `aidlc-docs/change-requests/CR-001-requirement-verification-questions.md` — **답변 게이트 대기**.

---

## 6. Change Request Log (형식: `common/workflow-changes.md`)

- **Timestamp**: 2026-09-09T00:00:00Z
- **Request**: 재사용 판단 흐름 끝에 Action Handoff(Decision·Evidence 기반 실행 Prompt 생성·표시·Copy) 추가.
- **Current State**: CONSTRUCTION — U1 Code Generation Step 0~11 완료, 단계 승인 대기(기준 커밋 `f347c2c`). Build and Test 미완, U2 미구현.
- **Impact Assessment**: §4 참조 (stories/application-design/U1 functional·NFR·code/U2 요구 추가; 기존 파이프라인 append-only 비회귀).
- **User Confirmation**: **대기 중** — §5 재진입 계획 승인 필요.
- **Action Taken (본 CR 시점)**: `codex/action-handoff` 브랜치 + `C:\Users\kimna\anabada-action-handoff` 워크트리 생성(격리), 본 CR 문서 작성, `aidlc-state.md` Workspace Root 갱신 및 Scope Change 기록, `audit.md` 로그.
- **Artifacts Affected (본 CR 시점)**: (신규) `aidlc-docs/change-requests/CR-001-action-handoff.md`; (수정) `aidlc-docs/aidlc-state.md`, `aidlc-docs/audit.md`. 코드/설계 산출물은 승인 후 변경.

---

## 7. 상태

**INTAKE 완료 · 재진입 계획 승인 대기.** (본 CR는 구현을 시작하지 않는다.)
