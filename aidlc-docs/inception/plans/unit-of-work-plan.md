# Unit of Work Plan — Rebuild or Reuse Advisor

> Stage: INCEPTION - Units Generation (Part 1: Plan + Questions)
> 근거: application-design.md(C1-C10, S1-S2), stories.md(5 Epic / 15 story), execution-plan.md(경량 1~2 유닛 권장).
> 목적: 시스템을 개발 단위(Unit of Work)로 분해. Greenfield → 코드 조직 전략 포함.
> 제약: 해커톤 MVP ~6h, 동기 순차 in-process 파이프라인, per-unit 루프 반복 최소화.

---

## Part A — 유닛 분해 초안 (Proposed)

Application Design의 동기 in-process 파이프라인 + 단일 화면 UX를 반영한 **2 유닛** 초안입니다.

| Unit | 이름 | 포함 컴포넌트 | 담당 스토리 | 성격 |
|---|---|---|---|---|
| **U1** | Advisor Backend (Reusability Pipeline) | C1~C10 + S1/S2 (Orchestrator, 구조화, 검색, 권한필터, Top-N, 재검증, 분류, Evidence, 피드백, Adapters, MockStore) | US-1.1~1.3, US-2.1/2.2, US-3.1~3.4, US-4.2/4.3, US-5.x(Later 위치) | 백엔드 로직 + LLM 연동 + mock 데이터 |
| **U2** | Web UI (Single-Screen Advisor) | Web UI (Intent 입력, 구조화 확인, 랭킹/Overall/Evidence 비교, 피드백) | US-1.1(입력 UI), US-4.1(랭킹 화면), US-4.2(Evidence 표시), US-4.3(피드백 UI), US-1.3(명료화 UI) | 프론트엔드 단일 화면 |

> **경계 원칙**: U2는 U1의 논리 엔드포인트(submitIntent/advise/submitFeedback)에만 의존. 내부 파이프라인 단계는 U1이 은닉(Q6-A 정합). 일부 스토리(US-1.1, US-1.3, US-4.2)는 백엔드 처리(U1)와 화면 표현(U2)에 걸쳐 있어 양쪽에 매핑.

---

## Part B — 실행 체크리스트

### Plan (Part 1)
- [x] 컨텍스트 분석 (application-design + stories) — 완료
- [x] 유닛 분해 초안 작성 — 완료 (Part A)
- [x] 분해 결정 질문 작성 (Part C) — 완료
- [x] 사용자 답변 수집 — 완료 (Q1~Q5 모두 A, 전부 권장 승인)
- [x] 답변 분석 (모호/모순 확인) 및 필요시 후속 질문 — 완료 (모호/모순 없음, 후속 불필요)

### Generation (Part 2) — 승인 후 생성할 필수 산출물
- [x] `application-design/unit-of-work.md` — 유닛 정의 + 책임 + **Greenfield 코드 조직 전략**
- [x] `application-design/unit-of-work-dependency.md` — 유닛 간 의존성 매트릭스
- [x] `application-design/unit-of-work-story-map.md` — 스토리↔유닛 매핑 (모든 스토리 할당 확인)
- [x] 유닛 경계·의존성 검증, 전 스토리 할당 검증

---

## Part C — 분해 결정 질문 (Please fill [Answer]: tags)

> 각 질문에 권장안(Recommended)을 제시했습니다. 권장안대로면 해당 letter만 적으시면 됩니다.

## Question 1
유닛 분해 개수/경계를 어떻게 할까요?

A) **2 유닛 (U1 Advisor Backend + U2 Web UI)** — 위 Part A 초안. 백엔드/프론트 관심사 분리, per-unit 루프 2회로 6h 관리 가능. **(Recommended)**

B) 1 유닛 (풀스택 단일 유닛) — 루프 1회로 최소화. 단 백엔드 로직과 UI 관심사가 한 설계에 섞임.

C) 3+ 유닛 (예: 파이프라인 / 데이터·Adapter / UI 분리) — 경계는 깔끔하나 6h에 루프 과다.

D) Other (please describe after [Answer]: tag below)

[Answer]: A (사용자 승인: 전부 권장으로 진행)

## Question 2
유닛 간 통합(연동) 방식을 어떻게 할까요?

A) **로컬 HTTP API (U2 → U1의 소수 엔드포인트 호출)** — 프론트/백엔드 표준 분리, 실제 Source 전환에도 자연스러움. **(Recommended)**

B) 단일 프로세스 in-process 호출 (UI와 백엔드가 같은 런타임, 함수 직접 호출) — 가장 단순하나 배포·확장 유연성 낮음.

C) Other (please describe after [Answer]: tag below)

[Answer]: A (사용자 승인: 전부 권장으로 진행)

## Question 3
per-unit 루프(Functional/NFR/Code Gen) 진행 순서를 어떻게 할까요?

A) **U1(백엔드) 먼저 완성 → U2(UI) 진행** — UI가 의존하는 API 계약이 먼저 확정되어 안정적. **(Recommended)**

B) U2(UI) 먼저 → U1(백엔드) — UI/UX 먼저 확정 후 백엔드 맞춤. mock 응답으로 UI 선개발.

C) Other (please describe after [Answer]: tag below)

[Answer]: A (사용자 승인: 전부 권장으로 진행)

## Question 4 (Greenfield 코드 조직 전략)
저장소/디렉터리 구조를 어떻게 둘까요? (워크스페이스 루트에 애플리케이션 코드 배치)

A) **단일 저장소, 최상위 `backend/` + `frontend/` 분리** — 2 유닛과 1:1 대응, 단순·표준. **(Recommended)**

B) 단일 저장소 통합 구조 (프레임워크 풀스택 하나, 예: Next.js 내부에 API routes) — 유닛 경계가 폴더로만 구분.

C) 별도 저장소 2개 (backend repo / frontend repo) — MVP 해커톤엔 과함.

D) Other (please describe after [Answer]: tag below)

[Answer]: A (사용자 승인: 전부 권장으로 진행)

## Question 5
mock 데이터/Adapter(C9/C10)의 소속을 어디로 둘까요?

A) **U1(백엔드) 내부에 포함** — Adapter/MockDataStore는 검색·권한 로직과 결합도가 높아 백엔드 소속이 자연스러움. **(Recommended)**

B) 별도 공유 모듈로 분리 — 재사용성은 있으나 MVP엔 과분할.

C) Other (please describe after [Answer]: tag below)

[Answer]: A (사용자 승인: 전부 권장으로 진행)
