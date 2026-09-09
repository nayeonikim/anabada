# AI-DLC State Tracking

## Project Information
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: **INCEPTION (re-entry) — User Stories (증분) APPROVED (2026-09-09); 다음: Workflow Planning(재계획) 진입 예정** for CR-001 Action Handoff, on local branch `feat/action-handoff` (tracks `origin/codex/action-handoff`, forked from `f347c2c`). `stories.md` Epic 6(US-6.1 생성 / US-6.2 표시·Copy) append-only 확정. Requirements Analysis (Minimal delta) + User Stories (증분) 모두 **APPROVED**. 기준 체크포인트(격리 원본): U1 Code Generation Steps 0~11 완료(12/12), 단계 승인 대기.
- **Discovery Input**: docs/aidlc/discovery-input.md (sole Evidence/input source per user constraint; **CR-001은 discovery-input.md에 반영하지 않고 별도 CR로 관리**)
- **Active Branch / Worktree**: local `feat/action-handoff` (tracks `origin/codex/action-handoff`) @ `C:\Users\kimna\anabada-feat-action-handoff` (기준 브랜치 `docs/aidlc-inception-requirements`와 격리)

## Workspace State
- **Existing Code**: No
- **Programming Languages**: None detected
- **Build System**: None detected
- **Project Structure**: Empty (docs + mock data only)
- **Reverse Engineering Needed**: No
- **Workspace Root**: C:\Users\kimna\anabada-feat-action-handoff

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis |
| Resiliency Baseline | No | Requirements Analysis |
| Property-Based Testing | Partial (pure logic / clear I·O only) | Requirements Analysis |

**Note**: Security extension disabled as blocking constraint, but asset permission filtering and unauthorized-asset exclusion retained as normal functional/non-functional requirements (see requirements.md FR-8, NFR-4).

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection (Greenfield determined)
- [x] Reverse Engineering (SKIPPED — Greenfield)
- [x] Requirements Analysis (APPROVED)
- [x] User Stories (APPROVED after revision: stories.md, personas.md)
- [x] Workflow Planning (APPROVED)
- [x] Application Design (APPROVED — 5 artifacts)
- [x] Units Generation — APPROVED (2 units: U1 Advisor Backend, U2 Web UI; US-1.2 U2 소유권 보정 후 승인)

