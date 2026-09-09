# NFR Design Plan — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Design (U1). NFR Requirements(APPROVED) 기반 설계 패턴 + 논리 컴포넌트 확정.
> 근거: nfr-requirements.md(NFR-P/S/A/SEC/T/M/C/U), tech-stack-decisions.md(D1~D8), business-logic-model.md(S1 오케스트레이션 + C1~C8 + SourceAdapterRegistry).
> 확장: Security/Resiliency blocking 미적용, PBT는 C6 순수 로직만.

---

## Part A — 실행 체크리스트

### Plan (questions)
- [x] NFR Requirements 분석(패턴 필요 지점 식별) — 완료
- [x] 설계 패턴/논리 컴포넌트 결정 질문 작성 (Part C) — 완료
- [x] 사용자 답변 수집 ([Answer]: 태그) — 완료 (Q1=C 보완, Q2~Q5 권장)
- [x] 답변 분석(모호/모순) 및 필요 시 후속 질문 — 완료 (모호성 없음; C5 기술실패↛DEVELOP 설계 함의 반영)

### Generation (승인 후 산출물)
- [x] `u1-advisor-backend/nfr-design/nfr-design-patterns.md` — 적용 설계 패턴(회복성/확장성/성능/보안) + NFR 매핑
- [x] `u1-advisor-backend/nfr-design/logical-components.md` — 논리 컴포넌트/인프라 요소 + 통합 방식

---

## Part B — 이미 확정된 사항 (재질문 안 함)
- 아키텍처: 동기 순차 in-process, S1(AdvisorOrchestratorService) 오케스트레이션 (Functional Design).
- 컴포넌트: C1 structure / AssetSearch / PermissionFilter / CandidateSelection / ReVerification / DecisionClassifier(순수) / EvidenceBuilder / Feedback + SourceAdapterRegistry.
- LLM 경계: C1 structure(), C5 reverify()만 LLM(Bedrock Claude, LLMClient 추상화 뒤). C6 순수 결정적(PBT).
- 데모 모드: demoMode(env) — ON=대표 시나리오 fixture 결정적·LLM 미호출 / OFF=실제 호출. Top-N·프롬프트 간결화 공통.
- 저장: mock JSON→in-memory(read-only) / feedback JSONL append-only(영속).
- Config: reuseThreshold=0.75, extendThreshold=0.50, topN(기본3·TOP_N override), 데모모드, LLM 설정, 경로, 로그.
- 권한: per-asset 필터, 미인가 자산 상세·개수·플래그 공개 응답 전면 비노출, 서버 내부 감사 로그.
- 성능: Hard SLA 없음(best-effort). Availability: Production HA 비목표(Resiliency skip).
- Infra: Infrastructure Design SKIP(mock 데이터, MVP 클라우드 프로비저닝 없음).

---

## Part C — 설계 패턴 / 논리 컴포넌트 결정 질문 (Please fill [Answer]: tags)

> 각 질문에 권장안(Recommended) 제시. 권장대로면 해당 letter만 적으면 됩니다.

## Question 1 (Resilience — LLM 실패/타임아웃 패턴, NFR-A2)
C1 structure()·C5 reverify() LLM 호출이 실패/타임아웃하면 어떻게 처리할까요?

A) **후보 단위 강등 (재시도 없음)** — reverify 실패 시 해당 후보를 `NEEDS_REVIEW`로 강등 + 내부 로그, 요청 전체는 계속 진행. structure 실패 시 대표 시나리오는 fixture 폴백, 그 외는 명확한 에러 응답. LLM 타임아웃은 config. **(Recommended, MVP)**

B) 경량 재시도 — 실패 시 1회 짧은 백오프 재시도 후 그래도 실패면 강등. (약간의 회복성, 지연 증가 가능)

C) Other (please describe after [Answer]: tag below)

