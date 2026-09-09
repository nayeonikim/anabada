# Code Generation Plan — U1 Advisor Backend

> Stage: CONSTRUCTION - Code Generation (U1). **이 문서는 Code Generation의 단일 진실원(single source of truth)**.
> 근거 산출물: domain-entities.md, business-rules.md, business-logic-model.md(S1 + C1~C8), nfr-design-patterns.md(§1~§7), logical-components.md, tech-stack-decisions.md(D1~D8).
> 프로젝트 유형: **Greenfield, multi-unit**(U1 백엔드 / U2 웹 UI). 본 계획은 **U1 백엔드**만 대상.

---

## Part A — 유닛 컨텍스트

### 구현 스토리 (unit-of-work-story-map U1 열)
| Story | 책임 | 컴포넌트 |
|---|---|---|
| US-1.1 Intent 접수 | rawText 접수/가드 | API `/intent`, S1 |
| US-1.2 Intent 구조화 | 5필드 추출(LLM) | C1 Structure |
| US-1.3 모호 의도 명료화 | 누락 검출 + ClarificationRequest | C1 |
| US-2.1 Multi-Source 검색 | Adapter 순회 → asset 단위 Candidate | C2 AssetSearch + Registry/Adapters/Repository |
| US-2.2 권한 필터 + Top-N | per-asset 필터 → 접근가능 Top-3 | C3 PermissionFilter, C4 CandidateSelection |
| US-3.1 LLM 재검증 | Score/근거/충분성 + evaluationStatus | C5 ReVerification |
| US-3.2 State 분류 | REUSE/EXTEND/NEEDS_REVIEW | C6 DecisionClassifier(순수) |
| US-3.3 근거 부족 → NEEDS_REVIEW | evidenceSufficient=false 처리 | C6 |
| US-3.4 적합 없음 → DEVELOP | deriveOverall | C6 |
| US-4.1 랭킹 데이터 | BR-RANK 정렬 + rank | S1 조립 |
| US-4.2 Evidence Chain | 접근가능 Evidence 투영 | C7 EvidenceBuilder |
| US-4.3 피드백 수집 | JSONL append | C8 Feedback, FeedbackStore |

> US-5.1/US-5.2(Later)는 범위 밖. 교체 경계(Adapter/LLMClient/Repository/FeedbackStore/PermissionContext)만 확장 가능하게 유지.

### 의존/인터페이스
- **업스트림 소비자**: U2 Web UI (HTTP `/intent`, `/advise`, `/feedback`). 공개 응답 DTO 계약이 U2와의 인터페이스.
- **하위 경계(DI/교체 가능)**: LLMClient(Bedrock Claude / FixtureProvider), SourceAdapter[](mock), AssetRepository(in-memory), FeedbackStore(JSONL), PermissionContext(mock).
- **소유 데이터**: mock Asset/Evidence(read-only, in-memory), feedback JSONL(append-only, 영속).

### 확정 스택 (tech-stack-decisions D1~D8)
Python 3.11+ / FastAPI(+uvicorn, Pydantic) / Amazon Bedrock Claude(boto3, LLMClient 뒤 격리) / Hypothesis(PBT) / pytest / JSON→in-memory + JSONL / 표준 structured logging.

---

## Part B — 프로젝트 구조 (Greenfield, 워크스페이스 루트)

> 애플리케이션 코드는 **워크스페이스 루트**(NEVER `aidlc-docs/`). 문서 요약만 `aidlc-docs/construction/u1-advisor-backend/code/`.

