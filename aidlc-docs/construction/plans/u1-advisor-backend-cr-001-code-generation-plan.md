# U1 Advisor Backend — CR-001 Action Handoff Code Generation Plan (증분)

> **Code Generation (증분) 단일 진실원(SSOT)** for CR-001. 기존 `u1-advisor-backend-code-generation-plan.md`(Step 0~11, 체크포인트)는 **보존**; 본 증분 계획이 CR-001 코드 생성의 실행 기준.
> 근거: `CR-001-functional-design-delta.md`(ActionPrompt·BR-HANDOFF·INV-HANDOFF-1~5·advise step 8), `CR-001-nfr-design-delta.md`(D3 하이브리드·비차단·grounding-only·PBT vs 예제·**§0 NFR 최소화**), `CR-001-application-design-delta.md`(ActionPromptDTO 계약).
> 프로젝트: Brownfield 증분 — **기존 파일은 in-place 수정**(복제본 금지), 신규는 생성. 애플리케이션 코드는 `advisor-backend/`, 문서는 `aidlc-docs/construction/u1-advisor-backend/code/`.
> **본 단계는 코드/테스트 생성까지**; 빌드·테스트 실행은 Build & Test 단계.

---

## 유닛 컨텍스트
- **구현 스토리**: US-6.1(Action Prompt 생성 — C11, U1 단독), US-6.2(데이터 제공 — `actionHandoff` DTO; 표시·Copy는 U2 범위 밖).
- **의존**: 기존 U1 파이프라인(C7/ranking 조립), LLMClient(+FixtureLLMClient), Config. **신규 인프라/저장 0**(NFR 최소화 §0).
- **계약(U1→U2)**: `AdviceResponse.actionHandoff: ActionPromptDTO | null`, `ActionPromptDTO = { decisionState, promptText, targetAssetNames[] }`(camelCase).
- **불변식**: INV-HANDOFF-1(decisionState==overall) / 2(targetAssetNames 규칙) / 3(비노출) / 4(실패→null 비차단) / 5(§3.1 게이팅).
- **비회귀**: 기존 P1~P11·응답 계약·기존 테스트 불변(actionHandoff는 optional/nullable 추가).

---

## 증분 단계 (Step 1~11)

- [x] **Step 1 — 도메인 엔티티** (`advisor-backend/app/domain/models.py`, 수정)
  - `ActionPrompt` dataclass 추가: `decision_state: OverallDecision`, `prompt_text: str`, `target_asset_names: list[str]`.
  - `AdviceResult`에 `action_prompt: Optional[ActionPrompt] = None` 추가(기존 필드 불변). *(US-6.1)*

- [x] **Step 2 — C11 ActionHandoffComponent** (`advisor-backend/app/components/action_handoff.py`, 신규)
  - **(a) 순수 로직**(PBT 대상): `decision_state = overall`; `select_target_asset_names(overall, ranking)`(REUSE/EXTEND → `[ranking[0].asset_name]`, 접근 가능 대상 없으면 예외; DEVELOP/NEEDS_REVIEW → `[]`); `should_note_unavailable(ranking)`(∃ evaluationStatus==UNAVAILABLE); grounding 페이로드 조립(접근 가능 ranking/evidence_chains/intent/overall/overall_rationale만) + 섹션 골격(목표·근거·다음 작업·확인 사항).
  - **(b) LLM 본문**: `llm_client.generate_action_prompt(payload)` → `prompt_text`.
  - `build(intent, overall, overall_rationale, ranking, evidence_chains) -> ActionPrompt`. 실패 시 예외(정합 가드 위반 포함). *(US-6.1 · BR-HANDOFF · INV-HANDOFF-1/2/5)*

- [x] **Step 3 — LLMClient 확장** (`advisor-backend/app/infra/llm_client.py`, 수정)
  - `LLMClient` ABC에 `generate_action_prompt(payload: ActionPromptRequest) -> str` 추가.
  - `BedrockClaudeClient`: grounding-only 간결 프롬프트(§2.4) 조립 + `_invoke` 재사용(재시도 없음·타임아웃 `LLM_TIMEOUT_SECONDS` 재사용).
  - `FixtureLLMClient`: fixtures `"actionHandoff"` 섹션에서 시나리오 키로 promptText 조회, 미매칭 → `DemoFixtureNotFoundError`. *(NFR-A3/T3/C2)*

