# CR-001 Action Handoff — Requirements Delta (Minimal)

> **Requirements Analysis (Minimal depth) 산출물** for CR-001 Product Scope Change.
> Open Decision **C**로 `aidlc-docs/inception/requirements/requirements.md`는 **미수정(동결)**한다.
> 신규 FR/NFR는 본 delta 문서에 기록하며, 분기 시 **stories.md가 authoritative**.
> Base: `requirements.md` FR-1..FR-10 / NFR-1..NFR-7. Answers: `CR-001-requirement-verification-questions.md` (전부 권장 A).

---

## 1. Intent Analysis (delta)

- **User Request**: 재사용 판단 흐름 끝(Evidence 직후)에 **Action Handoff** 추가 — Decision·Evidence 기반 실행 가능한 Prompt를 생성·표시·Copy.
- **Request Type**: Enhancement (기존 서비스에 신규 단계 추가)
- **Scope Estimate**: Multiple Components (U1 신규 컴포넌트 + `/advise` 응답 계약 확장 + U2 UI 요소)
- **Complexity Estimate**: Moderate
- **Requirements Depth**: Minimal (사용자 합의; requirements.md 동결)
- **흐름 변화**: `… → Decision → Evidence` → **`… → Decision → Evidence → Action Handoff`** (C7 EvidenceBuilder 직후 append-only 삽입)

### 확정된 결정 (answers = 전부 권장 A)
| Q | 결정 |
|---|---|
| Q1 | Action Prompt는 **Overall Decision 기준 단일 1개** |
| Q2 | **도구 비종속(tool-agnostic) 일반 텍스트** Prompt |
| Q3 | **사용자 Intent 입력 언어**를 따름(기본 한국어, 기술용어 영문 혼용) |
| Q4 | Review Prompt는 **Overall Decision = NEEDS REVIEW**일 때 산출 |
| Q5 | Extension 설정 **유지**(Security No / Resiliency No / PBT Partial) |
| Q6 | evidence-grounding **비노출 규칙 확정** |

---

## 2. New Functional Requirements

| ID | Requirement | 근거 |
|---|---|---|
| **FR-11 (Action Handoff — Prompt 생성)** | Advisor는 **Overall Decision과 그 근거 Evidence를 기반으로**, Overall Decision State별 목적에 맞는 **실행 가능한 단일 Action Prompt**를 생성한다. 도구 비종속 자연어 텍스트이며, 사용자 Intent 입력 언어를 따른다. | CR-001, Q1·Q2·Q3 |
| **FR-12 (표시·Copy)** | 생성된 Action Prompt를 **결과 화면에 표시**하고 **Copy 가능**하게 한다. (U2 책임; U1은 Prompt 텍스트를 `/advise` 응답으로 제공) | CR-001 MVP |

### FR-11 — Overall Decision State별 Prompt 목적
| Overall Decision | Action Prompt 목적 |
|---|---|
| **REUSE** | 선택된(최상위) 기존 Asset을 **활용·통합**하기 위한 Prompt |
| **EXTEND EXISTING** | 기존 Asset과 요구사항의 **Gap**을 기반으로 **수정·확장**하기 위한 Prompt |
| **DEVELOP** | Structured Intent + 신규 개발 판단 근거를 기반으로 **개발을 시작**하기 위한 Prompt |
| **NEEDS REVIEW** | **개발을 시작하지 않고**, 판단 확정에 필요한 **추가 Evidence와 질문**을 정리하는 **Review Prompt** (Q4: Overall=NEEDS REVIEW일 때) |

---

## 3. New Non-Functional Requirements

| ID | Requirement | 근거 |
|---|---|---|
| **NFR-8 (Evidence-grounded / Non-Disclosure 확장)** | Action Prompt는 **결과에 실제 존재하는 Decision·Evidence·접근 가능 Candidate만** 근거로 삼는다. 미인가·권한 제외 후보, 평가 미완료(UNAVAILABLE) 후보, 내부 기술사유(technicalFailureReason 등)는 **근거·노출 금지**. 근거 밖 내용 생성(환각) 금지. | Q6, 기존 FR-8 / NFR-4 / §3.2 확장 |

> NFR-1(Self-Explanatory)·NFR-6(Usability)는 Action Handoff에도 그대로 적용(결과 화면에서 다음 행동이 자기설명적으로 드러나야 함).

---

## 4. Constraints & Out-of-Scope (delta)

**Out-of-Scope (MVP) — 명시적 (범위 밖)**
- Coding Agent **자동 실행**
- 코드 **자동 수정**
- **Commit / PR 자동 생성**

→ Action Handoff MVP는 **Prompt 생성 + 표시 + Copy까지**. 실행/수정/커밋은 사용자가 외부 도구에서 수동 수행.

**Non-Regression 제약**
- Action Handoff는 Evidence(C7) 직후 **append-only** 단계. 기존 파이프라인(C1~C8)·랭킹(BR-RANK)·Overall(BR-OVERALL)·Candidate State(BR-STATE)·PBT(P1~P11)는 **변경 없이 동작**해야 한다.

---

## 5. Extension Configuration (delta)

| Extension | Enabled | 비고 |
|---|---|---|
| Security Baseline | **No** (유지) | 핵심 비노출(NFR-8)은 일반 requirement로 유지 |
| Resiliency Baseline | **No** (유지) | — |
| Property-Based Testing | **Partial** (유지) | Action Prompt의 **Decision→목적 매핑/선택 로직이 순수 함수**면 PBT 대상 후보 (예: Overall Decision → Prompt 종류 결정은 결정적·순수) |

---

## 6. Traceability (delta → 후속 단계)

| Delta 요구 | 다음 산출물(예정) |
|---|---|
| FR-11 | User Story(Action Handoff 생성, 백엔드) → C11 ActionHandoffBuilder + `/advise` 응답 `actionHandoff` 필드 |
| FR-12 | User Story(표시/Copy, U2) → U2 결과 화면 요소 |
| NFR-8 | Functional/NFR Design 규칙(BR-HANDOFF evidence-grounding) + 테스트 |
| Non-Regression | 기존 U1 회귀 테스트 유지 + Action Handoff append-only 검증 |

---

## 7. Summary

Action Handoff는 재사용 판단의 **결론(Overall Decision)과 근거(Evidence)를 "다음 행동을 위한 실행 가능한 단일 Prompt"로 연결**하는 append-only 단계다. 근거에 존재하는 접근 가능한 정보만 사용(NFR-8)하며, 생성·표시·Copy까지가 MVP이고 자동 실행/수정/커밋은 범위 밖이다.
