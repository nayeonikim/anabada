# Requirements — Rebuild or Reuse Advisor

> Sole Evidence source: `docs/aidlc/discovery-input.md`.
> Requirements below are derived from that Evidence plus the team's answers in
> `requirement-verification-questions.md` (Requirements Analysis gate).

---

## 1. Intent Analysis

- **User Request**: `docs/aidlc/discovery-input.md`를 입력으로 AI-DLC 워크플로우를 시작하여, "코딩 전에 사내 자산을 탐색·검증하여 재사용/확장/개발/재검토를 제안하는" 서비스(Rebuild or Reuse Advisor)를 도출.
- **Request Type**: New Project (Greenfield)
- **Scope Estimate**: System-wide / Multiple Components (Intent 입력·구조화, Multi-Source 검색, LLM 재검증, 권한 필터, 결과·Evidence UI)
- **Complexity Estimate**: Complex (다중 Persona, Multi-Source 통합, LLM 판단, 권한 모델)
- **Requirements Depth**: Comprehensive
- **Constraint Context**: Hackathon MVP — 약 6시간(MVP 4h + 리뷰 2h), Token Budget USD 1,000, 실제 사내 시스템 접근 제한 → representative mock data 사용.

### Persona (from Evidence)
- **Developer** 와 **Business User**를 동등한 Core Persona로 취급. 사전 우선순위 없음.
- MVP 데모는 **Persona 무관 공통 Reusability 흐름** 하나로 구현하고, 여유가 있으면 Role-specific extension으로 확장 (Q1).

---

## 2. Product Decision (Fixed — 팀 합의값)

Reusability 판단 결과는 아래 4개 Decision State 중 하나로 분류한다:

| Decision State | 의미 |
|---|---|
| **REUSE** | 기존 자산을 그대로 활용 |
| **EXTEND EXISTING** | 기존 자산을 기반으로 필요한 부분을 수정/확장 |
| **DEVELOP** | 적절한 기존 자산이 없어 신규 개발 |
| **NEEDS REVIEW** | 자동 판단이 어려워 추가 검토 필요 |

AI-DLC는 Evidence와 명확히 충돌하는 경우 문제를 제기할 수 있으나 이 4개 상태를 임의로 변경하지 않는다.

---

## 3. Functional Requirements

| ID | Requirement | Evidence / Source |
|---|---|---|
| **FR-1** | 사용자가 만들려는 S/W를 **자연어 Intent**로 입력한다. | Q2, Q7 |
| **FR-2** | AI가 자연어 Intent를 **Role / Goal / Function / Data / Output**으로 구조화한다. 의도 파악이 어려우면 **추가 질문 후 사용자 승인**을 받고 진행한다. | Q2 |
| **FR-3** | 구조화된 Intent를 기반으로 **Multi-Source 자산을 검색**하여 후보를 선별한다. Source는 GitHub / Confluence / Jira / IMS / BizForce / EDM을 대표하는 **representative mock asset**으로 구성한다. | Q3, discovery §5.3 |
| **FR-4** | 검색으로 선별한 **상위 N개 후보만 LLM으로 재사용성 재검증**한다 (Role/Task Context 반영, "단순 유사도 ≠ 실제 재사용성" 가설 반영). | Q4, discovery §4 |
| **FR-5** | 각 후보를 4개 **Decision State**(REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW) 중 하나로 분류한다. | Q5, discovery §1 |
| **FR-6** | 결과를 **복수 후보 랭킹**으로 제시하고, 후보별로 Source · Asset 이름/링크 · Capability Match · Reusability Score · Decision State · 판단 근거를 표시한다. | Q5, Q8 |
| **FR-7** | 모든 추천에 **추적 가능한 Evidence chain**(Source, asset link, 관련 Evidence, 판단 근거)을 제공하여 Black-box를 피한다. | Q8 |
| **FR-8** | 사용자의 **mock permission context**(Role + 자산별 접근 권한)에 따라 결과를 필터링한다. 사용자가 원래 접근할 수 없는 자산·Evidence는 결과에서 **제외**하며, Advisor는 사용자의 기존 권한을 확장하지 않는다. | Q6, Q9, discovery §5.3 |
| **FR-9** | 사용자가 상위 N개 결과에 **피드백**을 줄 수 있고, 피드백을 통해 후보 선별 방식을 고도화한다. | Q4 |
| **FR-10** | **웹 애플리케이션**에서 자연어 Intent 입력 영역과 함께 Asset Ranking · Decision State · Reusability Score · Evidence를 **한 화면에서 시각적으로 비교**한다 (Search → Compare → Decide → Evidence). | Q7 |

