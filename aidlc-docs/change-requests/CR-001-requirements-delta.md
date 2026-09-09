# CR-001 Action Handoff — Requirements Delta (Minimal)

> **Requirements Analysis (Minimal depth) 산출물** for CR-001 Product Scope Change.
> Open Decision **C**로 `aidlc-docs/inception/requirements/requirements.md`는 **미수정(동결)**한다.
> 신규 FR/NFR는 본 delta 문서에 기록하며, 분기 시 **stories.md가 authoritative**.
> Base: `requirements.md` FR-1..FR-10 / NFR-1..NFR-7. Answers: `CR-001-requirement-verification-questions.md` (전부 권장 A).

---

## 1. Intent Analysis (delta)

- **User Request**: 재사용 판단 흐름 끝(Evidence 직후)에 **Action Handoff** 추가 — Decision·Evidence 기반 실행 가능한 Prompt를 생성·표시·Copy.
- **Request Type**: Enhancement (기존 서비스에 신규 단계 추가)
- **Scope Estimate**: Multiple Components (U1 신규 컴포넌트 + Advisor 응답 계약 확장(API 형태는 Application Design 결정) + U2 UI 요소)
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
| Q6 | evidence-grounding **비노출 규칙 확정** (§3.1 경계 사례 보완: UNAVAILABLE→NEEDS REVIEW의 후보 비식별 일반 제한 문구 허용) |

---

## 2. New Functional Requirements

| ID | Requirement | 근거 |
|---|---|---|
| **FR-11 (Action Handoff — Prompt 생성)** | Advisor는 **확정된 Structured Intent, 현재 산출된 Overall Decision 및 판단 근거(decision rationale), 접근 가능한 Evidence·Candidate를 근거로**, Overall Decision State별 목적에 맞는 **실행 가능한 단일 Action Prompt**를 생성한다. 도구 비종속 자연어 텍스트이며, 사용자 Intent 입력 언어를 따른다. Prompt는 최소 유용성을 위해 **목표·근거·다음 작업·확인 사항**을 포함하고, REUSE / EXTEND EXISTING인 경우 **대상 Asset을 명확히 식별**한다. 확인되지 않은 Gap·전제는 사실로 단정하지 않고 **확인 질문 형태**로 표현한다. **Prompt 생성 실패 시에도 기존 Decision·Evidence·랭킹 결과는 유지·정상 반환**하고 Action Prompt 부재만 표시한다(append-only·비차단). | CR-001, Q1·Q2·Q3, Request Changes(2026-09-09), User Stories 답변(2026-09-09) |
| **FR-12 (표시·Copy)** | 생성된 Action Prompt를 **결과 화면에 표시**하고 **Copy 가능**하게 한다. (U2 책임; U1은 Prompt 텍스트를 Advisor 응답으로 제공 — API 형태는 Application Design 결정) | CR-001 MVP |

### FR-11 — Overall Decision State별 Prompt 목적
| Overall Decision | Action Prompt 목적 |
|---|---|
| **REUSE** | 선택된(최상위) 기존 Asset을 **활용·통합**하기 위한 Prompt |
| **EXTEND EXISTING** | 기존 Asset과 요구사항의 **Gap**을 기반으로 **수정·확장**하기 위한 Prompt (확인되지 않은 Gap은 사실로 단정하지 않고 확인 질문으로 표현) |
| **DEVELOP** | **확정된 Structured Intent**(핵심 근거) + 신규 개발 판단 근거를 기반으로 **개발을 시작**하기 위한 Prompt |
| **NEEDS REVIEW** | **개발을 시작하지 않고**, 판단 확정에 필요한 **추가 Evidence와 질문**을 정리하는 **Review Prompt** (Q4: Overall=NEEDS REVIEW일 때) |

---

## 3. New Non-Functional Requirements

| ID | Requirement | 근거 |
|---|---|---|
| **NFR-8 (Evidence-grounded / Non-Disclosure 확장)** | Action Prompt는 **확정된 Structured Intent, 현재 산출된 Overall Decision 및 판단 근거(decision rationale), 접근 가능한 Evidence·Candidate만** 근거로 삼는다(근거 밖 생성=환각 금지). 미인가·권한 제외 후보, 내부 기술사유(technicalFailureReason 등), 그리고 평가 미완료(UNAVAILABLE) 후보의 **후보별 상세·내부 오류**는 **근거·노출 금지**. 확인되지 않은 Gap·전제는 사실로 단정하지 않고 확인 질문으로 표현. **경계 예외(UNAVAILABLE→NEEDS REVIEW)는 §3.1 참조.** | Q6(+§3.1 보완), Request Changes(2026-09-09), 기존 FR-8 / NFR-4 / §3.2 확장 |

