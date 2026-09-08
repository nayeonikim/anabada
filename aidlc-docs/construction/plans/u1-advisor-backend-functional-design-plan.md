# Functional Design Plan — U1 Advisor Backend

> Stage: CONSTRUCTION - Functional Design (U1). Part 1: Plan + Questions.
> 근거: components.md(C1~C10), component-methods.md(개념 타입/시그니처), services.md(S1/S2 오케스트레이션), requirements.md(FR/NFR), stories.md(AC), unit-of-work.md.
> 목적: U1의 상세 비즈니스 로직/도메인 모델/비즈니스 룰을 기술 중립으로 확정. (기술스택은 이후 NFR 단계)
> 제약: 해커톤 MVP ~6h, 동기 순차 in-process 파이프라인, mock 데이터, 순수 판단 로직(C6) PBT 대상(NFR-5).

---

## Part A — 실행 체크리스트

### Plan (Part 1)
- [x] 컨텍스트 분석 (application-design + requirements + stories) — 완료
- [x] 설계 결정 질문 작성 (Part C) — 완료
- [ ] 사용자 답변 수집 (Q1~Q9 `[Answer]:` 태그 작성)
- [ ] 답변 분석 (모호/모순 확인), 필요 시 후속 질문

### Generation (Part 2) — 승인 후 생성할 산출물
- [ ] `construction/u1-advisor-backend/functional-design/domain-entities.md` — 도메인 엔티티 + 관계 + 필드 상세
- [ ] `construction/u1-advisor-backend/functional-design/business-logic-model.md` — 파이프라인 단계별 알고리즘/데이터 흐름
- [ ] `construction/u1-advisor-backend/functional-design/business-rules.md` — 판정 룰(Candidate State/Overall), 권한 필터, Top-N, 명료화, PBT 불변식
- [ ] 유닛 경계 검증(U1 API 3개), 담당 스토리(US-1.1~4.3 백엔드) 커버리지 검증

---

## Part B — 설계 대상 요약 (컨텍스트에서 확정된 것)

이미 확정되어 **질문 불필요**한 항목:
- 파이프라인 순서(services.md): search → permission filter → Top-N → reverify → classify → deriveOverall → evidence build → assemble.
- Candidate State 3종(REUSE/EXTEND EXISTING/NEEDS REVIEW), Overall 4종(+DEVELOP). 후보 단위엔 DEVELOP 없음.
- 명료화 기준: 5필드(Role/Goal/Function/Data/Output) 중 1개 이상 누락 시 ClarificationRequest.
- 권한 필터는 재검증 前, per-asset(allowedRoles/allowedUsers), 권한 확장 금지.
- 접근 가능 후보 0개 → Overall=DEVELOP.
- 노출 API 3개: `/intent`(submitIntent), `/advise`, `/feedback`.

아래 **질문에서 확정**해야 할 항목: Score 척도, State 판정 임계/룰, Top-N의 N, Overall 종합 룰, NEEDS REVIEW 근거 표현, 랭킹 tie-break, LLM 경계(실제 호출 vs 스크립트 mock), mock 데이터 시나리오 범위.

---

## Part C — 설계 결정 질문 (Please fill [Answer]: tags)

> 각 질문에 권장안(Recommended)을 제시했습니다. 권장안대로면 letter만 적으시면 됩니다.

## Question 1 — Reusability Score 척도
후보 재사용성 Score를 어떤 척도로 둘까요? (stories 예시는 0.9 / 0.8 / 0.4)

A) **0.0 ~ 1.0 실수(소수 둘째 자리)** — 예시와 일치, 정렬·임계 판정 단순. **(Recommended)**

B) 0 ~ 100 정수 스케일

C) 이산 등급(High/Medium/Low)만

D) Other

[Answer]: A

## Question 2 — Candidate State 판정 룰 (C6, PBT 핵심)
재검증 결과(Score + 근거)로부터 후보별 State(REUSE / EXTEND EXISTING / NEEDS REVIEW)를 어떻게 판정할까요?

A) **Score 임계 + 근거 충분성 플래그 조합 (Recommended)**:
   - `evidenceSufficient == false` → **NEEDS REVIEW** (Score 무관, US-3.3 우선).
   - else Score ≥ 0.75 → **REUSE**
   - else Score ≥ 0.5 → **EXTEND EXISTING**
   - else (< 0.5) → **NEEDS REVIEW**
   - (임계값 0.75 / 0.5는 조정 가능 — 변경 원하시면 D에 기입)

B) 근거 충분성 무시, Score 임계만으로 판정

C) 재검증(C5)이 State를 직접 반환하고 C6는 통과만 (C6 순수 로직 약화 — PBT 가치 저하)

