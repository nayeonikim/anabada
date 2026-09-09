# CR-001 Action Handoff — Application Design Delta (증분)

> **Application Design (증분) 산출물** for CR-001 Product Scope Change.
> 원본 `inception/application-design/*`는 append-only로 C11/Epic 6 반영(각 파일 CR-001 마커). 본 문서가 CR-001 설계 증분에 대해 **authoritative 요약·근거**.
> 근거: `CR-001-execution-plan-delta.md`(APPROVED §8 미결정 3건), `CR-001-requirements-delta.md`(FR-11/FR-12/NFR-8+§3.1), `stories.md` Epic 6(US-6.1/US-6.2).
> 상세 도메인 필드·비즈니스 룰(BR-HANDOFF)·Prompt 생성 방식(LLM vs 템플릿)은 **U1 Functional/NFR Design(증분)에서 확정**.

---

## 1. 확정된 설계 결정 (execution-plan-delta §8 미결정 해소)

| # | 미결정 | **확정(권장안)** | 근거 |
|---|---|---|---|
| D1 | API 형태: `/advise` 확장 vs 신규 엔드포인트 | **`/advise` 응답에 `actionHandoff` 단일 객체 필드 추가 (신규 엔드포인트 없음)** | Action Prompt는 `advise()`가 이미 산출한 Overall Decision·rationale·접근 가능 ranking/evidence에서 **동일 동기 파이프라인 내** 파생. 별도 엔드포인트는 결과 컨텍스트 재전달·중복 연산 유발. U2는 결과를 1회 호출로 소비(단일 화면, NFR-6). CR-001 §4.2 "MVP 신규 엔드포인트 불요"와 정합. **스토리 AC는 경로·필드 미전제 → 본 결정이 확정.** |
| D2 | C11 배치 & 실패 처리 | **orchestrator `advise()` 7단계 조립 직후(=C7 Evidence 이후) C11 호출, `try/except`로 감싸 실패 시 `actionHandoff=None` 반환(비차단)** | append-only·실패 격리(FR-11 생성 실패 유지, delta §4 Non-Regression). Action Handoff는 핵심 결과의 선행조건 아님. |
| D3 | Prompt 생성 방식(LLM/템플릿/혼합) | **Application Design에서 미확정 — C11 인터페이스는 추상(grounding 입력 → ActionPrompt) 유지, 방식은 Functional/NFR Design(증분)에서 확정** | 과설계 방지. PBT 후보(Overall→Prompt 목적 매핑=순수·결정) 여부도 Functional Design에서 판정. |

> D1/D2는 **권장 확정**이며 승인 게이트에서 변경 가능. D3은 의도적으로 다음 단계 이관.

---

## 2. 신규 컴포넌트 — C11 ActionHandoffBuilder

| 항목 | 내용 |
|---|---|
| **Component** | C11 ActionHandoffBuilder |
| **Unit** | U1 Advisor Backend |
| **Purpose** | 확정된 Structured Intent · **현재 산출된 Overall Decision 및 rationale** · **접근 가능한** ranking/evidence를 근거로, Overall Decision State별 목적에 맞는 **단일 실행 가능한 Action Prompt**를 생성한다. (FR-11) |
| **Responsibilities** | ① Overall Decision State(REUSE/EXTEND_EXISTING/DEVELOP/NEEDS_REVIEW)별 목적에 맞는 단일 Prompt 생성(도구 비종속 자연어, 사용자 입력 언어). ② 최소 유용성 확보: **목표·근거·다음 작업·확인 사항**을 Prompt 본문에 포함. ③ REUSE/EXTEND는 **대상 Asset(최상위 접근 가능 후보)을 명확히 식별**. ④ evidence-grounding 준수: 근거 밖 생성 금지, 미인가·후보별 내부정보·technicalFailureReason 비노출(NFR-8). ⑤ NEEDS_REVIEW는 개발 미시작 Review Prompt; 평가 미완료가 원인이면 §3.1 후보 비식별 일반 문구만. ⑥ 확인되지 않은 Gap/전제는 확인 질문 형태로 표현. ⑦ 생성 실패는 예외로 알리고 **호출측(orchestrator)이 비차단 처리**. |
| **Interface (개념)** | `build(intent, overallDecision, overallRationale, ranking, evidenceChains) → ActionPrompt` (실패 시 예외 → orchestrator가 None 처리) |
| **Non-Disclosure 구조 보장** | 입력 `ranking`은 **이미 미인가 후보 제외 + technicalFailureReason 미투영**된 공개 투영(RankedCandidate)이고, `evidenceChains`는 접근 가능 Evidence만 포함. C11은 이 공개 투영만 소비 → 구조적으로 미인가·내부정보 유입 불가. |