---

## 4. Non-Functional Requirements

| ID | Requirement | Evidence / Source |
|---|---|---|
| **NFR-1 (Self-Explanatory)** | Repository, README, AI-DLC 산출물, Evidence chain, 실제 서비스가 스스로 이해 가능하도록 구성한다 (별도 발표 없이 AI 평가 + 상호평가). | discovery §5.2 |
| **NFR-2 (Budget/Time)** | MVP는 약 6시간 내 구현 가능해야 하며 Token Budget(USD 1,000) 내에서 동작해야 한다. MVP 범위는 이 제약에 맞춘다. | discovery §5.1 |
| **NFR-3 (Extensibility)** | Multi-Source 검색은 **Source Adapter 구조**로 설계하여 mock → 실제 Source, mock user → 실제 AD SSO로 확장 가능해야 한다. | Q3, Q6 |
| **NFR-4 (Security — baseline, non-blocking)** | Security 확장 규칙은 blocking 제약으로 적용하지 않으나, **미인가 자산 제외 및 권한 필터링(FR-8)**은 일반 요구사항으로 유지한다. | Q9 |
| **NFR-5 (Testability)** | 입력·출력 관계가 명확한 **핵심 순수 판단 로직에 한해 Property-Based Testing(부분 적용)**으로 안정성을 검증한다. | Q11 |
| **NFR-6 (Usability)** | 단일 화면에서 Search → Compare → Decide → Evidence 흐름을 직관적으로 전달한다. | Q7 |
| **NFR-7 (Mock Representativeness)** | mock asset / permission context는 6개 Source와 권한 모델을 구조·확장 가능성 검증에 충분할 만큼 대표성 있게 구성한다. | Q3, Q6 |

---

## 5. Constraints & Out-of-Scope (MVP)

**Constraints**
- 약 6시간 개발, Token Budget USD 1,000.
- 실제 사내 시스템 접근 제한 → representative mock enterprise data / mock user & permission context 사용.
- 최종 지향점: 삼성전자 DS 전체 AD SSO, 실제 Multi-Source 통합.

**Out-of-Scope (MVP)**
- 실제 SSO 로그인 화면 및 실제 권한 시스템 연동 (mock으로 대체; SSO 화면은 핵심 아님 — Q6).
- 실제 GitHub/Confluence/Jira/IMS/BizForce/EDM 연동 (mock adapter로 대체).
- Production 수준 Resiliency / Failover / Availability 설계 (Resiliency 확장 skip — Q10).
- 전체 Security 확장 규칙의 blocking 적용 (Q9).
- Role-specific extension (여유 시 확장 — Q1).

---

## 6. Extension Configuration

| Extension | Enabled | Rationale |
|---|---|---|
| Security Baseline | **No** | Hackathon PoC; 핵심 보안 요구(권한 필터·미인가 자산 제외)만 일반 requirement로 유지 (Q9) |
| Resiliency Baseline | **No** | PoC — 핵심 End-to-End Flow 완성 우선; Production 전환 시 별도 적용 (Q10) |
| Property-Based Testing | **Partial** | 입력·출력 관계가 명확한 핵심 순수 로직에만 적용 (Q11) |

---

## 7. Assumptions

- **A-1**: Q7 "A+B" 답변은 본문 근거("Chat UI보다 웹 기반 결과 화면이 적합")에 따라 **웹 애플리케이션(자연어 Intent 입력 영역 포함)**으로 해석. Chat 전용 UI는 채택하지 않음.
- **A-2**: 권한별 Source 노출 범위의 세부 정책(Q3)은 **Workflow Planning 단계**에서 재결정.
- **A-3**: "상위 N개"의 N 구체값은 설계 단계에서 확정 (기본 가정: 3~5).

---

## 8. Requirements Summary (Key)

- **핵심 가치**: 코딩 전에 사내 자산을 탐색·비교하여 REUSE / EXTEND / DEVELOP / NEEDS REVIEW를 **근거(Evidence)와 함께** 제안 → 중복 개발·토큰 낭비 방지.
- **핵심 흐름**: 자연어 Intent → 구조화(Role/Goal/Function/Data/Output) → Multi-Source(mock) 검색 → 상위 N LLM 재검증 → Decision State 분류 → 권한 필터 → 랭킹 + Evidence를 웹 단일 화면에 제시.
- **MVP 초점**: Persona 무관 공통 Reusability 흐름 완성 + 추적 가능한 Evidence chain.