[Answer]: C (A 기반 보완 — 확정 계약)
- 재시도 없음, LLM 타임아웃은 config 관리. demoMode OFF: 실제 호출 실패 시 fixture 폴백 없음. demoMode ON: 대표 시나리오 fixture, 미매칭 입력은 명시적 오류.
- **C1 실패**: 명확한 오류 응답으로 요청 종료.
- **C5 일부 실패**: 정상 응답에 후보 포함하되 `evaluationStatus`로 구분 — COMPLETED(score∈[0,1], 기존 State 규칙; 근거부족 NEEDS_REVIEW도 COMPLETED) vs UNAVAILABLE(score=null, state=NEEDS_REVIEW). 공개 사유는 일반적 '평가 미완료'만; TECHNICAL_FAILURE·내부 예외는 서버 내부.
- **랭킹**: 평가 실패 후보는 점수 비교 제외, 완료 후보 뒤 정렬. 완료 후보는 State→Score→name 유지, 실패 후보끼리는 name→candidateId.
- **Overall**: 정상 REUSE/EXTEND 있으면 완료 후보만으로 기존 규칙; REUSE/EXTEND 없고 실패 후보 있으면 NEEDS_REVIEW; 일부 실패 시 overallRationale에 일반적 제한 문구; 기술 실패로 DEVELOP 산출 금지.
- **C5 전체 실패**(대상 ≥1 전부): AdviceResult 대신 비정상 HTTP + 공통 오류 `{error:{code,message,requestId}}`(내부 예외 문자열 미포함, HTTP↔code 매핑 설계 산출물에 정의). 검색 0/접근가능 0은 평가 실패 아님 → 기존 정상 DEVELOP 경로 유지.
- 설계 정합성: 후보 모델·공개 DTO·Overall/랭킹 규칙·PBT 불변식(P5 등) 변경을 산출물에 명시. UI 문구/표시는 추후. 현 단계는 백엔드 응답 계약만 확정. (Q1만 보완, 나머지 권장)

## Question 2 (Performance — 재검증 캐싱 패턴, NFR-P2/C1)
동일 자산·의도에 대한 LLM 재검증 결과를 캐싱할까요?

A) **캐싱 없음** — Top-N=3 상한 + 데모 모드 fixture로 충분. 상태 단순, MVP 적합. **(Recommended)**

B) in-memory memoization — (assetId + intent 해시) 키로 reverify 결과 캐시. 반복 데모 시 지연·토큰 절감, 상태 관리 추가.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 (Security — 미인가 비노출 강제 패턴, NFR-SEC2)
미인가 자산 정보가 공개 응답에 새지 않도록 어떻게 강제할까요?

A) **공개 응답 전용 DTO 분리 + 초기 단일 필터 (이중 방어)** — PermissionFilter를 파이프라인 초기에 단일 스테이지로 적용하고, 공개 응답은 내부 타입(ExcludedCandidate 등)을 구조적으로 담을 수 없는 별도 Pydantic response model로만 직렬화. 내부 감사 로그와 응답 모델을 타입으로 분리. **(Recommended)**

B) 단일 필터 스테이지만 — 내부 타입을 응답에 직접 넣지 않도록 코드 관례로 관리(타입 분리 없음).

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4 (Scalability — Source Adapter 등록 패턴, NFR-S2/NFR-3)
Multi-Source 확장을 위한 SourceAdapter 등록 방식은?

A) **Config-driven Registry** — SourceAdapterRegistry가 config에 선언된 adapter 목록을 로드. 신규 Source는 Adapter 구현 + config 등록만으로 통합(코어 무변경). 코어 로직은 Adapter 인터페이스에만 의존. **(Recommended)**

B) 코드 하드코딩 목록 — registry에 adapter를 코드로 나열(확장 시 코드 수정 필요).

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5 (Logical Components — 구성 범위)
U1 논리 컴포넌트/인프라 요소 구성 범위는?

A) **최소 구성** — Config 모듈, LLMClient 추상화(+FixtureProvider), StructuredLogger(+내부 감사), FeedbackStore(JSONL), In-memory AssetRepository(+SourceAdapterRegistry). Circuit breaker / message queue / 외부 cache 없음. **(Recommended, MVP)**

B) 추가 인프라 컴포넌트 포함 — 위에 더해 cache/retry decorator 등 추가.

C) Other (please describe after [Answer]: tag below)

[Answer]: A
