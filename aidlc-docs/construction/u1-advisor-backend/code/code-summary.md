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