> NFR-1(Self-Explanatory)·NFR-6(Usability)는 Action Handoff에도 그대로 적용(결과 화면에서 다음 행동이 자기설명적으로 드러나야 함).

### 3.1 UNAVAILABLE 비노출 ↔ NEEDS REVIEW 경계 사례 (Q6 승인 규칙 보완)

Q6=A로 확정한 규칙은 평가 미완료(UNAVAILABLE) 후보를 근거·노출에서 제외한다. 그러나 기존 로직(BR-STATE / BR-OVERALL)상 **평가 미완료가 원인이 되어 Overall = NEEDS REVIEW**가 될 수 있으므로, Review Prompt가 그 사유를 전혀 표현하지 못하면 자기설명성(NFR-1)이 훼손된다. Q6 승인 결정을 **조용히 바꾸지 않고** 아래와 같이 명시적으로 보완한다:

- **금지(유지)**: 평가 미완료 **후보의 식별정보·후보별 상세·내부 기술사유(technicalFailureReason 등)** 는 계속 근거·노출 금지.
- **허용(명시)**: Overall = NEEDS REVIEW의 근거로서, **후보를 식별하지 않는 집계·일반 수준의 제한 문구** — 예: "일부 후보의 평가가 완료되지 않아 판단 확정을 위해 추가 검토가 필요하다" — 는 Review Prompt에 표현 가능.
- **취지**: Q6=A(내부·미인가·후보별 정보 비노출)를 유지하면서 NEEDS REVIEW의 자기설명성(NFR-1)을 확보하는 정제. 구체 문안·발동 조건은 Functional/NFR Design(BR-HANDOFF)에서 확정.

---

## 4. Constraints & Out-of-Scope (delta)

**Out-of-Scope (MVP) — 명시적 (범위 밖)**
- Coding Agent **자동 실행**
- 코드 **자동 수정**
- **Commit / PR 자동 생성**

→ Action Handoff MVP는 **Prompt 생성 + 표시 + Copy까지**. 실행/수정/커밋은 사용자가 외부 도구에서 수동 수행.

**Non-Regression 제약**
- Action Handoff는 Evidence(C7) 직후 **append-only** 단계. 기존 파이프라인(C1~C8)·랭킹(BR-RANK)·Overall(BR-OVERALL)·Candidate State(BR-STATE)·PBT(P1~P11)는 **변경 없이 동작**해야 한다.
- **Action Handoff 실패 격리(비차단)**: Action Prompt 생성이 실패해도 기존 Decision·Evidence·랭킹 결과는 **유지·정상 반환**한다(Action Prompt 부재만 표시). Action Handoff는 핵심 결과의 선행 조건이 아니다. (User Stories 답변 2026-09-09)

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
| FR-11 | User Story(Action Handoff 생성, 백엔드) → (제안) C11 ActionHandoffBuilder + Advisor 응답에 `actionHandoff` 필드. **API 형태(`/advise` 확장 vs 신규 엔드포인트)는 Application Design에서 확정** |
| FR-12 | User Story(표시/Copy, U2) → U2 결과 화면 요소 |
| NFR-8 | Functional/NFR Design 규칙(BR-HANDOFF evidence-grounding) + 테스트 |
| Non-Regression | 기존 U1 회귀 테스트 유지 + Action Handoff append-only 검증 |

---

## 7. Summary

Action Handoff는 재사용 판단의 **현재 산출된 Overall Decision(NEEDS REVIEW 포함)과 근거(확정된 Structured Intent·판단 근거·접근 가능한 Evidence·Candidate)를 "다음 행동을 위한 실행 가능한 단일 Prompt"로 연결**하는 append-only 단계다. Prompt는 목표·근거·다음 작업·확인 사항을 담아 최소 유용성을 보장하며(REUSE/EXTEND는 대상 Asset을 명확히 식별), 생성 실패 시에도 기존 Decision·Evidence는 유지된다. 근거 밖 생성(환각) 및 미인가·후보별 내부정보 노출은 금지하되, UNAVAILABLE→NEEDS REVIEW 경계에서는 후보 비식별 일반 제한 문구를 허용한다(NFR-8 §3.1). API 형태(`/advise` 확장 vs 신규 엔드포인트) 및 필드명은 **제안**이며 Application Design에서 확정한다(스토리 AC는 특정 경로·필드를 전제하지 않음). 생성·표시·Copy까지가 MVP이고 자동 실행/수정/커밋은 범위 밖이다.
