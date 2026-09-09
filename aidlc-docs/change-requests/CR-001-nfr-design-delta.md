# CR-001 Action Handoff — U1 NFR Design Delta (증분)

> **U1 NFR Design (증분) 산출물** for CR-001 Product Scope Change.
> 기존 `construction/u1-advisor-backend/nfr-design/*`(nfr-design-patterns.md / logical-components.md)에 append-only 반영(CR-001 마커). 본 문서가 **authoritative 요약·설계 결정(D3)·패턴 매핑**.
> 근거: `CR-001-functional-design-delta.md`(ActionPrompt·BR-HANDOFF·INV-HANDOFF-1~5), `CR-001-application-design-delta.md`(C11·ActionPromptDTO 계약·D1~D3), nfr-design-patterns.md(§1 회복성·§3 비노출·§5 테스트성), tech-stack-decisions.md(D3 Bedrock·D4 Hypothesis·D7 demoMode).

---

## 0. NFR 최소화 방침 (사용자 승인 시 확정, 2026-09-09)

> **결정**: Action Handoff의 NFR 요구/설계는 **최소 footprint**로 유지한다(MVP·해커톤 정합, 확장 규칙 Security/Resiliency 이미 Disabled).
> **적용**:
> - **신규 config/인프라 0**: 별도 `ACTION_HANDOFF_TIMEOUT_SECONDS`·`ACTION_HANDOFF_ENABLED` 플래그 **도입하지 않음** → 기존 `DEMO_MODE` + `LLM_TIMEOUT_SECONDS`만 재사용.
> - **정량 SLA·부하·미터링 없음**(기존 best-effort 계승). Action Handoff 전용 관측/메트릭 미도입.
> - **테스트 최소 세트**: PBT는 INV-HANDOFF-1/2/5(순수부)만, 예제는 INV-HANDOFF-3/4 + 최소 유용성 + demoMode 재현 대표 케이스만. 광범위 매트릭스 지양.
> - 비목표 그대로 계승(§1.7/§2.5/§4.4 등). 아래 패턴은 이 최소 방침 하에서 필요한 항목만 유지.

---

## 1. 확정 설계 결정 — D3: Action Prompt 생성 방식 (Application Design 이관)

### D3 = **하이브리드 (결정적 구조/조립 + LLM 자연어 본문)** *(권장·확정, 게이트에서 override 가능)*

C11 ActionHandoffBuilder를 **2계층**으로 구현한다:

| 계층 | 방식 | 담당 | 근거 불변식/NFR |
|---|---|---|---|
| **(a) 구조·선택 (순수·결정적)** | 코드 로직 (LLM 미사용) | Decision→목적 매핑, 대상 Asset 선택(ranking[0]), §3.1 문구 허용 여부 판정, **grounding 페이로드 조립**(접근 가능 ranking/evidenceChains만), 섹션 골격(목표·근거·다음 작업·확인 사항) | INV-HANDOFF-1/2/5 (PBT), NFR-T1/T2 |
| **(b) 자연어 본문 (LLM)** | LLMClient(Bedrock Claude) 뒤 격리 + FixtureProvider | (a)가 만든 **grounding-only 페이로드**로 promptText 자연어 문안 생성 | NFR-T3(LLM Seam), NFR-A3(demoMode 결정성), NFR-C1/C2 |

**선택 근거**:
- **유용성**: Action Prompt는 외부 AI 개발 도구에 붙여 쓰는 **실행 Prompt** → 자연어 유창성 필요(LLM). 순수 템플릿만으로는 최소 유용성(§목표·근거·다음 작업·확인 사항)의 문안 품질 부족.
- **안전성(NFR-8)**: **구조 필드(targetAssetNames)·매핑·§3.1 게이팅은 LLM이 아닌 순수 로직**이 결정 → 환각/누출 위험을 구조적으로 축소(INV-HANDOFF-2/3/5). LLM은 이미 필터링된 **접근 가능 공개 투영**만 입력으로 받음(신규 데이터 접근 없음).
- **아키텍처 정합**: 기존 C1/C5와 동일한 **LLMClient + FixtureProvider + demoMode** 이음새 재사용(§5.2/§5.3) → 추가 인프라 0.
- **결정성(NFR-A3)**: demoMode ON에서 대표 시나리오는 fixture 결정적 응답 → Action Prompt도 재현 가능.
- **비차단(BR-HANDOFF-FAIL)**: (b) LLM 실패/타임아웃 → C11 예외 → orchestrator가 `actionPrompt=null`(핵심 결과 정상 200). (a) 정합 가드 위반도 동일 처리.

