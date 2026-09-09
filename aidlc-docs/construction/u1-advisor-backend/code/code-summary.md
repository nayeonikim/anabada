# Code Summary — U1 Advisor Backend

> CONSTRUCTION - Code Generation (U1) 산출 요약. 실제 코드는 워크스페이스 루트 `advisor-backend/`.
> 근거 계획: `aidlc-docs/construction/plans/u1-advisor-backend-code-generation-plan.md` (Step 0~11).
> NFR Design §7.1~7.4 반영: evaluationStatus(COMPLETED/UNAVAILABLE) 계약, nullable score,
> 공개 DTO 분리(§3.2), 오류 매핑(§1.6), PBT P1~P11, demoMode.

---

## 1. 생성 파일 목록

### 애플리케이션 (`advisor-backend/`)
| 파일 | 책임 | 스토리/컴포넌트 |
|---|---|---|
| `app/config.py` | env override 설정 + 임계값 제약 폴백(P9) | 횡단 |
| `app/logging_setup.py` | 구조화 로깅 + 내부 감사 로거(공개 미노출) | 횡단 |
| `app/domain/models.py` | 도메인 엔티티/열거(evaluationStatus, nullable score, 내부 기술사유) | §7.1 |
| `app/domain/errors.py` | 오류 코드 + 파이프라인 예외(공개 message/내부 detail 분리) | §1.6 |
| `app/infra/asset_repository.py` | in-memory Asset/Evidence 로드(read-only) | US-2.1 |
| `app/infra/feedback_store.py` | JSONL append-only(영속) | US-4.3 |
| `app/infra/llm_client.py` | LLMClient + BedrockClaudeClient(재시도 없음) + FixtureLLMClient | US-1.2/3.1 |
| `app/adapters/base.py` `registry.py` `mock_source_adapter.py` | SourceAdapter 추상화 + mock 6 Source | US-2.1 |
| `app/components/structure.py` (C1) | 5필드 추출 + 누락 검출 + Clarification | US-1.1/1.2/1.3 |
| `app/components/asset_search.py` (C2) | Multi-Source → asset 단위 Candidate + relevance | US-2.1 |
| `app/components/permission_filter.py` (C3) | per-asset 권한 필터(BR-PERMISSION), excluded 내부 감사 | US-2.2 |
| `app/components/candidate_selection.py` (C4) | relevance Top-N | US-2.2 |
| `app/components/reverification.py` (C5) | LLM 재검증 → COMPLETED/UNAVAILABLE, 전체 실패→오류 | US-3.1 |
| `app/components/decision_classifier.py` (C6) | 순수 로직: classify/deriveOverall/rank(§7.3) | US-3.2/3.3/3.4/4.1 |
| `app/components/evidence_builder.py` (C7) | Evidence Chain(UNAVAILABLE은 '평가 미완료'만) | US-4.2 |
| `app/components/feedback.py` (C8) | 피드백 기록 + 확인 id | US-4.3 |
| `app/services/orchestrator.py` (S1) | submitIntent/advise/submitFeedback 동기 순차 + 실패 매트릭스 | 전체 |
| `app/api/schemas.py` | 공개 요청/응답 DTO(내부·제외 필드 부재, §3.2) | 계약 |
| `app/api/errors.py` | 공통 오류 모델 + HTTP↔code 매핑(§1.6) | 계약 |
| `app/main.py` | FastAPI 앱 + DI 조립 + 예외 핸들러(내부 문자열 미노출) | 계약 |

### 데이터 (`advisor-backend/data/`)
- `assets.json` — 12 Asset(per-asset `allowedRoles`/`allowedUsers` + 정규화 필드).
- `evidence.json` — 36 Evidence 레코드(6 Source: GitHub/Confluence/Jira/IMS/BizForce/EDM).
- `demo_fixtures.json` — Hero + 3 Unhappy 결정적 fixture(structure + reverify).