```
advisor-backend/                     # U1 백엔드 루트 (워크스페이스 루트 하위)
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 앱, 라우트 3개, 예외→오류 DTO 핸들러
│   ├── config.py                    # Config 모듈(env override): thresholds, topN, DEMO_MODE, LLM, 경로, 로그
│   ├── logging_setup.py             # StructuredLogger + 내부 제외 감사 로거
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic 요청 모델 + 공개 응답 DTO(내부 타입 미포함)
│   │   └── errors.py                # 공통 오류 모델 + HTTP↔code 매핑(§1.6)
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py                # 도메인 엔티티/열거(Evidence, Candidate, VerifiedCandidate, evaluationStatus, ExcludedCandidate(내부), ...)
│   ├── services/
│   │   ├── __init__.py
│   │   └── orchestrator.py          # S1 AdvisorOrchestratorService
│   ├── components/
│   │   ├── __init__.py
│   │   ├── structure.py             # C1 (LLM)
│   │   ├── asset_search.py          # C2
│   │   ├── permission_filter.py     # C3
│   │   ├── candidate_selection.py   # C4
│   │   ├── reverification.py        # C5 (LLM)
│   │   ├── decision_classifier.py   # C6 (순수·PBT)
│   │   ├── evidence_builder.py      # C7
│   │   └── feedback.py              # C8
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py                  # SourceAdapter 인터페이스
│   │   ├── registry.py              # SourceAdapterRegistry (config-driven)
│   │   └── mock_source_adapter.py   # mock 6 Source Evidence 검색
│   └── infra/
│       ├── __init__.py
│       ├── llm_client.py            # LLMClient 추상화 + BedrockClaudeClient + FixtureLLMClient
│       ├── asset_repository.py      # in-memory Asset/Evidence 로드
│       └── feedback_store.py        # JSONL append-only
├── data/
│   ├── assets.json                  # per-asset allowedRoles/allowedUsers + Asset 구조(정합 재작성)
│   ├── evidence.json                # Evidence 레코드(assetId/source/evidenceType/title/summary/sourceRef)
│   └── demo_fixtures.json           # Hero + 3 Unhappy 결정적 fixture (demoMode)
├── tests/
│   ├── __init__.py
│   ├── unit/                        # 예제 기반 pytest (C1~C5,C7,C8, API, adapters, repo)
│   └── pbt/
│       └── test_decision_classifier.py  # Hypothesis P1~P11
├── requirements.txt
├── .env.example
└── README.md
```

**Mock 데이터 정합 지시(aidlc-state Open Decision 반영)**: 워크스페이스 `mock/` 원본은 **source-level 권한 모델**(users.json의 source_type scope)로, 도메인 결정 A-2(per-asset)와 다르며 **superseded**. Code Gen은 `advisor-backend/data/`에 **per-asset `allowedRoles`/`allowedUsers` + 정규화된 Asset(summary/lifecycleStatus/capabilities/constraints/evidenceRefs) + Evidence 레코드** 구조로 **파생 mock을 새로 작성**한다. 원본 `mock/`은 참조용으로 보존(수정하지 않음). 권한 매핑은 원본 users.json role(Developer/Sales/Sales·Marketing)과 asset constraint 의미를 반영하여 대표 시나리오(Hero+3 Unhappy)가 재현되도록 부여.

---

## Part C — 실행 스텝 (번호·체크박스; Part 2에서 순차 실행)

### Step 0 — 기능설계 산출물 정합 (NFR Design §7.5 반영) — **문서 갱신, 코드 아님**
> §7.5 지시: NFR Design 시 확정한 §7.1~7.4(evaluationStatus 계약·BR 정제·PBT P1~P11)를 상위 기능설계 문서에 **Code Gen 시 반영**. 코드가 이 문서들을 근거로 생성되므로 **코드 작성 전** 선행.
- [x] `aidlc-docs/construction/u1-advisor-backend/functional-design/domain-entities.md`: VerifiedCandidate에 `evaluationStatus(COMPLETED|UNAVAILABLE)` + nullable `reusabilityScore` + 내부 기술사유(공개 비노출) 필드 반영, ExcludedCandidate(내부 전용) 명시(§7.1) — EvaluationStatus 열거(2.8b) 신설, VerifiedCandidate(2.7)·RankedCandidate(2.10) 갱신
- [x] `.../functional-design/business-rules.md`: BR-STATE(COMPLETED만 REUSE/EXTEND, UNAVAILABLE⇒NEEDS_REVIEW)·BR-OVERALL(기술실패↛DEVELOP, UNAVAILABLE 존재∧REUSE/EXTEND 0⇒NEEDS_REVIEW)·BR-RANK(COMPLETED[State→Score→name]→UNAVAILABLE[name→candidateId]) 정제 + PBT 불변식 **P1~P11**(P5·P8 개정, P10·P11 신규) 반영(§7.3·§7.4)
- [x] `.../functional-design/business-logic-model.md`: C5(ReVerification 성공→COMPLETED / 실패→UNAVAILABLE)·C6(정제 규칙)·C7(UNAVAILABLE은 '평가 미완료'만) 흐름 + 실패 매트릭스(C1 실패→오류 / C5 일부→강등 / C5 전체→오류) + §1.6 HTTP↔code 매핑 반영(§6 재작성)
- [x] 각 문서 상단/해당 섹션에 "NFR Design §7.1~7.4 반영(Code Gen)" 근거 주석 명시. UI 문구/표시는 범위 밖(추후).