- [x] **Step 4 — Orchestrator advise() step 8** (`advisor-backend/app/services/orchestrator.py`, 수정)
  - 생성자에 `action_handoff: ActionHandoffComponent` 주입.
  - step 7(ranking) 직후: `try: action_prompt = self._action_handoff.build(...) except Exception: action_prompt=None; audit("action_handoff_failed", ...)` (비차단, 내부 감사).
  - `AdviceResult(..., action_prompt=action_prompt)`. *(BR-HANDOFF-FAIL · INV-HANDOFF-4)*

- [x] **Step 5 — DI 배선** (`advisor-backend/app/main.py`, 수정)
  - `ActionHandoffComponent(llm_client)` 생성 후 `AdvisorOrchestratorService(...)`에 전달. 기존 조립 흐름 유지.

- [x] **Step 6 — 공개 DTO 매핑** (`advisor-backend/app/api/schemas.py`, 수정)
  - `ActionPromptDTO(BaseModel)`: `decisionState: str`, `promptText: str`, `targetAssetNames: list[str]`(camelCase alias 규약 준수).
  - `AdviceResponse`에 `actionHandoff: Optional[ActionPromptDTO] = None` 추가.
  - AdviceResult→AdviceResponse 매퍼에서 `action_prompt` None-safe 매핑(없으면 `actionHandoff=null`). 내부 타입 미노출(§3.2). *(US-6.2 데이터 · INV-HANDOFF-3)*

- [x] **Step 7 — demoMode fixture** (`advisor-backend/data/demo_fixtures.json`, 수정)
  - `"actionHandoff"` 섹션 추가: 대표 시나리오(REUSE/EXTEND_EXISTING/DEVELOP/NEEDS_REVIEW[UNAVAILABLE 포함])별 결정적 `promptText`(목표·근거·다음 작업·확인 사항 포함; §3.1 케이스는 후보 비식별 일반 문구). **대표 케이스 최소 세트**(§0). *(NFR-A3)*

- [x] **Step 8 — Config 확인** (`advisor-backend/app/config.py`, 확인/필요 시 최소 수정)
  - **신규 플래그 미도입**(§0): 기존 `DEMO_MODE` + `LLM_TIMEOUT_SECONDS` 재사용 확인. 하드코딩 부재 확인.

- [x] **Step 9 — 테스트(최소 세트)**
  - `advisor-backend/tests/pbt/test_action_handoff.py`(신규): Hypothesis — INV-HANDOFF-1(decisionState==overall)/2(targetAssetNames 규칙)/5(§3.1 게이팅) 순수 로직.
  - `advisor-backend/tests/unit/test_action_handoff.py`(신규): INV-HANDOFF-3(promptText/targetAssetNames에 미인가 자산명·technicalFailureReason 미포함), INV-HANDOFF-4(LLM mock 예외→action_prompt=None ∧ 기타 결과 불변), 최소 유용성 4요소 존재(fixture), demoMode 재현. *(NFR-T1/T3)*

- [x] **Step 10 — 문서 갱신** (`aidlc-docs/construction/u1-advisor-backend/code/code-summary.md` 수정 + `advisor-backend/README.md` 수정)
  - code-summary: CR-001 증분 파일·트레이스·계약 섹션 추가. README: `actionHandoff` 필드·demoMode 재현 note.

- [x] **Step 11 — 비회귀 확인 note**
  - 기존 공개 DTO/테스트 계약 불변(actionHandoff optional/nullable), P1~P11 불변 확인 note. (실제 실행·통과 확인은 Build & Test)

---

## 스토리 트레이스
| Story | 단계 |
|---|---|
| US-6.1 Action Prompt 생성(C11) | Step 1·2·3·4·5·7·9 |
| US-6.2 데이터 제공(actionHandoff DTO) | Step 6 (표시·Copy는 U2 범위 밖) |

## 산출/수정 파일 요약
- **수정(in-place)**: `app/domain/models.py`, `app/infra/llm_client.py`, `app/services/orchestrator.py`, `app/main.py`, `app/api/schemas.py`, `app/config.py`(확인), `data/demo_fixtures.json`, `code-summary.md`, `README.md`
- **신규**: `app/components/action_handoff.py`, `tests/pbt/test_action_handoff.py`, `tests/unit/test_action_handoff.py`

## 총 규모
- **11 증분 단계**, 신규 3파일 + 수정 9파일. NFR 최소화(§0): 신규 config/인프라 0, 테스트 최소 세트, 단일 LLM 호출.