### 2.1 grounding 입력 상세
| 입력 | 타입 | 비고 |
|---|---|---|
| intent | StructuredIntent | 확정된 5필드 (DEVELOP의 핵심 근거) |
| overallDecision | OverallDecision | 현재 산출된 Overall(NEEDS_REVIEW 포함) |
| overallRationale | string | Overall 산출 근거 |
| ranking | RankedCandidate[] | **접근 가능** 후보만(권한 제외·내부사유 부재). REUSE/EXTEND 대상 Asset = 최상위 후보(BR-OVERALL=최고 Score 후보 State) |
| evidenceChains | EvidenceChain[] | 접근 가능 Evidence만 |

---

## 3. C11 메서드 (component-methods 증분)

| Method | Purpose | Input | Output |
|---|---|---|---|
| `build(intent, overallDecision, overallRationale, ranking, evidenceChains)` | Overall Decision별 목적의 단일 Action Prompt 생성(grounding 준수) | StructuredIntent, OverallDecision, string, RankedCandidate[], EvidenceChain[] | ActionPrompt (실패 시 예외) |

> 내부 보조 로직(Decision→목적 매핑, 대상 Asset 선택, §3.1 문구 판정 등)은 Functional Design(BR-HANDOFF)에서 상세화. Application Design 수준은 시그니처·목적까지.

---

## 4. Action Prompt 응답 계약 (U1 → U2 API, D1 확정)

### 4.1 신규 공개 DTO — `ActionPromptDTO`
| Field | 개념 타입 | 설명 |
|---|---|---|
| decisionState | string | 이 Prompt가 대응하는 Overall Decision (REUSE/EXTEND_EXISTING/DEVELOP/NEEDS_REVIEW) — U2 자기설명성(US-6.2) |
| promptText | string | 도구 비종속 자연어 Prompt 전문(사용자 입력 언어; 목표·근거·다음 작업·확인 사항 포함). Copy 대상 |
| targetAssetNames | string[] | REUSE/EXTEND의 대상 Asset 명(접근 가능 ranking에서만 도출; DEVELOP/NEEDS_REVIEW는 빈 배열). 선택적 구조화 노출 — 본문에도 식별됨 |

> **비노출 유지**: ActionPromptDTO에는 후보 id·미인가 자산·technicalFailureReason·제외 개수·플래그 필드가 **구조적으로 부재**(기존 `schemas.py` §3.2 원칙 계승).

### 4.2 `AdviceResponse` 확장 (append-only)
- `AdviceResponse`에 **`actionHandoff: ActionPromptDTO | null`** 필드 추가.
- **생성 실패/부재 시 `actionHandoff = null`** → 기존 `ranking`/`overallDecision`/`overallRationale`/`isRecommendation`/`evidenceChains`는 **그대로 정상 반환**(FR-11·US-6.1/US-6.2 비차단 AC).
- 기존 필드·의미 **불변**(비회귀).

### 4.3 도메인 모델 (개념 — Functional Design에서 확정)
- 신규 도메인 엔티티 `ActionPrompt { decisionState, promptText, targetAssetNames[] }`. `AdviceResult`에 `actionPrompt: ActionPrompt | None` 추가(공개 DTO 매핑 원천).

---

## 5. 서비스 오케스트레이션 증분 (S1 AdvisorOrchestratorService)

`advise()` 순서에 **7단계 조립 직후** append:

