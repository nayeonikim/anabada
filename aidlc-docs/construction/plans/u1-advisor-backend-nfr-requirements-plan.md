# NFR Requirements Plan — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Requirements (U1). Functional Design(APPROVED) 기반 비기능 요구 + 기술 스택 확정.
> 확장 설정(aidlc-state): Security Baseline=No, Resiliency Baseline=No, Property-Based Testing=Partial(순수 로직만).
> 제약: 해커톤 MVP ~6h(NFR-2), Token Budget USD 1,000, 동기 순차 in-process 파이프라인, mock 데이터.
> 근거: requirements.md(NFR-1~7), business-logic-model.md(LLM 경계 Q7=A), domain-entities.md(Evidence/Config), business-rules.md(C6 PBT P1~P9).

---

## Part A — 실행 체크리스트

### Plan (questions)
- [x] Functional Design 분석(도메인/흐름/규칙) — 완료
- [x] 기존 NFR(NFR-1~7)·확장 설정 로드 — 완료
- [x] NFR/스택 결정 질문 작성 (Part C) — 완료
- [x] 사용자 답변 수집 ([Answer]: 태그) — 완료 (모두 권장안, Q5/Q7 보강)
- [x] 답변 분석(모호/모순) 및 필요 시 후속 질문 — 완료 (모호성 없음, 후속 질문 불필요)

### Generation (승인 후 산출물)
- [x] `u1-advisor-backend/nfr-requirements/nfr-requirements.md` — U1 비기능 요구 확정본(NFR-1~7 구체화 + 측정 기준)
- [x] `u1-advisor-backend/nfr-requirements/tech-stack-decisions.md` — 언어/프레임워크/LLM/PBT/저장/로깅 결정 + 근거

---

## Part B — 이미 확정된 사항 (재질문 안 함)
- 파이프라인: 동기 순차 in-process, S1 오케스트레이션 (Functional Design).
- 임계값 env override: reuseThreshold=0.75 / extendThreshold=0.50 / topN=3 (Q2/Q3).
- LLM 사용 지점: C1 structure(), C5 reverify()만 LLM. C6는 순수 로직(결정성 보장, PBT 대상).
- 데모 결정성: 대표 시나리오(Hero+3 Unhappy)는 결정적 fixture로 재현(Q7=A/Q8).
- 권한: per-asset(A-2). 미인가 자산 상세는 서버 내부 전용, 공개 응답 미노출(FR-8/NFR-4).
- 확장: Security/Resiliency 규칙 blocking 미적용. PBT는 C6 순수 로직에만 부분 적용(NFR-5).
- 배포/인프라: Infrastructure Design SKIP(mock 데이터, MVP 클라우드 프로비저닝 없음).

---

## Part C — NFR / 기술 스택 결정 질문 (Please fill [Answer]: tags)

> 각 질문에 권장안(Recommended)을 제시. 권장대로면 해당 letter만 적으면 됩니다.

## Question 1 (Backend 언어/런타임)
U1 백엔드 구현 언어/런타임을 무엇으로 할까요?

A) **Python 3.11+** — LLM SDK 성숙, PBT(Hypothesis) 강력, 6h MVP에 생산성 높음. **(Recommended)**

B) TypeScript/Node.js — 프론트(U2)와 언어 통일, PBT는 fast-check.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2 (웹 API 프레임워크)
U2가 호출할 로컬 HTTP API(`/intent`,`/advise`,`/feedback`) 프레임워크는?

A) **FastAPI (Python)** — 타입 기반 스키마/자동 문서(OpenAPI), 경량·빠른 구현, NFR-1(자기설명) 유리. **(Recommended, Q1=A 전제)**

B) Flask (Python) — 더 미니멀하나 스키마/문서는 수동.

C) Express (Node/TS) — Q1=B일 때.

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 (LLM 제공자/SDK)
C1 structure()·C5 reverify()에 쓸 LLM 연동 방식은? (AWS AI-DLC 해커톤 컨텍스트)

A) **Amazon Bedrock — Claude 모델** — AWS 환경 정합, 사내 정책·크레딧 활용 자연스러움. **(Recommended)**

B) Anthropic API 직접(Claude) — 설정 단순, 최신 모델 즉시.

C) 기타 제공자(OpenAI 등).

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4 (PBT 프레임워크 — NFR-5, C6 P1~P9)
C6 순수 로직 Property-Based Testing 프레임워크는?

A) **Hypothesis (Python)** — Q1=A 전제, 성숙·표현력 높음. **(Recommended)**

B) fast-check (TS) — Q1=B일 때.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5 (mock 데이터 + 피드백 저장)
mock Asset/Evidence + 사용자 피드백을 어떻게 저장할까요?

A) **파일(JSON) 로드 + in-memory 보관, 피드백은 in-memory(선택적으로 JSON append)** — 6h MVP·재현성에 충분, DB 불필요. **(Recommended)**

B) 경량 임베디드 DB(SQLite) — 영속성은 좋으나 MVP엔 과함.

C) Other (please describe after [Answer]: tag below)

[Answer]: A (보강) — mock Asset/Evidence는 JSON 로드 후 in-memory 보관(read-only). 사용자 피드백은 **JSONL append-only 파일**에 기록하여 서버 재시작 후에도 유지(영속). 즉 mock=in-memory, feedback=JSONL 파일 영속.

## Question 6 (성능 목표 — /advise)
`/advise`는 Top-3 순차 LLM 재검증을 포함합니다. 성능 목표를 어떻게 둘까요?

A) **Hard SLA 없음. Best-effort 목표(예: 통상 응답 ~15초 이내 지향), fixture 경로는 즉시 응답** — MVP·데모 관점 현실적. **(Recommended)**

B) 구체 SLA 지정(예: p95 < N초) — 부하 테스트 필요, MVP엔 과함.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 7 (토큰 예산 가드 — NFR-2, USD 1,000)
LLM 토큰/비용 통제를 어떻게 할까요?

A) **구조적 가드만: Top-N=3 상한 + 대표 데모는 fixture 우선 + 프롬프트 간결화. 별도 미터링 미구현** — MVP 충분. **(Recommended)**

B) 호출당 토큰 로깅·누적 카운터 등 경량 미터링 추가.

C) Other (please describe after [Answer]: tag below)

[Answer]: A (보강) — fixture 우선 경로는 암묵 분기가 아니라 **명시적 데모 모드**(demoMode 플래그 / 환경변수)로 구분. 데모 모드 ON이면 대표 시나리오는 fixture 결정적 응답, OFF이면 실제 LLM 호출. Top-N=3 상한·프롬프트 간결화는 두 모드 공통.

## Question 8 (로깅/관측)
서버 내부 로깅(미인가 제외 목록 감사 로그 포함) 수준은?

A) **표준 구조화 로그(콘솔/파일), 요청ID·단계·제외 감사(서버 내부)만. 외부 관측 스택 없음** — NFR-1 자기설명 + FR-8 감사 충족, MVP 경량. **(Recommended)**

B) 최소 콘솔 로그만.

C) Other (please describe after [Answer]: tag below)

[Answer]: A
