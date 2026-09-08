# AI-DLC State Tracking

## Project Information
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T00:00:00Z
- **Current Stage**: CONSTRUCTION - U1 (Advisor Backend) Functional Design — IN PROGRESS
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
- [~] Units Generation — IN PROGRESS (2 units: U1 Advisor Backend, U2 Web UI — awaiting approval)

### 🟢 CONSTRUCTION PHASE
- [ ] Functional Design — EXECUTE
- [ ] NFR Requirements — EXECUTE
- [ ] NFR Design — EXECUTE
- [ ] Infrastructure Design — SKIP (mock data, no cloud provisioning for MVP)
- [ ] Code Generation — EXECUTE
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Open Decisions (carried forward)
- **A-2**: 권한별 Source 노출 세부 정책 → **RESOLVED (Application Design Q4=A)**: per-asset 권한 모델(allowedRoles/allowedUsers), Source-level 정책 레이어 없음.
- **A-3**: Top-N의 N 구체값(기본 3~5) → Functional Design에서 확정.
- **Consistency C-1/C-2**: requirements.md 미수정(User 결정 C). 분기 시 stories.md가 authoritative.
