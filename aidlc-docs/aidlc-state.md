# AI-DLC State Tracking

## Project Information
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: OPERATIONS (placeholder) — CONSTRUCTION 전 단계 완료·승인. Build and Test APPROVED(제품 전체 U1+U2): U1 44/44·coverage 92%, U2 tsc strict 0 + vite build 38 modules, 통합 A 4/4. 사용자 승인 2026-09-09. Operations는 향후 배포/모니터링 확장을 위한 placeholder.
- **Discovery Input**: docs/aidlc/discovery-input.md (sole Evidence/input source per user constraint)

## Workspace State
- **Existing Code**: No
- **Programming Languages**: None detected
- **Build System**: None detected
- **Project Structure**: Empty (docs + mock data only)
- **Reverse Engineering Needed**: No
- **Workspace Root**: C:\Users\kimna\anabada

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
- [x] Code Generation — U1 APPROVED (Steps 0~11, 12/12)
- [x] Build and Test — U1 APPROVED (44/44 pass, coverage 92%) — 사용자 승인 2026-09-09.
- [x] U2 Web UI per-unit loop (fast-path):
  - [x] Functional/NFR/Infra 설계 — 압축(U1 API 계약 + application-design 재사용, 신규 도메인/NFR/인프라 없음)
  - [x] Code Generation — APPROVED(React+Vite+TS, 13/13 steps; `npm run build` 성공, strict 오류 0). 사용자 승인 2026-09-09.
- [x] Build and Test — APPROVED(제품 전체 U1+U2, 사용자 승인 2026-09-09): U1 44/44·92%, U2 tsc strict 0 + vite build 38 modules, 통합 A 4/4. 아티팩트: build/unit/integration(Part A+B)/performance/e2e(신규)/summary. Part B 실 렌더링·성능·실 LLM은 데모/Operations 단계.

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER (향후 배포/모니터링 확장 대상; CONSTRUCTION 완료로 현재 진입 지점)

## Open Decisions (carried forward)
- **A-2**: 권한별 Source 노출 세부 정책 → **RESOLVED (Application Design Q4=A)**: per-asset 권한 모델(allowedRoles/allowedUsers), Source-level 정책 레이어 없음.
- **A-3**: Top-N의 N 구체값 → **RESOLVED (U1 Functional Design Q3=A)**: N=3 (config.topN, env override 가능).
- **Consistency C-1/C-2**: requirements.md 미수정(User 결정 C). 분기 시 stories.md가 authoritative.
- **US-4.1 AC 갱신**: 랭킹 정렬 State→Score→name (U1 Functional Design Follow-up1=A로 stories.md 갱신 완료).
- **State 임계값(Q2=D)**: reuseThreshold=0.75 / extendThreshold=0.50 기본, 환경변수 override → NFR/Code Gen에서 config 노출.
- **Domain-Mock 정합(2026-09-09, Minimal)**: U1 domain model을 mock/adapter-contract에 맞춰 개정 — Evidence 엔티티 도입(Asset 1:N, 다중 Source), Asset 구조화 필드(type/capabilities/lifecycleStatus/constraints) 추가, Candidate=asset 단위. 권한은 A-2(per-asset) 유지, mock의 source-level `accessible_sources` 예시는 **superseded**. **Code Gen 시 mock JSON을 per-asset allowedRoles/allowedUsers + Asset/Evidence 구조로 작성**할 것.