### Step 1 — 프로젝트 구조 셋업 (greenfield)
- [ ] `advisor-backend/` 디렉터리 트리 + `__init__.py` 생성
- [ ] `requirements.txt`(fastapi, uvicorn, pydantic, boto3, hypothesis, pytest), `.env.example`, `README.md` 스캐폴드

### Step 2 — Config + Logging (횡단)
- [ ] `app/config.py`: env override 설정(reuseThreshold=0.75, extendThreshold=0.50, TOP_N=3, DEMO_MODE, LLM 모델/리전/타임아웃, 데이터/피드백 경로, 로그 레벨). 임계값 제약(`0<extend≤reuse≤1`) 위반 시 기본값 폴백 + 경고(BR-STATE/P9)
- [ ] `app/logging_setup.py`: 구조화 로거 + **내부 제외 감사 로거**(공개 응답 미포함)

### Step 3 — 도메인 모델 (Business Logic 기반)
- [ ] `app/domain/models.py`: StructuredIntent, ClarificationRequest, Asset, Evidence, Candidate, PermissionContext, **ExcludedCandidate(내부 전용)**, VerifiedCandidate(+`evaluationStatus: COMPLETED|UNAVAILABLE`, nullable `reusabilityScore`, 내부 실패사유 필드), CandidateState/OverallDecision/SourceId/AssetType 열거, RankedCandidate, EvidenceChain/EvidenceItem, AdviceResult, Feedback, ClassificationConfig
- [ ] NFR Design §7.1 반영: evaluationStatus·nullable score·내부 기술사유 분리

### Step 4 — Repository / FeedbackStore / Adapters (Infra)
- [ ] `app/infra/asset_repository.py`: `data/assets.json`+`evidence.json` 로드 → read-only in-memory
- [ ] `app/infra/feedback_store.py`: JSONL append-only + 시작 시 로드(영속, NFR-A4)
- [ ] `app/adapters/base.py`(SourceAdapter 인터페이스), `registry.py`(config-driven), `mock_source_adapter.py`(Evidence[] 반환)

### Step 5 — LLMClient 추상화 + FixtureProvider (Infra)
- [ ] `app/infra/llm_client.py`: `LLMClient` 인터페이스, `BedrockClaudeClient`(boto3, 타임아웃 config, **재시도 없음**), `FixtureLLMClient`(demoMode: `data/demo_fixtures.json` 결정적 응답 / 미매칭 → 명시적 오류)
- [ ] demoMode ON=Fixture / OFF=Bedrock 분기(폴백 없음, §1.2)

### Step 6 — Mock 데이터 작성 (per-asset 권한 정합)
- [ ] `data/assets.json`: 12개 Asset을 per-asset `allowedRoles`/`allowedUsers` + 정규화 필드로 작성
- [ ] `data/evidence.json`: Evidence 레코드(assetId/source/evidenceType/title/summary/sourceRef/lastUpdated)
- [ ] `data/demo_fixtures.json`: Hero + 3 Unhappy 시나리오 결정적 fixture(C1/C5 응답)

### Step 7 — C6 DecisionClassifier (순수 로직) + Business Logic Unit/PBT
- [ ] `app/components/decision_classifier.py`: classifyCandidate/classifyAll(BR-STATE), deriveOverall(BR-OVERALL), BR-RANK 정렬 — **NFR Design §7.3 정제 반영**(COMPLETED만 REUSE/EXTEND 판정, UNAVAILABLE만 존재→NEEDS_REVIEW, 기술실패↛DEVELOP; 랭킹 COMPLETED[State→Score→name]→UNAVAILABLE[name→candidateId])
- [ ] `tests/pbt/test_decision_classifier.py`: Hypothesis **P1~P11**(P5·P8 개정, P10·P11 신규)
- [ ] `tests/unit/test_decision_classifier_examples.py`: 예제 기반 경계 케이스

### Step 8 — C1~C5, C7, C8 컴포넌트 + 단위 테스트
- [ ] `structure.py`(C1): 5필드 추출 + detectMissingFields + ClarificationRequest. 실패→오류(§1.3), demoMode ON 미매칭→명시적 오류
- [ ] `asset_search.py`(C2): Registry 순회 → Evidence를 assetId로 asset 단위 Candidate 집계 + relevance
- [ ] `permission_filter.py`(C3): per-asset isAccessible(BR-PERMISSION) → accessible/excluded, **초기 단일 스테이지**, excluded는 내부 감사 로그
- [ ] `candidate_selection.py`(C4): 접근가능 relevance 내림차순 Top-N(config), 0개→DEVELOP 플래그
- [ ] `reverification.py`(C5): LLM 재검증 → COMPLETED(score/reasoning/roleTaskContextNote/evidenceSufficient) / 실패→UNAVAILABLE(score=null, 내부 사유). 전체 실패→오류 신호(§1.6)
- [ ] `evidence_builder.py`(C7): 접근가능 Evidence → EvidenceChain. UNAVAILABLE은 '평가 미완료'만(내부 기술사유 비노출)
- [ ] `feedback.py`(C8): (resultId, candidateId, verdict) → FeedbackStore append + 확인 id
- [ ] `tests/unit/`: 각 컴포넌트 예제 기반 테스트(LLM은 Fixture/mock 주입)

