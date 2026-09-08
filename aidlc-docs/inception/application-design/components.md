# Components — Rebuild or Reuse Advisor

> INCEPTION - Application Design. 고수준 컴포넌트 정의 + 책임 + 인터페이스.
> 설계 결정: Q1(A) 파이프라인 단계별 컴포넌트, Q2(A) 재검증/분류 분리, Q3(A) SourceAdapter+Registry, Q4(A) per-asset 권한, Q5(A) 동기 순차, Q6(A) 소수 논리 엔드포인트.
> 상세 비즈니스 룰/알고리즘은 Functional Design(CONSTRUCTION)에서 확정.

---

## 컴포넌트 개요

| # | Component | 책임 | 근거 |
|---|---|---|---|
| C1 | IntentStructuringComponent | 자연어 Intent → Role/Goal/Function/Data/Output 구조화, 누락 필드 명료화 질문 | FR-2, US-1.2/1.3 |
| C2 | AssetSearchComponent | 구조화 Intent로 Multi-Source 후보 전체 검색 (SourceAdapter 경유) | FR-3, US-2.1 |
| C3 | PermissionFilterComponent | per-asset 권한으로 접근 불가 자산 제외 (재검증 前) | FR-8, US-2.2 |
| C4 | CandidateSelectionComponent | 접근 가능 후보 중 Top-N(3~5) 선별 | US-2.2 |
| C5 | ReVerificationComponent | 상위 후보 LLM 재검증 → Reusability Score + 근거 | FR-4, US-3.1 |
| C6 | DecisionClassifierComponent | Candidate State + Overall Decision 판정 (순수 로직) | FR-5, US-3.2/3.3/3.4 |
| C7 | EvidenceBuilderComponent | 후보별 Evidence chain 구성 (접근 가능 항목만) | FR-7, US-4.2 |
| C8 | FeedbackComponent | 결과 피드백 기록 (MVP: 수집) | FR-9, US-4.3 |
| C9 | SourceAdapter (interface) + MockSourceAdapters | 공통 검색 인터페이스 + 6개 mock 구현 (확장 지점) | NFR-3, FR-3 |
| C10 | MockDataStore | mock assets + mock permission context 제공 | NFR-7 |

---

## C1. IntentStructuringComponent
- **Purpose**: 사용자의 자연어 의도를 검색·판단에 쓸 구조화된 Intent로 변환하고, 필수 필드 누락 시 명료화한다.
- **Responsibilities**:
  - 자연어 입력을 Role/Goal/Function/Data/Output 5필드로 요약(LLM 활용).
  - 5필드 중 하나 이상 누락 시 "의도 불명확"으로 판단하고 누락 필드별 명료화 질문 생성(US-1.3 기준).
  - 사용자 승인된 구조만 다음 단계로 전달.
- **Interface (개념)**: 자연어 text → StructuredIntent(+ 필요 시 ClarificationRequest).

## C2. AssetSearchComponent
- **Purpose**: 구조화 Intent로 여러 Source의 mock 자산 후보 전체를 조회.
- **Responsibilities**:
  - SourceAdapterRegistry의 모든 어댑터에 검색 위임 후 결과 병합.
  - 각 후보에 Source·자산 식별자·요약 메타 유지(US-2.1).
- **Interface**: StructuredIntent → Candidate[] (전체 목록, 필터/선별 前).

## C3. PermissionFilterComponent
- **Purpose**: 사용자가 접근할 수 없는 자산을 재검증 이전에 제외 (권한 확장 금지).
- **Responsibilities**:
  - per-asset 권한 모델(allowedRoles/allowedUsers) + 사용자 permission context로 접근 가능 여부 판정.
  - 제외된 자산과 제외 사유(Evidence)를 별도 기록.
- **Interface**: (Candidate[], PermissionContext) → { accessible: Candidate[], excluded: ExcludedCandidate[] }.

## C4. CandidateSelectionComponent
- **Purpose**: 접근 가능한 후보 중 재검증 대상 Top-N을 선별.
- **Responsibilities**:
  - 검색 관련도 기반 상위 N(기본 3~5) 선별.
  - 접근 가능 후보가 0개이면 그 사실을 명시(Overall=DEVELOP로 이어짐).
- **Interface**: (accessible Candidate[], N) → Candidate[] (Top-N).

## C5. ReVerificationComponent
- **Purpose**: Top-N 후보를 Role/Task 맥락으로 LLM 재검증.
- **Responsibilities**:
  - 각 후보에 Reusability Score + 판단 근거 부여(단순 유사 ≠ 재사용성).
  - Role/Task 맥락 반영을 근거에 드러냄.
- **Interface**: (Top-N Candidate[], StructuredIntent) → VerifiedCandidate[] (score + reasoning).

## C6. DecisionClassifierComponent
- **Purpose**: 재검증 결과로부터 상태를 판정하는 **순수 로직**(PBT 대상, NFR-5).
- **Responsibilities**:
  - 후보별 Candidate State 판정: REUSE / EXTEND EXISTING / NEEDS REVIEW (후보 단위엔 DEVELOP 없음).
  - 근거 부족/상충 시 NEEDS REVIEW(US-3.3).
  - Overall Decision 산출: 적합(REUSE/EXTEND) 후보가 하나도 없으면 DEVELOP, 아니면 후보 종합(US-3.4).
- **Interface**: VerifiedCandidate[] → { candidateStates: Map, overallDecision }.

## C7. EvidenceBuilderComponent
- **Purpose**: 각 판단을 추적 가능한 Evidence chain으로 구성(Black-box 방지).
- **Responsibilities**:
  - 후보별 Source·자산 링크·관련 Evidence·State 근거 결합.
  - 사용자가 접근 가능한 Evidence만 노출(FR-8 연계).
- **Interface**: (VerifiedCandidate[], decisions, PermissionContext) → EvidenceChain[].

## C8. FeedbackComponent
- **Purpose**: 결과에 대한 사용자 피드백 수집(MVP).
- **Responsibilities**: 후보별 피드백(유용/부적합) 기록. (선별 반영은 [Later] US-5.1)
- **Interface**: (resultId, candidateId, feedback) → 기록 확인.

## C9. SourceAdapter (interface) + Mock Adapters
- **Purpose**: Multi-Source 검색의 확장 지점(NFR-3). mock → 실제 Source 전환 시 구현체만 교체.
- **Responsibilities**:
  - 공통 `search(structuredIntent) → Candidate[]` 계약 정의.
  - GitHub/Confluence/Jira/IMS/BizForce/EDM 6개 Mock Adapter가 공통 mock dataset을 Source별로 분리 반환.
- **Interface**: SourceAdapter.search(StructuredIntent) → Candidate[]; SourceAdapterRegistry.getAll().

## C10. MockDataStore
- **Purpose**: 대표성 있는 mock 자산 + per-asset 권한 context 제공(NFR-7).
- **Responsibilities**: mock assets(Source·요약·allowedRoles/allowedUsers 등) + mock user/permission context 저장·조회.
- **Interface**: getAssets(source?), getPermissionContext(userId/role).