D) Other (임계값/룰 직접 지정)

[Answer]: D. A의 방향으로 하되, 임계값 수치는 사용자가 환경 변수로 변경할 수 있도록 한다.

## Question 3 — Top-N의 N 값 (Open Decision A-3)
권한 필터 후 재검증 대상 상위 N개의 N을 얼마로 확정할까요?

A) **N = 3 (Recommended)** — 6h/토큰 예산 내 재검증 호출 최소화, 데모 화면 간결.

B) N = 5

C) N = 접근 가능 후보 수에 따라 3~5 동적 (min(5, accessible))

D) Other

[Answer]: A

## Question 4 — Overall Decision 종합 룰
후보별 State로부터 요청 전체 Overall Decision(REUSE/EXTEND EXISTING/NEEDS REVIEW/DEVELOP)을 어떻게 산출할까요?

A) **우선순위 종합 (Recommended)**:
   - 접근 가능 후보 0개 → **DEVELOP**
   - REUSE 후보 ≥ 1 → **REUSE**
   - else EXTEND EXISTING 후보 ≥ 1 → **EXTEND EXISTING**
   - else 적합(REUSE/EXTEND) 후보 0 & NEEDS REVIEW만 존재 → **NEEDS REVIEW**
   - (적합 후보 하나도 없고 후보 자체가 없으면 DEVELOP)

B) 최고 Score 후보의 State를 Overall로 승격 (단, 적합 0 → DEVELOP)

C) Other

[Answer]: B로 하여 추천하고, 최종 판단은 사용자가 하는 것이라고 명시한다.

## Question 5 — NEEDS REVIEW 근거(evidenceSufficient) 표현 방식
"근거 부족/상충"(US-3.3)을 재검증 산출물에 어떻게 표현할까요?

A) **VerifiedCandidate에 `evidenceSufficient: boolean` + `insufficiencyReason?: string` 필드 추가 (Recommended)** — C6가 순수 판정에 사용, Evidence chain에 사유 노출.

B) Score를 특수 구간(예: null/음수)으로 인코딩

C) 별도 confidence 수치(0~1)로 두고 임계 판정

D) Other

[Answer]: A.

## Question 6 — 랭킹 정렬 & Tie-break
결과 랭킹(AdviceResult.ranking) 정렬 기준은?

A) **Reusability Score 내림차순, 동점 시 assetName 사전순 (Recommended)** — 결정적(deterministic)이라 데모/테스트 재현 가능.

B) Score 내림차순만 (동점 순서 비결정적 허용)

C) State 우선(REUSE>EXTEND>NEEDS REVIEW) 후 Score

D) Other

[Answer]: C. state->score->assetName 순. 

## Question 7 — LLM 경계 (구조화 C1 / 재검증 C5)
MVP 데모에서 C1 구조화와 C5 재검증의 LLM 부분을 어떻게 다룰까요? (기술 중립 — 실제 모델/프롬프트는 NFR 단계)

A) **실제 LLM 호출 (Recommended)** — 자연어 구조화·재검증에 실제 LLM 사용. 단, 데모 재현성을 위해 대표 mock 시나리오는 결정적 fallback/픽스처 병행. (토큰 예산 USD 1,000 내)

B) 전부 스크립트된 mock (LLM 호출 없음) — 완전 결정적, 토큰 0. 데모 안정성 최고, 실제 가치 시연 약함.

C) 구조화(C1)만 실제 LLM, 재검증(C5)은 mock (또는 그 반대)

D) Other

[Answer]: A.

## Question 8 — Mock 데이터 시나리오 범위 (C10)
functional design에서 정의할 대표 mock 자산/시나리오 범위는?

A) **Hero 1개 + Unhappy 3개(권한 제외 / NEEDS REVIEW / DEVELOP) 시나리오를 커버하는 최소 대표 세트 (Recommended)** — 6개 Source 걸쳐 8~12개 자산, stories 예시(forecast-gap-lib 등) 재사용.

B) 각 Source(6개)별 균등 다수 자산으로 폭넓게

C) Hero 시나리오만 (unhappy는 test case에서 별도)

D) Other

[Answer]: A.

## Question 9 — Feedback 기록 범위 (C8, MVP)
피드백(US-4.3 MVP: 수집)의 기록 항목·저장 개념은?

A) **`{resultId, candidateId, verdict(useful|notFit), timestamp}` 를 in-memory/경량 append 기록 (Recommended)** — MVP는 수집만, 선별 반영은 Later(US-5.1).

B) 자유 텍스트 코멘트까지 포함

C) Other

[Answer]: A.