> **대안 기각**: (A) 순수 LLM 일괄 생성 = 구조 필드까지 LLM 의존 → 비노출·불변식 보장 약화. (B) 순수 템플릿 = 안전하나 실행 Prompt 유용성/자연스러움 부족. → 하이브리드가 두 목표(유용성·안전)를 동시 충족.

---

## 2. 패턴 적용 (nfr-design-patterns.md 증분 §8 Action Handoff)

### 2.1 Resilience — 비차단 격리 (BR-HANDOFF-FAIL) · NFR-A2
- C11 LLM 호출은 **재시도 없음 + Config Timeout**(§1.1 재사용; `LLM_TIMEOUT_SECONDS` 또는 전용 `ACTION_HANDOFF_TIMEOUT_SECONDS`).
- **핵심 차이(vs C1/C5)**: C1 실패=요청 오류 종료, C5 전체 실패=공통 오류. **C11 실패는 오류 응답이 아니라 `actionPrompt=null` 비차단**(§1.3 매트릭스에 신규 행). Action Handoff는 핵심 결과의 선행 조건이 아님(FR-11/delta §4).
- **부분 실패 개념 없음**: C11은 요청당 최대 1회 생성(후보 fan-out 아님) → 성공 or null.

### 2.2 Performance / Cost — 단일 추가 호출 · NFR-P2/C1/C2
- `/advise`에 **LLM 호출 1회 추가**(재검증 fan-out과 무관, 상한 불필요). best-effort(§2.5), demoMode fixture 경로 즉시 응답.
- **프롬프트 간결화**(§2.4): grounding 페이로드는 접근 가능 ranking 요약 + 대상 evidence 요약 + intent 핵심만 → 토큰 최소화.
- **No Caching**(§2.2 계승).

### 2.3 Security / Non-Disclosure — grounding-only + 타입 강제 · NFR-8/SEC2/SEC3
- **입력 격리**: (a)가 조립하는 grounding 페이로드는 **접근 가능 ranking·evidenceChains·intent·overallDecision·overallRationale만** 포함. 미인가 후보·ExcludedCandidate·technicalFailureReason·제외 개수/플래그는 **애초에 페이로드에 부재**(입력이 공개 투영이라 구조적 유입 불가).
- **구조 필드 비-LLM 결정**: `targetAssetNames`는 순수 로직(ranking[0].assetName)에서 산출 — LLM 자유생성 아님(INV-HANDOFF-2/3).
- **Rationale Guard 확장(§3.3)**: promptText도 서술 필드로 간주 → 미인가 자산명·식별자 미포함 가드 적용.
- **Type-Enforced Non-Disclosure(§3.2 계승)**: 공개 **ActionPromptDTO**는 `{ decisionState, promptText, targetAssetNames[] }`만 → 후보 id·내부 사유 필드 **구조적 부재**.
- **§3.1 경계 게이팅(NFR-8)**: '평가 미완료' 일반 문구는 (a)가 `∃ UNAVAILABLE in ranking`일 때만 프롬프트 지시에 포함 허용(INV-HANDOFF-5). LLM에 후보 식별정보·기술사유 미전달.

### 2.4 Testability — PBT vs 예제 배분 · NFR-T1/T3 (PBT=Partial)
| 대상 | 방식 | 커버 |
|---|---|---|
| (a) 구조·선택 순수 로직 | **Hypothesis PBT** | **INV-HANDOFF-1**(decisionState==overallDecision), **INV-HANDOFF-2**(targetAssetNames 규칙), **INV-HANDOFF-5**(§3.1 문구 게이팅) — 순수·결정적 |
| (b) LLM 본문 생성 | **pytest 예제 + FixtureProvider** | 최소 유용성 4요소(목표·근거·다음 작업·확인 사항) 존재, demoMode 재현(NFR-A3), grounding 준수 스모크 |
| 비노출 | **pytest 예제** | **INV-HANDOFF-3**(promptText/targetAssetNames에 미인가 자산명·technicalFailureReason 미포함 — fixture 산출물 검증) |
| 비차단 | **pytest 예제(LLM mock 예외 주입)** | **INV-HANDOFF-4**(C11 실패 → actionPrompt=null ∧ 나머지 결과 불변) |

