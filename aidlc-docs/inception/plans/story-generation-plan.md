# Story Generation Plan — Rebuild or Reuse Advisor

> Product Owner 역할로 작성. 이 계획은 requirements.md(FR-1..FR-10, NFR-1..NFR-7)를 사용자 중심 스토리로 변환하기 위한 방법론과 결정 사항을 담습니다.
> 아래 **Planning Questions**의 `[Answer]:` 뒤에 letter를 채운 뒤 "완료"라고 알려주세요. 답변이 모두 채워질 때까지 스토리 생성(PART 2)으로 진행하지 않습니다.

---

## A. Story Development Approach (제안)

- **Role**: Product Owner
- **기준**: INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- **Mandatory Artifacts**:
  - [x] `stories.md` — INVEST 기반 사용자 스토리 + 각 스토리 Acceptance Criteria
  - [x] `personas.md` — 사용자 아키타입 및 특성
  - [x] Persona ↔ Story 매핑

**Answers**: Q1=D (Epic + 내부 User Journey), Q2=A (Developer + Business User), Q3=C (GWT + Hero 데이터 예시), Q4=A (전 스토리 MVP/Later 태그), Q5=A (3개 비해피 스토리 포함, 각 mock 1개). Generation complete.

---

## B. Planning Questions

## Question 1
스토리 **Breakdown 방식**은? (requirements의 공통 Reusability 흐름 반영)

A) User Journey 기반 — 사용자 흐름(Intent 입력 → 구조화 → 검색 → 재검증 → 결과/Evidence → 피드백)을 따라 스토리 구성

B) Feature 기반 — 시스템 기능(검색, 분류, 권한 필터, Evidence 등) 단위로 구성

C) Epic 기반 — 상위 Epic 아래 하위 스토리로 계층 구성

D) Hybrid — Epic으로 묶되 각 Epic 내부는 User Journey 순서로 배열

X) Other (please describe after [Answer]: tag below)

[Answer]: D. 전체 스토리는 큰 기능 목적에 따라 Epic으로 묶고, 각 Epic 내부에서는 실제 사용자가 서비스를 이용하는 순서인 Intent 입력 → 검색 → 후보 재검증 → Decision → Evidence 확인 흐름에 맞춰 스토리를 구성한다. 이를 통해 시스템 구조를 쉽게 파악할 수 있으면서도 실제 사용자 경험이 어떻게 연결되는지 한눈에 이해할 수 있다.

## Question 2
MVP에서 모델링할 **Persona 범위**는? (discovery: Developer/Business User 동등)

A) Developer + Business User 2개 (공통 흐름 중심)

B) Developer + Business User + Asset Owner/관리자(권한·자산 출처 관점) 3개

C) 공통 사용자(Persona 무관 단일) 1개 + 이후 확장 표기

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 이번 프로젝트의 핵심 가설이 “직군에 관계없이 Reusability 판단을 지원한다”는 것이므로 두 Persona를 명시하는 게 좋음. Asset Owner/관리자는 MVP 핵심 사용자가 아니어서 넣으면 범위가 불필요하게 넓어짐.

## Question 3
**Acceptance Criteria 형식**은?

A) Given / When / Then (BDD 형식)

B) 체크리스트형 (검증 항목 나열)

C) Given/When/Then + 핵심 스토리에 한해 검증 데이터 예시 추가

X) Other (please describe after [Answer]: tag below)

[Answer]: C. BDD만 쓰는 것보다 실제 mock asset/입력 예시가 있으면 AI-DLC 이후 구현·테스트 연결이 훨씬 명확해짐. 모든 스토리에 데이터를 붙이지 않고 Hero Scenario 중심으로만 적용하면 부담도 작음

## Question 4
MVP 스토리 **범위/우선순위 표기** 방식은? (6시간 제약)

A) 모든 스토리에 MVP / Later 태그를 붙여 Hero Scenario와 확장 범위를 구분

B) MVP 필수 스토리만 작성하고 확장 스토리는 별도 "Future" 섹션에 요약

C) 우선순위 없이 전체 스토리만 나열 (범위 판단은 Workflow Planning에서)

X) Other (please describe after [Answer]: tag below)

[Answer]: A . 모든 스토리에 MVP 또는 Later 태그를 명시하여 이번 해커톤에서 구현할 범위와 향후 확장 범위를 명확하게 구분한다. 6시간이라는 강한 시간 제약이 있기 때문에 구현 과정에서 Scope Creep이 발생하지 않도록 하는 것이 중요하다. 동시에 Later 스토리를 삭제하지 않고 남겨두면 현재 MVP가 전체 서비스 비전에서 어느 위치에 있는지도 보여줄 수 있다.


## Question 5
아래 **엣지/비해피 스토리**를 MVP 스토리에 포함할까요? (discovery Unhappy Path 및 FR-8 반영)

A) 포함 — 권한 없는 자산 제외(FR-8), NEEDS REVIEW 판정, 적합 자산 없음(DEVELOP) 시나리오를 스토리로 명시

B) 핵심 해피 패스만 스토리화하고 엣지는 Acceptance Criteria 안에서만 다룸

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 세 가지 비해피 시나리오는 별도 MVP 스토리로 포함한다. 이들은 일반적인 예외 처리가 아니라 Rebuild or Reuse Advisor가 올바르게 동작하는지를 보여주는 핵심 Business Logic이기 때문이다.

특히 다음 세 가지를 명확하게 검증한다.

권한 없는 자산 제외 — 검색 결과가 좋아도 사용자가 접근할 수 없는 Asset은 추천하지 않는다.
NEEDS REVIEW — Evidence가 부족하거나 판단이 모호하면 AI가 억지로 결론을 내리지 않는다.
DEVELOP — 재사용 가능한 적합 자산이 없으면 신규 개발을 권고한다.

단, MVP 범위를 고려하여 복잡한 예외처리 시스템을 구현하는 것이 아니라 각 시나리오를 검증할 수 있는 대표 Mock Data/Test Case를 1개씩 준비하는 방식으로 최소 구현한다.