### 🟢 CONSTRUCTION PHASE
- [x] Functional Design — U1 APPROVED (domain-Mock 정합 + 미인가 자산 비노출 반영)
- [x] NFR Requirements — U1 APPROVED (nfr-requirements.md, tech-stack-decisions.md; Top-N config 조정 가능 반영)
- [x] NFR Design — U1 APPROVED (nfr-design-patterns.md + logical-components.md; Q1=C evaluationStatus 계약, PBT P1~P11)
- [x] Infrastructure Design — SKIPPED (mock data, no cloud provisioning for MVP)
- [~] Code Generation — U1 Part 2 완료 (Steps 0~11, 12/12); awaiting stage approval
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Product Scope Change — CR-001 Action Handoff
- **Type**: Product Scope Change (Construction 중 발생, Discovery Input에 없던 신규 요구)
- **Source**: 사용자 요청(본 대화). `docs/aidlc/discovery-input.md` 미수정 — 별도 `aidlc-docs/change-requests/CR-001-action-handoff.md`로 관리.
- **Fork**: 브랜치 `codex/action-handoff` ← 기준 커밋 `f347c2c15ec24f92784648e33317f7610f44960b` (`docs/aidlc-inception-requirements`), 워크트리 `C:\Users\kimna\anabada-feat-action-handoff`.
- **분기 관찰**: 워크트리 생성 직후 기존 워크트리(`C:\Users\kimna\anabada`)에 미커밋 변경(audit.md + `construction/build-and-test/`) 관찰 — 병행 세션의 Build&Test 진입으로 추정. 본 브랜치는 커밋 상태에서 분기하여 격리. 기존 워크트리 진행 중 작업은 미변경.
- **범위(MVP)**: Evidence-grounded Action Prompt 생성 + 결과 화면 표시 + Copy. **범위 밖**: Coding Agent 자동 실행 / 코드 자동 수정 / Commit·PR 자동 생성.
- **Status**: 재진입 계획 승인됨. Requirements Analysis(Minimal delta) **APPROVED**. **INCEPTION - User Stories(증분) APPROVED (2026-09-09)** — stories.md Epic 6 확정. 다음: Workflow Planning(재계획). 구현 미시작.
- **재진입 순서(정정, CR-001 §5)**: Requirements Analysis(Minimal) → User Stories(증분) → Workflow Planning(재계획) → Application Design(증분) → [Units Generation SKIP] → U1 Functional/NFR/Code(증분) → U2(표시/Copy) → Build & Test.
- [x] CR-001 재진입 계획 승인 (2026-09-09, 정정된 Inception→Construction 순서)
- [x] **INCEPTION - Requirements Analysis (Minimal delta)** — `CR-001-requirements-delta.md`(FR-11 / FR-12 / NFR-8 + §3.1 UNAVAILABLE 경계). **APPROVED (2026-09-09)** — Request Changes 3건 반영(Structured Intent grounding·§3.1 경계 명시·API 제안화).
- [x] User Stories (증분) — **APPROVED (2026-09-09)**. Epic 6: US-6.1(생성)/US-6.2(표시·Copy), append-only. Q1~Q7=A + 정제 5건(Hero=Copy 성공·Copy 성공/실패 AC·생성 실패 시 Decision/Evidence 유지[delta+스토리]·API 경로/필드 AC 미전제·목표·근거·다음작업·확인+REUSE/EXTEND 대상 Asset 명확·"현재 산출된 Overall Decision"). delta FR-11/§4/NFR-8/Summary 동반 갱신.
- [ ] Workflow Planning (재계획) — delta 스테이지·깊이 확정
- [ ] Application Design (증분) — C11 ActionHandoffBuilder + `/advise` DTO 계약 + U2 표시 책임
- [ ] Units Generation — **SKIP 예정** (새 유닛 없음; `unit-of-work-story-map.md` 매핑만 갱신)
- [ ] U1 Functional Design (증분) → NFR Design (증분) → Code Generation (증분)
- [ ] U2 착수 시 Action Handoff 표시/Copy 반영 → Build & Test

## Open Decisions (carried forward)
- **A-2**: 권한별 Source 노출 세부 정책 → **RESOLVED (Application Design Q4=A)**: per-asset 권한 모델(allowedRoles/allowedUsers), Source-level 정책 레이어 없음.
- **A-3**: Top-N의 N 구체값 → **RESOLVED (U1 Functional Design Q3=A)**: N=3 (config.topN, env override 가능).
- **Consistency C-1/C-2**: requirements.md 미수정(User 결정 C). 분기 시 stories.md가 authoritative.
- **US-4.1 AC 갱신**: 랭킹 정렬 State→Score→name (U1 Functional Design Follow-up1=A로 stories.md 갱신 완료).
- **State 임계값(Q2=D)**: reuseThreshold=0.75 / extendThreshold=0.50 기본, 환경변수 override → NFR/Code Gen에서 config 노출.
- **CR-001 Action Handoff (2026-09-09, Product Scope Change)**: 재사용 흐름 끝에 Action Handoff 단계 추가(Decision·Evidence 기반 실행 Prompt 생성·표시·Copy). C7 EvidenceBuilder 직후 append-only 삽입 예정. 기존 파이프라인/랭킹/Overall 규칙 비회귀 유지. 상세·영향분석은 `change-requests/CR-001-action-handoff.md`. 승인 대기.
- **Domain-Mock 정합(2026-09-09, Minimal)**: U1 domain model을 mock/adapter-contract에 맞춰 개정 — Evidence 엔티티 도입(Asset 1:N, 다중 Source), Asset 구조화 필드(type/capabilities/lifecycleStatus/constraints) 추가, Candidate=asset 단위. 권한은 A-2(per-asset) 유지, mock의 source-level `accessible_sources` 예시는 **superseded**. **Code Gen 시 mock JSON을 per-asset allowedRoles/allowedUsers + Asset/Evidence 구조로 작성**할 것.