> Partial PBT 원칙 준수: **순수 매핑/선택 로직에만 PBT**, LLM 경계·문안은 예제 기반. (business-rules.md의 INV-HANDOFF-1/2/5를 PBT 대상으로 표기)

### 2.5 Scalability / Maintainability
- **DI 경계 재사용(§4.2)**: C11은 기존 LLMClient/FixtureProvider/Config를 주입받음 — 신규 경계 없음.
- **Externalized Config(§4.3) — 최소(§0)**: **기존 `DEMO_MODE` + `LLM_TIMEOUT_SECONDS` 재사용**. Action Handoff 전용 신규 플래그 미도입.
- **OpenAPI(NFR-M1/U1)**: ActionPromptDTO·AdviceResponse.actionHandoff 자동 문서화(nullable 명시).

---

## 3. 논리 컴포넌트 증분 (logical-components.md)

### C11 ActionHandoffComponent (신규)
- **책임**: (a) Decision→목적 매핑·대상 Asset 선택·§3.1 게이팅·grounding 페이로드 조립(순수) → (b) LLMClient로 promptText 생성 → ActionPrompt 반환. 실패 시 예외(orchestrator가 null 처리).
- **의존**: LLMClient(+FixtureProvider), Config. (신규 저장/인프라 없음)
- **위치**: S1 advise 조립(step 7) 직후 step 8. try/except로 감싸 비차단.
- **NFR**: NFR-8/SEC2·SEC3, NFR-A2(비차단), NFR-A3(demoMode), NFR-T1(PBT 순수부)·T3(LLM Seam), NFR-C1/C2, NFR-M1/U1.

### API Layer 증분
- 공개 **ActionPromptDTO** = `{ decisionState, promptText, targetAssetNames[] }`(camelCase). **AdviceResponse.actionHandoff: ActionPromptDTO | null** 추가(생성 실패/부재 시 null). 내부 타입(ActionPrompt)↔DTO 매핑 경계에서 비노출 재확인.

### 데이터 흐름 증분 (advise)
```
… → S1 assemble(ranking) → C11 ActionHandoff(LLMClient|Fixture) : ActionPrompt|null (try/except 비차단)
                          → 공개 Response DTO(actionHandoff 포함; 실패 시 null)
```

---

## 4. NFR ↔ 패턴 매핑 (Action Handoff 행 추가)
| NFR | 적용 |
|---|---|
| NFR-8 / SEC2·SEC3 | grounding-only 입력, 구조 필드 비-LLM 결정, Rationale Guard 확장, ActionPromptDTO 타입 강제, §3.1 게이팅 |
| NFR-A2 | 비차단 격리(실패→actionPrompt=null), No-Retry+Timeout |
| NFR-A3 | LLM Seam + FixtureProvider(demoMode 결정적 재현) |
| NFR-C1/C2 | 단일 추가 호출·프롬프트 간결화·demoMode fixture |
| NFR-T1/T3 | PBT(INV-HANDOFF-1/2/5 순수부) + LLM Seam 예제 |
| NFR-M1/U1 | ActionPromptDTO/actionHandoff OpenAPI 문서화 |

## 5. Code Generation 반영 지시 (증분)
- `app/components/action_handoff.py`(C11): (a)순수 구조/선택 + (b)LLMClient 본문 생성, 실패 시 예외.
- `app/api/schemas.py`: `ActionPromptDTO` + `AdviceResponse.actionHandoff: Optional[ActionPromptDTO]=None`(camelCase).
- `orchestrator.advise()`: step 7 직후 try/except로 C11 호출 → `AdviceResult.actionPrompt`(실패 시 None).
- Config/env: **기존 `DEMO_MODE` + `LLM_TIMEOUT_SECONDS`만 재사용**(신규 플래그 미도입, §0 최소화).
- FixtureProvider: 대표 시나리오(REUSE/EXTEND/DEVELOP/NEEDS_REVIEW·UNAVAILABLE 포함)별 결정적 Action Prompt fixture — **대표 케이스 최소 세트**.
- 테스트(최소 세트, §0): PBT(INV-HANDOFF-1/2/5) + pytest(INV-HANDOFF-3/4, 최소 유용성 4요소, demoMode 재현 대표 케이스) + **비회귀**(기존 P1~P11·응답 계약 불변).
