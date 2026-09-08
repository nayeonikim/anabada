# Application Design — Rebuild or Reuse Advisor (통합본)

> INCEPTION - Application Design 통합 문서. 상세 산출물: [components.md](components.md), [component-methods.md](component-methods.md), [services.md](services.md), [component-dependency.md](component-dependency.md).
> 근거: requirements.md(FR-1..10, NFR-1..7), stories.md(5 Epic), personas.md(P1/P2).
> 목적: 고수준 컴포넌트/서비스/인터페이스/의존성 정의. **상세 비즈니스 룰·데이터 스키마·기술스택은 이후 Functional Design / NFR 단계에서 확정.**

---

## 1. 설계 결정 요약 (Application Design Questions)

| Q | 결정 | 영향 |
|---|---|---|
| Q1 | 파이프라인 단계별 개별 컴포넌트 + 단일 Orchestrator | 자기설명적 구조, 단계별 테스트 용이 |
| Q2 | ReVerification(LLM)과 DecisionClassifier(순수) 분리 | 결과 일관성 ↑, C6를 PBT 대상화(NFR-5) |
| Q3 | 공통 SourceAdapter 인터페이스 + Registry, 6 Mock Adapter | NFR-3 확장성 시연, 실제 Source 전환 격리 |
| Q4 | per-asset 권한 모델(allowedRoles/allowedUsers) | A-2 이월결정 확정, 단순·시연 용이 |
| Q5 | 동기 순차 in-process 파이프라인 | 흐름 명확성·디버깅·6h 적합 |
| Q6 | 소수 논리 엔드포인트(submitIntent/advise/feedback) | 단일 화면 UX(NFR-6) 정합 |

**이월 결정 A-2 종결**: 권한 모델 단위 = per-asset. (별도 Source-level 정책 레이어 없음)

---

## 2. 아키텍처 개요

```
 [Web UI]  --(single entry)-->  [AdvisorOrchestratorService]
                                        |
   순차 조율: C1 구조화 -> C2 검색 -> C3 권한필터 -> C4 Top-N -> C5 재검증(LLM) -> C6 분류(순수) -> C7 Evidence
                                        |            |                                                |
                              [SourceAdapterRegistry]|                                       [MockDataStore]
                                        |            +--(reads)---------------------------------> (assets+perms)
                              [6 Mock SourceAdapters]
   피드백: C8 Feedback
```
- **권한 필터는 LLM 재검증 이전**(stories.md authoritative, C-1 분기 반영).
- **Candidate State**(REUSE/EXTEND/NEEDS REVIEW, 후보별) 와 **Overall Decision**(+DEVELOP, 요청 전체) 분리(C-2 분기 반영).

## 3. 컴포넌트 (요약)

C1 IntentStructuring · C2 AssetSearch · C3 PermissionFilter · C4 CandidateSelection · C5 ReVerification · C6 DecisionClassifier(순수/PBT) · C7 EvidenceBuilder · C8 Feedback · C9 SourceAdapter+MockAdapters · C10 MockDataStore. 상세는 [components.md](components.md).

## 4. 서비스 (요약)

S1 AdvisorOrchestratorService(동기 순차 조율, 엔드포인트 3개), S2 SourceAdapterRegistry(확장 지점). advise() 순서 및 오케스트레이션은 [services.md](services.md).

## 5. 의존성 (요약)

Web UI → Orchestrator(단일 의존). C6은 외부 의존 없는 순수 로직. C10은 C3/C7/C9 공유 데이터 소스. 확장 지점(C9/S2)이 상위 파이프라인을 격리. 매트릭스·데이터 흐름은 [component-dependency.md](component-dependency.md).

## 6. 요구사항 커버리지

| 요구/스토리 | 담당 |
|---|---|
| FR-1, FR-10 | Web UI, S1(submitIntent/advise) |
| FR-2, US-1.2/1.3 | C1 IntentStructuring |
| FR-3, US-2.1, NFR-3 | C2 AssetSearch, C9 Adapters, S2 Registry |
| FR-8, US-2.2 (권한) | C3 PermissionFilter (per-asset) |
| US-2.2 (Top-N) | C4 CandidateSelection |
| FR-4, US-3.1 | C5 ReVerification |
| FR-5, US-3.2/3.3/3.4 | C6 DecisionClassifier (Candidate State + Overall Decision) |
| FR-7, US-4.2, NFR-1 | C7 EvidenceBuilder |
| FR-9, US-4.3 | C8 Feedback (MVP: 수집) |
| NFR-5 | C6 순수 로직 PBT 대상 |
| NFR-6 | S1 소수 엔드포인트 + 단일 화면 |
| NFR-7 | C10 MockDataStore |

## 7. 후속 단계로 이월 (Functional Design / NFR)
- **Functional Design**: 데이터 스키마 상세(StructuredIntent/Asset/EvidenceChain 필드 확정), C6 분류 규칙(Score 임계·NEEDS REVIEW 트리거), Top-N의 N 확정(기본 3~5, A-3), 관련도 산정 방식.
- **NFR Requirements/Design**: 기술스택(Web+백엔드+LLM 연동), C6 PBT 적용 지점, mock dataset 대표성 구성, 단일 화면 UX 패턴.
- **Units Generation**: 본 설계 기준 유닛 분해(권장 1~2: Advisor 백엔드 / Web UI).

## 8. 정합성 참고 (Consistency)
- C-1/C-2 불일치는 User 결정(C)에 따라 requirements.md 미수정. **본 설계는 stories.md(authoritative)를 따른다**: 권한 필터가 재검증 前, Candidate State(3)와 Overall Decision(4) 분리.
