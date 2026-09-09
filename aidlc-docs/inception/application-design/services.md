# Services — Rebuild or Reuse Advisor

> 서비스 정의 + 책임 + 오케스트레이션 패턴.
> 설계 결정: Q5(A) 동기 순차 in-process 파이프라인, Q6(A) 소수 논리 엔드포인트.

---

## S1. AdvisorOrchestratorService (핵심)

- **책임**: Web UI의 단일 진입점. 파이프라인 각 컴포넌트를 **순서대로 in-process 동기 호출**하여 조율. UI는 내부 단계를 직접 호출하지 않는다.
- **논리 엔드포인트 (Q6-A)**:
  1. `submitIntent(rawText)` → 구조화 결과 또는 명료화 요청 반환 (US-1.2/1.3)
  2. `advise(approvedIntent, ctx)` → 검색~Decision~Evidence~**Action Handoff** 일괄 실행, `AdviceResult`(+`actionPrompt?`) 반환 (US-2.1~US-4.2, **US-6.1** CR-001 증분)
  3. `submitFeedback(...)` → 피드백 위임 (US-4.3)
- **advise() 오케스트레이션 순서 (권한 필터가 재검증 前)**:
  ```
  1) AssetSearchComponent.search(intent)                     → Candidate[] (전체)
  2) PermissionFilterComponent.filter(candidates, ctx)       → { accessible, excluded }
  3) CandidateSelectionComponent.selectTopN(accessible, N)   → Top-N
     └ accessible == 0 → Top-N 비고, DEVELOP 경로 표시
  4) ReVerificationComponent.reverify(topN, intent)          → VerifiedCandidate[]
  5) DecisionClassifierComponent.classifyAll(...)            → candidateStates
     DecisionClassifierComponent.deriveOverall(...)          → overallDecision
  6) EvidenceBuilderComponent.build(...)                     → EvidenceChain[]
  7) 랭킹 조립 (ranking = State→Score→name, rank, capabilityMatch)
  8) [CR-001 증분] ActionHandoffBuilder.build(intent, overall, overallRationale, ranking, evidenceChains)
        try  → actionPrompt        (Overall Decision별 목적의 단일 Prompt)
        except → actionPrompt=None (내부 감사 로깅, 비차단 — 기존 결과 유지)
  9) AdviceResult 조립 (ranking, overallDecision, evidenceChains, [+actionPrompt])
  ```
- **오류/경계 처리(개념)**: 접근 가능 후보 0개여도 정상 흐름으로 Overall=DEVELOP 반환. (Production 예외/재시도는 Resiliency skip 범위 밖)
- **Action Handoff 실패 격리(CR-001 §D2)**: C11 예외는 상위로 전파하지 않는다 — Action Prompt 생성 실패 시에도 ranking·overallDecision·evidenceChains는 정상 반환하고 `actionPrompt=None`(응답 `actionHandoff=null`). Action Handoff는 핵심 결과의 선행 조건이 아니다(append-only·비차단, FR-11).

## S2. SourceAdapterRegistry

- **책임**: SourceAdapter 구현체 등록/조회. AssetSearchComponent가 검색 시 `getAll()`로 모든 어댑터 순회. mock → 실제 Source 전환 시 등록 구현체만 교체(NFR-3 확장 지점).
- **오케스트레이션 관여**: 없음(레지스트리 역할). AssetSearchComponent가 사용.

---

## 오케스트레이션 패턴 요약
- **패턴**: 동기 순차 파이프라인 (Orchestrator = 조율자, 컴포넌트 = 단일 책임 단계).
- **이유**: 판단 흐름의 명확성·자기설명성(NFR-1)·디버깅 용이·6h 제약. 비동기/이벤트는 MVP 과설계.
- **상태 관리**: 요청 단위 in-memory 파이프라인 (세션/영속 저장은 MVP 밖, 피드백만 경량 기록).
- **UI 계약**: submitIntent → (사용자 승인) → advise → 결과 화면 → submitFeedback. 단일 화면 UX(NFR-6)와 정합.
