# Application Design Plan — Rebuild or Reuse Advisor

> Stage: INCEPTION - Application Design (Part 1: Plan + Questions)
> 근거: requirements.md(FR-1..10, NFR-1..7), stories.md(5 Epic / 15 story), personas.md(P1/P2), execution-plan.md.
> 목적: 신규 시스템의 **고수준 컴포넌트 식별 + 서비스 계층 + 컴포넌트 인터페이스/의존성** 설계. (상세 비즈니스 로직은 이후 Functional Design에서 확정)
> 제약: 해커톤 MVP ~6h, mock 데이터, Source Adapter 확장 구조(NFR-3), 단일 화면(NFR-6).

---

## Part A — 컴포넌트 구조 초안 (Proposed — 질문 답변으로 확정)

Hero 흐름(자연어 Intent → 구조화 → 검색 → **권한 필터** → Top-N → LLM 재검증 → Candidate State/Overall Decision → 랭킹+Evidence)을 컴포넌트로 분해한 초안입니다.

```
[Web UI]
   │  (자연어 Intent, 구조화 확인, 결과/Evidence, 피드백)
   ▼
[Advisor Orchestrator Service]  ── 파이프라인 조율
   ├─ 1. IntentStructuringComponent   (FR-2, US-1.2/1.3)  자연어→Role/Goal/Function/Data/Output, 누락필드 명료화
   ├─ 2. AssetSearchComponent         (FR-3, US-2.1)      Source Adapter 통해 후보 전체 검색
   │        └─ SourceAdapter (interface) → GitHub/Confluence/Jira/IMS/BizForce/EDM Mock Adapters (NFR-3)
   ├─ 3. PermissionFilterComponent    (FR-8, US-2.2)      mock permission context로 접근불가 자산 제외 (재검증 前)
   ├─ 4. CandidateSelectionComponent  (US-2.2)            접근가능 후보 중 Top-N(3~5) 선별
   ├─ 5. ReVerificationComponent      (FR-4, US-3.1)      LLM 재검증 → Reusability Score + 근거
   ├─ 6. DecisionClassifierComponent  (FR-5, US-3.2/3.3/3.4) Candidate State + Overall Decision
   ├─ 7. EvidenceBuilderComponent     (FR-7, US-4.2)      후보별 Evidence chain 구성
   └─ 8. FeedbackComponent            (FR-9, US-4.3)      피드백 기록 (MVP: 수집만)

[Mock Data Store]  ── mock assets + mock permission context (NFR-7)
```

**Service 계층 초안**: `AdvisorOrchestratorService`(파이프라인 조율, 단일 진입점), `SourceAdapterRegistry`(어댑터 등록/조회).

---

## Part B — 실행 체크리스트

### Plan (Part 1)
- [ ] 컨텍스트 분석 (requirements + stories) — 완료
- [ ] 컴포넌트 구조 초안 작성 — 완료 (Part A)
- [ ] 설계 결정 질문 작성 (Part C) — 완료
- [ ] 사용자 답변 수집
- [ ] 답변 분석 (모호/모순 확인) 및 필요시 후속 질문

### Generation (Part 2) — 답변 승인 후 실행할 필수 산출물
- [ ] `application-design/components.md` — 컴포넌트 정의 + 고수준 책임 + 인터페이스
- [ ] `application-design/component-methods.md` — 메서드 시그니처 + I/O 타입 (비즈니스 룰 상세는 Functional Design)
- [ ] `application-design/services.md` — 서비스 정의 + 오케스트레이션 패턴
- [ ] `application-design/component-dependency.md` — 의존성 매트릭스 + 통신 패턴 + 데이터 흐름
- [ ] `application-design/application-design.md` — 위 문서 통합본
- [ ] 설계 완전성·정합성 검증

---

## Part C — 설계 결정 질문 (Please fill [Answer]: tags)

> 각 질문에 권장안(Recommended)을 함께 제시했습니다. 권장안 그대로 진행하려면 해당 letter를 적으시면 됩니다.

## Question 1
컴포넌트 조직/그룹핑 전략을 어떻게 할까요? (execution-plan의 Units Generation 방향과 연결됨)

A) **파이프라인 단계별 개별 컴포넌트 + 단일 Orchestrator Service** (위 Part A 초안 그대로). 각 단계가 독립 컴포넌트라 테스트·설명이 쉬움. **(Recommended)**

B) 기능을 3개 묶음으로 그룹핑 — Intake(구조화), Retrieval(검색+권한+Top-N), Reasoning(재검증+Decision+Evidence). 컴포넌트 수 감소로 6h에 유리.

C) Other (please describe after [Answer]: tag below)

[Answer]: A. 파이프라인 단계별로 나누면 Intent → Search → Permission → Top-N → ReVerification → Decision → Evidence가 코드 구조에 그대로 드러나서 테스트와 설명이 쉽습니다. 컴포넌트 수는 많아 보이지만 실제 구현은 작은 함수/클래스 수준으로 두면 6시간 내 가능합니다. 심사 시에도 구조가 가장 자기설명적입니다.

