# Unit of Work — Rebuild or Reuse Advisor

> INCEPTION - Units Generation. 유닛 정의 + 책임 + Greenfield 코드 조직 전략.
> 결정: Q1(A) 2 유닛, Q2(A) 로컬 HTTP API, Q3(A) 백엔드 먼저, Q4(A) `backend/`+`frontend/`, Q5(A) mock 데이터/Adapter는 U1 내부.

---

## 유닛 개요

| Unit | 이름 | 성격 | per-unit 루프 순서 |
|---|---|---|---|
| **U1** | Advisor Backend (Reusability Pipeline) | 백엔드 로직 + LLM 연동 + mock 데이터 | **1순위 (먼저 완성)** |
| **U2** | Web UI (Single-Screen Advisor) | 프론트엔드 단일 화면 | 2순위 (U1 API 확정 후) |

---

## U1 — Advisor Backend (Reusability Pipeline)

- **책임**: Hero 파이프라인 전체를 백엔드에서 수행. 자연어 Intent 구조화 → Multi-Source 검색 → per-asset 권한 필터 → Top-N 선별 → LLM 재검증 → Candidate State/Overall Decision 분류 → Evidence chain 구성 → 피드백 수집.
- **포함 컴포넌트**: C1 IntentStructuring, C2 AssetSearch, C3 PermissionFilter, C4 CandidateSelection, C5 ReVerification, C6 DecisionClassifier(순수/PBT), C7 EvidenceBuilder, C8 Feedback, C9 SourceAdapter+6 Mock Adapters, C10 MockDataStore, S1 AdvisorOrchestratorService, S2 SourceAdapterRegistry.
- **노출 인터페이스 (U2 대상, Q6-A / Q2-A)**: 로컬 HTTP API 3개 — `POST /intent`(submitIntent: 구조화/명료화), `POST /advise`(검색~Decision~Evidence 일괄), `POST /feedback`.
- **mock 데이터/Adapter (Q5-A)**: C9/C10은 U1 내부에 포함 (검색·권한 로직과 결합도 높음).
- **테스트 초점**: C6 DecisionClassifier 순수 로직 PBT(NFR-5) + 3개 Unhappy 대표 mock 케이스(권한 제외 / NEEDS REVIEW / DEVELOP).
- **담당 스토리**: US-1.1(접수), US-1.2, US-1.3(명료화 로직), US-2.1, US-2.2, US-3.1, US-3.2, US-3.3, US-3.4, US-4.2(Evidence 구성), US-4.3(피드백 기록). Later 위치: US-5.1/US-5.2.

## U2 — Web UI (Single-Screen Advisor)

- **책임**: 단일 화면(NFR-6)에서 Search → Compare → Decide → Evidence 흐름 전달. 자연어 Intent 입력, 구조화 결과/명료화 질문 표시·응답, 후보 랭킹(Source·Score·Candidate State)·Overall Decision·Evidence chain 비교, 피드백 입력.
- **의존**: U1의 HTTP API 3개에만 의존 (내부 파이프라인 은닉).
- **담당 스토리**: US-1.1(입력 UI), US-1.3(명료화 UI), US-4.1(랭킹 화면), US-4.2(Evidence 표시), US-4.3(피드백 UI).
- **테스트 초점**: 대표 mock 시나리오 렌더링(Hero + 3 Unhappy) 시각 확인.

---

## Greenfield 코드 조직 전략 (Q4-A)

- **저장소**: 단일 저장소(현 워크스페이스 루트). 애플리케이션 코드는 루트에 배치(문서는 `aidlc-docs/`에만).
- **디렉터리 구조 (제안, 상세 스택은 NFR 단계에서 확정)**:
  ```
  <workspace-root>/
  ├── backend/        # U1 — Advisor pipeline (C1-C10, S1/S2), mock data & adapters, tests
  │   ├── (구조화/검색/권한/선별/재검증/분류/evidence/feedback 모듈)
  │   ├── adapters/   # C9 6 mock source adapters + registry
  │   ├── mockdata/   # C10 mock assets + permission context
  │   └── tests/      # C6 PBT + unhappy 시나리오
  ├── frontend/       # U2 — single-screen web UI
  └── aidlc-docs/     # 문서 전용 (코드 없음)
  ```
- **유닛↔폴더 1:1 대응**: U1 ↔ `backend/`, U2 ↔ `frontend/`.
- **통합**: U2가 U1의 로컬 HTTP API 호출(Q2-A). 개발 순서는 U1 → U2(Q3-A)로 API 계약 선확정.
