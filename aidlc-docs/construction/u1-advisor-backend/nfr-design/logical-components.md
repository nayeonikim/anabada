# Logical Components — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Design (U1). NFR 설계 패턴을 지탱하는 논리 컴포넌트/인프라 요소와 통합 방식.
> 근거: nfr-design-patterns.md, business-logic-model.md(S1 + C1~C8), tech-stack-decisions.md. Q5=A(최소 구성).
> 구성 원칙: MVP 최소 인프라. Circuit breaker / message queue / 외부 cache 없음.

---

## 1. 컴포넌트 계층 (Logical View)

```
                         ┌─────────────────────────────────────┐
   HTTP (U2) ──────────► │  API Layer (FastAPI)                 │
   /intent /advise       │  - Request models (Pydantic)         │
   /feedback             │  - Public Response DTOs (Pydantic)   │  ◄── Type-Enforced Non-Disclosure
                         └───────────────┬─────────────────────┘
                                         │ (도메인 타입 ↔ DTO 매핑)
                         ┌───────────────▼─────────────────────┐
                         │  S1 AdvisorOrchestratorService       │  (동기 순차 오케스트레이션)
                         └──┬───┬───┬───┬───┬───┬───┬───────────┘
        ┌───────────┬───────┘   │   │   │   │   │   └──────────────┐
        ▼           ▼           ▼   ▼   ▼   ▼   ▼                  ▼
   C1 Structure  AssetSearch  Perm  Cand  ReVerif  Decision   Evidence   C8 Feedback
   (LLM)         Component    Filter Select (LLM)  Classifier Builder    Component
        │           │                          │   (순수/PBT)              │
        │           │                          │                          │
   ┌────▼────┐ ┌────▼──────────────┐     ┌─────▼─────┐            ┌────────▼────────┐
   │LLMClient│ │SourceAdapterReg-  │     │LLMClient  │            │ FeedbackStore   │
   │(+Fixture│ │istry(config-driven)│    │(+Fixture) │            │ (JSONL, 영속)   │
   │Provider)│ │  └─ SourceAdapter[]│     └───────────┘            └─────────────────┘
   └─────────┘ └────┬───────────────┘
                    ▼
              AssetRepository (in-memory, JSON 로드)

   ─────────────── 횡단(cross-cutting) ───────────────
   Config 모듈 (env/config)      StructuredLogger (+ 내부 감사 로그)
```

---

## 2. 컴포넌트 카탈로그

### 2.1 API Layer (FastAPI)
- **책임**: `/intent`, `/advise`, `/feedback` 엔드포인트. 요청 검증(Pydantic), 도메인 호출, **공개 응답 DTO로 매핑·직렬화**.
- **NFR**: NFR-M1(자동 OpenAPI 문서), NFR-U1(계약 명확성), NFR-SEC2(응답 DTO 경계로 비노출 강제).
- **핵심**: 공개 Response DTO는 내부 타입(ExcludedCandidate/제외 개수/플래그)을 **필드로 갖지 않음**.

### 2.2 S1 AdvisorOrchestratorService
- **책임**: submitIntent / advise / submitFeedback 흐름의 동기 순차 오케스트레이션(business-logic-model 3장).
- **NFR**: NFR-P4(순차 in-process), NFR-A2(실패 매트릭스에 따른 흐름 제어 — C1 실패→오류, C5 전체 실패→오류, 일부 실패→후보 강등).

### 2.3 C1 StructureComponent (LLM)
- **책임**: rawText → StructuredIntent(5필드). 실패 시 **명확한 오류**(폴백 없음, demoMode ON은 fixture/미매칭 오류).
- **의존**: LLMClient. **NFR**: NFR-A2, NFR-C2.

### 2.4 AssetSearchComponent
- **책임**: SourceAdapterRegistry 순회 → Evidence 수집 → asset 단위 Candidate 집계 + relevance 부여.
- **의존**: SourceAdapterRegistry, AssetRepository. **NFR**: NFR-S2.

### 2.5 PermissionFilterComponent
- **책임**: per-asset 접근 판정(BR-PERMISSION), 미인가 → ExcludedCandidate 분리. **초기 단일 스테이지**.
- **NFR**: NFR-SEC1(필터), NFR-SEC4(내부 감사 로그 기록). 권한 확장 금지.

### 2.6 CandidateSelectionComponent
- **책임**: 접근 가능 후보 중 Top-N(config, 기본 3) 선별. 접근 가능 0개 → DEVELOP 경로 플래그.
- **NFR**: NFR-P3(Bounded Fan-out).

### 2.7 ReVerificationComponent (LLM)
- **책임**: Top-N 후보를 LLM 재검증 → reusabilityScore/reasoning/roleTaskContextNote/evidenceSufficient.
- **실패 처리(NFR-A2)**: 일부 후보 실패 → 해당 후보 `NEEDS_REVIEW(stateReason=TECHNICAL_FAILURE)`; 전체 실패 → 오류 응답.
- **의존**: LLMClient. **NFR**: NFR-A2, NFR-C1.