### 테스트 (`advisor-backend/tests/`)
- `pbt/test_decision_classifier.py` — Hypothesis P1~P11(§7.4).
- `unit/test_decision_classifier_examples.py` — 경계 케이스(0.75/0.50).
- `unit/test_components.py` — C1~C5,C7,C8 예제 기반(LLM Fixture 주입).
- `unit/test_orchestrator.py` — Hero + 3 Unhappy end-to-end.
- `unit/test_api.py` — 라우트·DTO 비노출·오류 매핑.
- `unit/test_demo_coverage.py` — 데모 fixture 커버리지 회귀 가드(Top-N ⊆ reverify fixture, 시나리오 키 정합).
- `unit/conftest.py` — repository/registry fixture.

> 문서 정합(Step 0): `functional-design/{domain-entities,business-rules,business-logic-model}.md`를
> §7.1~7.4에 맞춰 갱신(코드 생성 근거 선반영).

## 2. 스토리 ↔ 코드 트레이스
| Story | 구현 |
|---|---|
| US-1.1/1.2/1.3 | C1 structure + `/intent` + orchestrator.submit_intent |
| US-2.1 | Adapters/Registry/Repository + C2 asset_search |
| US-2.2 | C3 permission_filter + C4 candidate_selection |
| US-3.1 | LLMClient + C5 reverification (evaluationStatus 계약) |
| US-3.2/3.3/3.4 | C6 decision_classifier (BR-STATE/BR-OVERALL, PBT) |
| US-4.1 | orchestrator 조립(BR-RANK) + RankedCandidate DTO |
| US-4.2 | C7 evidence_builder |
| US-4.3 | FeedbackStore + C8 feedback + `/feedback` |

## 3. 핵심 설계 계약
- **evaluationStatus(§7.1)**: COMPLETED만 Score 기반 판정, UNAVAILABLE⇒NEEDS_REVIEW & score=null.
  기술 실패↛DEVELOP(BR-OVERALL). `technicalFailureReason`은 서버 내부 전용(공개 미노출).
- **Type-Enforced Non-Disclosure(§3.2)**: 공개 응답 DTO에 ExcludedCandidate·제외 개수·플래그·
  내부 기술사유 필드가 **구조적으로 부재**. 권한 제외는 내부 감사 로그에만 기록.
- **실패 매트릭스(§1.3/§1.6)**: 빈 rawText→400, C1 실패→502/타임아웃 504,
  C5 일부 실패→UNAVAILABLE 강등(200), C5 전체 실패→502, demoMode 미매칭→422.
- **demoMode**: ON=결정적 fixture(폴백 없음), OFF=Bedrock(폴백 없음).

## 4. 실행/테스트
`advisor-backend/README.md` 참조 (uvicorn 실행, env, demoMode, pytest).

> **주의**: 본 단계는 코드/테스트 **생성**까지. 빌드·테스트 실행 및 통과 확인은 Build & Test 단계.

---

## CR-001 Action Handoff (증분)

> Evidence-grounded Action Prompt 생성 증분. 근거 계획: `aidlc-docs/construction/plans/u1-advisor-backend-cr-001-code-generation-plan.md`(Step 1~11).
> 근거 설계: `change-requests/CR-001-functional-design-delta.md`(ActionPrompt·BR-HANDOFF·INV-HANDOFF-1~5·advise step 8), `CR-001-nfr-design-delta.md`(D3 하이브리드·비차단·grounding-only·§0 NFR 최소화), `CR-001-application-design-delta.md`(ActionPromptDTO 계약).