```
… 6) EvidenceBuilder.build(...)            → EvidenceChain[]
   7) 조립: BR-RANK 정렬 + rank + capabilityMatch → ranking
   8) [신규] ActionHandoffBuilder.build(intent, overall, overallRationale, ranking, evidenceChains)
        try  → actionPrompt
        except → actionPrompt = None (내부 감사 로깅, 비차단)   # D2
   9) AdviceResult 조립 (… + actionPrompt)
```

- **UI 계약 불변**: submitIntent → advise → 결과 화면 → submitFeedback. `advise` 응답에 `actionHandoff`만 추가.
- **실패 격리**: C11 예외는 상위로 전파하지 않음(핵심 결과 보호).

---

## 6. 컴포넌트 의존성 증분 (component-dependency)

| Depends → | 대상 |
|---|---|
| **Orchestrator(S1)** → **C11 ActionHandoffBuilder** | ✅ 신규(C7 이후 호출) |
| **C11** → 외부 | 없음(순수 조립) 또는 LLMClient(방식이 LLM일 경우 — Functional/NFR Design에서 확정). MockDataStore 직접 의존 없음(공개 투영만 소비) |

- C11은 **접근 가능 공개 투영(ranking/evidenceChains)만** 입력받아 미인가/내부정보 유입 경로 없음(구조적 비노출).
- 기존 C1~C8 의존성·데이터 흐름 **불변**.

---

## 7. U2 (Web UI) 표시·Copy 책임 (US-6.2 / FR-12)

- Advisor 결과의 `actionHandoff`를 소비하여 **결과 화면에 Action Prompt 표시**, 어떤 Overall Decision(`decisionState`)에 대한 것인지 자기설명적으로 노출(NFR-1/NFR-6).
- **Copy**: `promptText` 전체를 클립보드 복사 + **성공 알림("복사됨")** / **실패 시 알림 + 수동 선택·복사 대안** 제공.
- **부재 처리**: `actionHandoff = null`이면 기존 랭킹·Decision·Evidence는 그대로 표시하고 **Action Prompt 부재만 안내**.
- U2는 U1 계약 소비자 — 경로·필드는 본 문서 D1(`/advise` 응답 `actionHandoff`) 확정에 따름.

---

## 8. Story ↔ Unit 매핑 증분 (unit-of-work-story-map)

| Story | U1 Advisor Backend | U2 Web UI | 비고 |
|---|---|---|---|
| US-6.1 Action Prompt 생성 | ✅ C11 ActionHandoffBuilder + `AdviceResult.actionPrompt` | — | 백엔드 전용(생성·grounding·비차단) |
| US-6.2 Action Prompt 표시 & Copy | ✅ `/advise` 응답 `actionHandoff` 제공 | ✅ 표시 + Copy(성공/실패) + 부재 안내 | 화면 주도(U2), 데이터(U1) |

- 유닛 경계(2 units) 불변 — 새 유닛 없음(Units Generation SKIP).

---

## 9. 비회귀 / 불변식 (재확인)

- 기존 C1~C8 파이프라인·BR-RANK·BR-OVERALL·BR-STATE·evaluationStatus(UNAVAILABLE) 계약·PBT P1~P11 **변경 없음**.
- `AdviceResponse` 기존 필드 불변; `actionHandoff`는 **선택적 추가**(append-only, null 허용).
- 미인가·후보별 내부정보·technicalFailureReason 비노출 원칙 계승(NFR-8), §3.1 경계는 NEEDS_REVIEW 후보 비식별 일반 문구만 허용.

---

## 10. 다음 단계 이관 (Traceability)

| 항목 | 이관 대상 |
|---|---|
| BR-HANDOFF(Decision별 목적·대상 Asset 선택·§3.1 문구·확인 질문화·최소 유용성) 상세 규칙 | U1 Functional Design (증분) |
| Prompt 생성 방식(LLM/템플릿/혼합) + PBT 적용 지점(Overall→목적 매핑) + demoMode 결정성 | U1 NFR Design (증분) |
| `ActionPromptDTO`/`AdviceResponse.actionHandoff`/`ActionPrompt` 도메인 + C11 구현 + orchestrator 통합 + 테스트(Decision 4종·grounding·비차단·비회귀) | U1 Code Generation (증분) |
| 표시·Copy(성공/실패)·부재 안내 UI | U2 |