### 2.8 DecisionClassifierComponent (순수 로직, PBT)
- **책임**: classifyAll(verified) → CandidateState(+stateReason), deriveOverall → OverallDecision.
- **핵심 규칙**: TECHNICAL_FAILURE NEEDS_REVIEW는 **DEVELOP 신호로 사용 안 함**(nfr-design-patterns 1.3).
- **NFR**: NFR-T1/T2(순수·결정적·PBT), NFR-A2.

### 2.9 EvidenceBuilderComponent
- **책임**: 접근 가능 후보의 Evidence[] → EvidenceChain. NEEDS_REVIEW는 stateRationale에 사유 포함(기술 실패/근거 부족 구분).
- **NFR**: FR-7, NFR-SEC3(미인가 근거 미포함).

### 2.10 C8 FeedbackComponent
- **책임**: (resultId, candidateId, verdict) 기록 → FeedbackStore append, 확인 id 반환.
- **의존**: FeedbackStore. **NFR**: NFR-A4(영속).

---

## 3. 인프라/횡단 논리 컴포넌트 (Q5=A 최소 구성)

| 컴포넌트 | 책임 | 통합 방식 | NFR |
|---|---|---|---|
| **Config 모듈** | 임계값·topN·demoMode·LLM 설정·경로·로그 레벨 단일 소스. env override. | 시작 시 로드, DI로 각 컴포넌트에 주입. | NFR-S4, NFR-M3 |
| **LLMClient (추상화)** | Bedrock Claude 호출 인터페이스. 타임아웃 config. | C1/C5가 의존. **FixtureProvider**로 대체 가능(demoMode/테스트). | NFR-T3, NFR-A2, NFR-S3 |
| **FixtureProvider** | 대표 시나리오 결정적 응답. 미매칭 입력 → 명시적 오류(demoMode ON). | LLMClient 구현/데코 형태로 주입. | NFR-A3, NFR-C2 |
| **SourceAdapterRegistry** | config 선언 adapter 목록 로드·제공. | AssetSearch가 인터페이스로 소비. 신규 Source=Adapter+config. | NFR-S2, NFR-3 |
| **SourceAdapter[] (mock)** | 6개 Source 대표 mock 검색 → Evidence[]. | 인터페이스 구현체. | NFR-7, NFR-S2 |
| **AssetRepository (in-memory)** | mock Asset/Evidence JSON 로드 → read-only in-memory 제공. | 시작 시 로드, DI 주입. | NFR-2 |
| **FeedbackStore (JSONL)** | 피드백 append-only JSONL 기록·로드. **재시작 후 유지**. | C8이 의존. 경로 config. | NFR-A4 |
| **StructuredLogger** | 구조화 로그(요청ID·단계) + **서버 내부 제외 감사 로그**. | 횡단 주입. 외부 관측 스택 없음. | NFR-M2, NFR-SEC4 |

**의도적 미포함**(Q5=A): Circuit breaker, retry decorator, message queue, 외부 cache, DB. (MVP 비목표)

---

## 4. 데이터 흐름 상 컴포넌트 협력 (advise)

```
API(request DTO) → S1.advise
  → AssetSearch(Registry→Adapters→Repository)         : Candidate[]
  → PermissionFilter(ctx)                             : accessible / excluded(내부, 감사 로그)
  → CandidateSelection(topN)                          : Top-N
  → ReVerification(LLMClient|Fixture)                 : Verified[] (실패→NEEDS_REVIEW/TECHNICAL_FAILURE or 오류)
  → DecisionClassifier(순수)                           : states(+reason) + Overall(기술실패↛DEVELOP)
  → EvidenceBuilder                                   : EvidenceChain[]
  → S1 assemble → 공개 Response DTO (excluded 미포함)   : AdviceResult
StructuredLogger: 전 단계 요청ID·소요·제외 감사(내부)
```

---

## 5. 교체 경계 요약 (mock → 실제)

| 경계 | MVP | 확장 시 |
|---|---|---|
| SourceAdapter | mock adapter(JSON) | 실제 GitHub/Confluence/Jira/IMS/BizForce/EDM adapter |
| PermissionContext 제공 | mock user/permission | 실제 AD SSO |
| LLMClient | Bedrock Claude(+Fixture) | 동일 인터페이스, 모델/설정만 변경 |
| AssetRepository | in-memory JSON | 실제 검색/인덱스 백엔드 |
| FeedbackStore | JSONL 파일 | DB/메시지 파이프라인 |

> 모든 교체는 인터페이스·DI 경계에서 이루어져 코어 로직 무변경(NFR-S2/S3).