### C1. 생성/수정 파일
| 파일 | 구분 | 변경 |
|---|---|---|
| `app/components/action_handoff.py` | 신규 | C11 ActionHandoffComponent(하이브리드) + 순수 `select_target_asset_names`/`should_note_unavailable`/`_evidence_lines` |
| `tests/pbt/test_action_handoff.py` | 신규 | Hypothesis PBT(INV-HANDOFF-1/2/5 순수 로직) |
| `tests/unit/test_action_handoff.py` | 신규 | pytest 예제(INV-HANDOFF-3/4·최소 유용성 4요소·demoMode 재현) |
| `app/domain/models.py` | 수정 | `ActionPrompt` dataclass + `AdviceResult.action_prompt: Optional[ActionPrompt]=None` |
| `app/infra/llm_client.py` | 수정 | `ActionPromptRequest` + `generate_action_prompt` (ABC/BedrockClaudeClient/FixtureLLMClient) |
| `app/services/orchestrator.py` | 수정 | advise() step 8 try/except 비차단(C11 실패→`action_prompt=None`, `action_handoff_failed` 내부 감사) |
| `app/api/schemas.py` | 수정 | `ActionPromptDTO` + `AdviceResponse.actionHandoff: Optional[ActionPromptDTO]=None` |
| `app/main.py` | 수정 | `ActionHandoffComponent(llm)` DI 배선 + AdviceResult→DTO None-safe 매퍼 |
| `data/demo_fixtures.json` | 수정 | `actionHandoff` 섹션(대표 시나리오 3종 결정적 promptText) |

### C2. 설계 요점
- **D3 하이브리드**: (a) **순수·결정적** 구조/선택 — Decision→목적 매핑, 대상 Asset 선택(`ranking[0]`), §3.1 '평가 미완료' 게이팅, grounding 페이로드 조립(접근 가능 ranking/evidenceChains 공개 투영만) → PBT 대상. (b) **LLM 자연어 본문** — grounding-only 페이로드로 promptText 생성(LLMClient/FixtureLLMClient).
- **비차단 격리(INV-HANDOFF-4)**: C11 실패(정합 가드 위반·LLM 오류/타임아웃·빈 응답)는 예외로 신호, orchestrator가 잡아 `action_prompt=None` → 핵심 결과 200 정상, 나머지 결과 불변.
- **grounding-only 비노출(NFR-8/INV-HANDOFF-3)**: 입력이 이미 공개 투영이라 미인가 자산명·`technicalFailureReason`·제외 개수/플래그가 구조적으로 유입 불가. `targetAssetNames`는 순수 로직 산출(LLM 자유생성 아님).
- **NFR 최소화(§0)**: 신규 config/인프라 0(기존 `DEMO_MODE`+`LLM_TIMEOUT_SECONDS` 재사용), `/advise`당 LLM 호출 1회 추가, 전용 관측/정량 SLA 없음.

### C3. 공개 계약 (U1→U2)
- `AdviceResponse.actionHandoff: ActionPromptDTO | null` (생성 실패/부재 시 `null` — 비차단).
- `ActionPromptDTO = { decisionState, promptText, targetAssetNames[] }` (camelCase). 내부 `ActionPrompt` 타입 미노출(§3.2).

### C4. 스토리 ↔ 불변식 트레이스
| 근거 | 대상 |
|---|---|
| US-6.1 / FR-11 | BR-HANDOFF · ActionPrompt 엔티티 · INV-HANDOFF-1~5 (C11 생성) |
| NFR-8 / §3.1 | INV-HANDOFF-3(비노출) · INV-HANDOFF-5(§3.1 게이팅) |
| delta §4 비차단 | INV-HANDOFF-4(실패→null, 핵심 결과 불변) |
| US-6.2 / FR-12 | `actionHandoff` DTO 데이터 제공(표시·Copy는 **U2** 범위, U1은 데이터만) |

### C5. 불변식 검증 배분
| 방식 | 커버 |
|---|---|
| Hypothesis PBT (순수) | INV-HANDOFF-1(decisionState==overall) · 2(targetAssetNames 규칙) · 5(§3.1 게이팅) |
| pytest 예제 | INV-HANDOFF-3(promptText/targetAssetNames 미인가 자산명·technicalFailureReason 미포함) · 4(LLM mock 예외→action_prompt=None ∧ 기타 결과 불변) · 최소 유용성 4요소(목표·근거·다음 작업·확인 사항) · demoMode 재현 |

> **비회귀**: 기존 공개 DTO/테스트 계약 불변(`actionHandoff`는 optional/nullable 추가), P1~P11 불변. orchestrator `action_handoff` 생성자 인자 기본값 `None`으로 기존 `test_orchestrator.py` 무수정.
> **주의**: 본 단계는 코드/테스트 **생성**까지. 빌드·테스트 실행 및 통과 확인은 Build & Test 단계.