### Step 9 — S1 Orchestrator + 조립
- [ ] `app/services/orchestrator.py`: submitIntent / advise / submitFeedback 동기 순차 오케스트레이션(business-logic-model §2~§4). 실패 매트릭스(§1.3): C1 실패→오류, C5 일부→강등, C5 전체→오류. 조립 시 BR-RANK + capabilityMatch + excluded 내부 감사
- [ ] `tests/unit/test_orchestrator.py`: Hero + 3 Unhappy end-to-end(Fixture 주입) 흐름 검증

### Step 10 — API Layer + 공개 DTO + 오류 매핑
- [ ] `app/api/schemas.py`: 요청 모델(IntentRequest/AdviseRequest/FeedbackRequest) + **공개 응답 DTO**(RankedCandidate DTO에 `evaluationStatus`+nullable `reusabilityScore`; ExcludedCandidate/제외 개수/플래그/내부 기술사유 **필드 부재** — §3.2 Type-Enforced Non-Disclosure)
- [ ] `app/api/errors.py`: 공통 오류 모델 `{error:{code,message,requestId}}` + HTTP↔code 매핑(§1.6: 502 INTENT_STRUCTURING_FAILED / 504 LLM_TIMEOUT / 502 REVERIFICATION_UNAVAILABLE / 422 DEMO_FIXTURE_NOT_FOUND / 400 EMPTY_INTENT)
- [ ] `app/main.py`: FastAPI 앱, `/intent`·`/advise`·`/feedback` 라우트, DI 조립(config→components→orchestrator), 예외 핸들러(내부 예외 문자열 미노출), OpenAPI 자동 문서
- [ ] `tests/unit/test_api.py`: 라우트·DTO 직렬화(미인가/내부 필드 부재 검증)·오류 매핑 테스트

### Step 11 — 문서 요약 (aidlc-docs)
- [ ] `aidlc-docs/construction/u1-advisor-backend/code/code-summary.md`: 생성 파일 목록·구조·스토리 트레이스·실행 방법 요약
- [ ] `advisor-backend/README.md`: 설치·실행(uvicorn)·env·demoMode·테스트 실행법

> **주의**: 테스트는 본 단계에서 **생성만** 하고 실제 실행/통과는 Build & Test 단계에서 수행.

---

## Part D — 스토리 ↔ 스텝 트레이스

| Story | Step |
|---|---|
| (전체 계약 정합) | Step 0(기능설계 문서 §7.5 반영) |
| US-1.1/1.2/1.3 | Step 8(C1), Step 9, Step 10 |
| US-2.1 | Step 4(Adapter/Repo), Step 8(C2) |
| US-2.2 | Step 8(C3/C4) |
| US-3.1 | Step 5(LLMClient), Step 8(C5) |
| US-3.2/3.3/3.4 | Step 7(C6) |
| US-4.1 | Step 9(조립 BR-RANK), Step 10(DTO) |
| US-4.2 | Step 8(C7) |
| US-4.3 | Step 4(FeedbackStore), Step 8(C8) |

---

## 실행 원칙 (code-generation.md Critical Rules)
- **NO HARDCODED LOGIC / FOLLOW PLAN EXACTLY**: 본 계획 스텝만 실행, 순서 준수.
- **UPDATE CHECKBOXES**: 각 스텝 완료 즉시 `[x]`.
- **코드 위치**: 애플리케이션 코드는 `advisor-backend/`(워크스페이스 루트). 문서 요약만 `aidlc-docs/.../code/`.
- **NFR Design 계약 반영**: evaluationStatus(COMPLETED/UNAVAILABLE)·nullable score·공개 DTO 분리·오류 매핑·PBT P1~P11·demoMode.
- **§7.5 선행 정합**: Step 0에서 domain-entities/business-rules/business-logic-model.md를 §7.1~7.4에 맞게 갱신한 뒤 코드 생성(코드가 이 문서를 근거로 하므로 선행).
- 총 **12 스텝**(Step 0~11).