## Question 2
LLM 재검증(ReVerificationComponent)과 Decision 분류(DecisionClassifierComponent)를 분리 유지할까요, 통합할까요?

A) **분리 유지** — 재검증(Score+근거 산출)과 분류(State 판정)는 책임이 다르고, 분류 로직은 순수 로직이라 PBT(NFR-5) 대상으로 삼기 좋음. **(Recommended)**

B) 통합 — LLM 한 번 호출로 Score·근거·State를 함께 산출. 토큰/호출 절감(NFR-2)에 유리하나 순수 분류 로직 분리가 어려워짐.

C) Other (please describe after [Answer]: tag below)

[Answer]: A. LLM은 “재사용 가능성 평가와 근거 생성”, DecisionClassifier는 “정해진 기준으로 State 결정”에 집중하게 됩니다. 특히 Decision 로직을 LLM 밖의 순수 로직으로 두면 결과 일관성이 좋아지고 테스트(PBT)도 쉬워집니다.

## Question 3
SourceAdapter 인터페이스의 확장 형태(NFR-3)를 어떻게 설계할까요?

A) **공통 `SourceAdapter` 인터페이스(search(structuredIntent) → Candidate[]) + Registry**, 6개 Mock Adapter가 구현. 실제 Source/SSO 전환 시 구현체만 교체. **(Recommended)**

B) 단일 `MockAssetRepository`가 6개 Source를 내부적으로 처리 (어댑터 인터페이스 없음). 구현은 빠르나 NFR-3 확장성 시연 약화.

C) Other (please describe after [Answer]: tag below)

[Answer]: A. 지금은 mock이지만 나중에 실제 GitHub/Confluence 등으로 바꿀 때 Adapter 구현만 교체할 수 있습니다. NFR-3의 확장성을 가장 간단하게 보여주는 구조입니다. 단, 6개 Adapter 모두 복잡하게 만들 필요 없이 동일한 공통 Mock Dataset을 Source별로 분리해 반환하는 수준이면 충분합니다.

## Question 4
권한 필터(FR-8, A-2 이월결정)의 권한 모델 단위를 확정합니다. execution-plan 권장안 재확인입니다.

A) **자산 단위(per-asset) 권한 모델** — 각 mock 자산이 허용 Role/User 목록을 가지며 Source 단위 접근은 자산 단위에서 파생. 별도 Source-level 정책 레이어 없음. **(Recommended, A-2 권장안)**

B) Source 단위(per-source) 권한 — Role별 접근 가능한 Source 집합을 정의하고 자산은 소속 Source 권한을 상속.

C) 2단계(Source-level + asset-level 오버라이드) 혼합 모델.

D) Other (please describe after [Answer]: tag below)

[Answer]: A. 자산 단위 권한이 가장 단순하면서도 실제 권한 필터 동작을 보여주기 좋습니다. 예를 들어 Asset마다 allowedRoles 또는 allowedUsers만 두면 됩니다. Source-level + Asset-level 혼합은 MVP에는 과합니다.

## Question 5
컴포넌트 간 통신/조율 패턴을 어떻게 할까요?

A) **동기 순차 파이프라인** — Orchestrator가 각 컴포넌트를 순서대로 in-process 호출. 단순·디버깅 용이, 6h MVP에 적합. **(Recommended)**

B) 이벤트/메시지 기반 비동기 파이프라인 — 확장성은 높으나 MVP 과설계 위험.

C) Other (please describe after [Answer]: tag below)

[Answer]: A. 동기 순차 호출이 가장 적합합니다. 이 서비스의 핵심은 실시간 대규모 처리보다 판단 흐름의 명확성입니다. 비동기 이벤트 구조는 6시간 해커톤에서는 과설계입니다. 디버깅도 순차 파이프라인이 훨씬 쉽습니다.

## Question 6
Web UI ↔ 백엔드 인터페이스 경계(컴포넌트 관점)를 어떻게 둘까요? (상세 API 계약은 Functional Design)

A) **단일 백엔드 진입점(AdvisorOrchestratorService)에 대해 소수 논리적 엔드포인트** — ① Intent 제출/구조화, ② 구조화 승인 후 advise(검색~Decision~Evidence 일괄), ③ 피드백. 단일 화면(NFR-6)에 맞음. **(Recommended)**

B) 파이프라인 단계별로 세분화된 엔드포인트(구조화/검색/필터/재검증/결과 각각) — 단계별 제어는 좋으나 왕복 증가.

C) Other (please describe after [Answer]: tag below)

[Answer]: A. UI가 각 내부 단계를 직접 호출할 필요가 없습니다. Intent 구조화와 Advise 실행, Feedback 정도만 외부 인터페이스로 두고 내부 단계는 Orchestrator가 책임지게 하는 게 깔끔합니다. 단일 화면 UX와도 잘 맞습니다.
