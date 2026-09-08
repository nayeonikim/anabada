# NFR Design Patterns — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Design (U1). NFR 요구를 구체적 설계 패턴으로 구현.
> 근거: nfr-requirements.md, tech-stack-decisions.md, business-logic-model.md(S1 + C1~C8), NFR Design plan(Q1~Q5).
> 확장: Security/Resiliency blocking 미적용. 아래 패턴은 MVP 범위의 경량 적용.

---

## 0. 설계 원칙 요약

- **단순·결정적 우선**: 동기 순차 in-process, 상태 최소화. 회복성/성능 패턴은 MVP에 필요한 최소만.
- **경계 격리**: LLM·Source·저장을 인터페이스 뒤로 격리(확장성/테스트성).
- **타입으로 보안 강제**: 미인가 정보 비노출을 관례가 아닌 타입(응답 DTO) 경계로 강제.
- **실패 투명성**: 기술적 실패를 비즈니스 판정(DEVELOP)으로 오해하지 않도록 명확히 구분.

---

## 1. Resilience Patterns (회복성) — Q1=C, NFR-A2

### 1.1 No-Retry + Config Timeout (재시도 없음, 타임아웃 config)
- LLM 호출(C1 structure, C5 reverify)은 **재시도하지 않는다**. 타임아웃은 config(`LLM_TIMEOUT_SECONDS`)로 관리하며 초과 시 실패로 처리.
- 근거: MVP 단순성 + 예측 가능한 지연. 재시도로 인한 토큰/지연 증가 회피.

### 1.2 실패 처리 매트릭스 (핵심 결정)

| 지점 | 실패 범위 | 처리 | Overall 영향 |
|---|---|---|---|
| **C1 structure()** | 실패/타임아웃 | **명확한 오류 응답 반환** (요청 종료, 폴백 없음) | N/A (advise 진입 전) |
| **C5 reverify()** | **일부 후보** 실패 | 해당 후보를 **`NEEDS_REVIEW`(reason=TECHNICAL_FAILURE)** 로 처리 | **DEVELOP 산출 금지** — 기술 실패를 재사용 부적합으로 간주하지 않음 |
| **C5 reverify()** | **전체 후보** 실패 | **명확한 오류 응답 반환** (부분 결과로 위장하지 않음) | N/A (오류 응답) |

### 1.3 Technical-Failure NEEDS_REVIEW 구분 (deriveOverall 함의)
- **문제**: 기존 BR-OVERALL은 접근 가능 후보가 없거나 유효 후보가 없을 때 `DEVELOP`을 도출. C5 부분 기술 실패로 후보가 `NEEDS_REVIEW`가 되면, 이를 "적합 자산 없음 = DEVELOP"으로 **오판**할 위험.
- **패턴**: `NEEDS_REVIEW` 후보에 **원인 태그**(`stateReason`)를 부여 — `INSUFFICIENT_EVIDENCE`(비즈니스) vs `TECHNICAL_FAILURE`(기술).
  - deriveOverall는 **기술 실패 후보를 DEVELOP 신호로 사용하지 않는다.**
  - 접근 가능 후보 중 REUSE/EXTEND가 없고 남은 것이 전부 `TECHNICAL_FAILURE`면 → Overall도 `NEEDS_REVIEW`(추가 검토 필요)로 도출, **DEVELOP 아님**.
  - 진짜 "적합 자산 없음"(검색 0 / 접근 가능 0 / 비즈니스적 부적합)일 때만 `DEVELOP` 유지.
- **DecisionClassifier(C6, 순수 로직)** 는 `stateReason`을 입력·출력에 포함 → 결정성·PBT 대상 유지. (business-rules BR-OVERALL 정제 필요 — Code Gen 시 반영)

### 1.4 데모 모드 폴백 정책 (Q1=C 명시)
- **demoMode OFF**: LLM 실패 시 **fixture 폴백 없음** — 위 매트릭스대로 오류/강등 처리(운영 진실성 확보).
- **demoMode ON**: 대표 시나리오(Hero + 3 Unhappy)는 fixture 결정적 응답 사용. **fixture에 매칭되지 않는 입력은 명시적 오류**로 처리(암묵적 실제 호출 폴백 금지 → 데모 재현성·투명성).

### 1.5 비목표 (Resiliency 확장 skip)
- Circuit breaker, 지수 백오프 재시도, bulkhead, 큐 기반 비동기 복구는 범위 밖(NFR-A1).

---

## 2. Performance Patterns (성능) — Q2=A, NFR-P

### 2.1 Bounded Fan-out (Top-N 상한)
- LLM 재검증 대상을 **Top-N(기본 3, `TOP_N` config)** 로 상한 → 지연·비용 구조적 통제(NFR-P3/C1).

### 2.2 No Caching (캐싱 없음)
- reverify 결과 캐싱하지 않음(무상태). 근거: Top-N 상한 + 데모 모드 fixture로 충분, 상태 관리 복잡도 회피.

### 2.3 Deterministic Fast Path (데모 모드)
- demoMode ON: 대표 시나리오는 LLM 미호출 결정적 fixture → 즉시 응답(NFR-P2). 성능·비용·재현성 동시 확보.

### 2.4 Prompt 간결화
- C1/C5 프롬프트는 필요한 필드/근거만 포함하여 토큰 최소화(NFR-C1).

### 2.5 비목표
- 정량 SLA, 병렬 재검증, 부하 테스트 없음(Hard SLA 없음, best-effort).

---

## 3. Security Patterns (권한/비노출) — Q3=A, NFR-SEC

### 3.1 Early Single-Stage Filtering (초기 단일 필터)
- PermissionFilterComponent를 파이프라인 **초기 단일 스테이지**(search 직후, selectTopN 이전)에 배치.
- per-asset 판정: `role ∈ allowedRoles OR userId ∈ allowedUsers` (BR-PERMISSION). 권한 확장 금지.
- 미인가 후보는 `ExcludedCandidate(reason=NOT_ACCESSIBLE)`로 분리 → 이후 파이프라인은 접근 가능 후보만 처리.

### 3.2 Type-Enforced Non-Disclosure (공개 DTO 분리 — 이중 방어)
- **내부 도메인 타입**(Candidate, ExcludedCandidate, EvidenceChain 내부 필드 등)과 **공개 응답 DTO**(Pydantic response model)를 **타입으로 분리**.
- 공개 응답 DTO는 구조적으로 미인가 정보를 담을 수 없음: `ExcludedCandidate`·제외 개수·제외 플래그 필드가 **응답 모델에 존재하지 않음**.
- 방어선 2겹: (1) 초기 필터로 데이터 제거, (2) 응답 직렬화 경계에서 타입으로 차단.

### 3.3 Rationale Guard (근거 텍스트 누출 방지)
- overallRationale·capabilityMatch 등 서술 필드 생성 시 미인가 자산명·식별자가 포함되지 않도록 가드(NFR-SEC3). 서술은 접근 가능 후보만 근거로 구성.

### 3.4 Internal Audit Logging (서버 내부 감사)
- 미인가 제외 판정은 **서버 내부 감사 로그**에만 기록(요청ID·제외 자산·사유). 공개 응답 아님(NFR-SEC4).

### 3.5 비목표
- 인증(SSO)·암호화·전체 Security 확장 규칙 blocking 적용은 범위 밖(mock permission context).

---

## 4. Scalability Patterns (확장성) — Q4=A, NFR-S

### 4.1 Adapter Pattern + Config-driven Registry
- Multi-Source 검색은 **SourceAdapter 인터페이스** 뒤로 격리. 코어(AssetSearch)는 인터페이스에만 의존.
- **SourceAdapterRegistry** 가 config에 선언된 adapter 목록을 로드 → 신규 Source는 **Adapter 구현 + config 등록**만으로 통합(코어 무변경) (NFR-S2/NFR-3).

### 4.2 Dependency Injection Boundaries (교체 가능한 경계)
- LLMClient / SourceAdapter / AssetRepository / FeedbackStore / PermissionContext 제공을 주입 경계로 격리 → mock → 실제(SSO/실제 Source)로 교체 가능(NFR-S3).

### 4.3 Externalized Configuration
- 임계값(reuse=0.75, extend=0.50), topN(3), demoMode, LLM 설정, 경로, 로그 레벨을 **config/env로 외부화** → 코드 수정 없이 조정(NFR-S4/M3).

### 4.4 비목표
- 수평 확장/오토스케일/분산은 범위 밖(단일 프로세스 데모 동시성).

---

## 5. Testability Patterns (테스트 용이성) — NFR-T

### 5.1 Pure-Core Isolation (순수 코어 격리)
- DecisionClassifier(C6: classify/deriveOverall)는 부작용 없는 **순수 결정적 함수** → Hypothesis PBT(P1~P9) 대상. `stateReason` 포함해도 결정성 유지.

### 5.2 LLM Seam (LLM 이음새)
- LLMClient 추상화 뒤로 격리 → 테스트는 mock/fixture 주입. LLM 경계·I/O는 예제 기반 pytest.

### 5.3 Fixture Provider
- demoMode 및 테스트용 결정적 응답은 FixtureProvider로 제공 → 재현성 확보.

---

## 6. NFR ↔ 패턴 매핑

| NFR | 적용 패턴 |
|---|---|
| NFR-P1~P4 | Bounded Fan-out, No Caching, Deterministic Fast Path, Prompt 간결화, 동기 순차 |
| NFR-S1~S4 | Adapter+Registry, DI Boundaries, Externalized Config |
| NFR-A2 | No-Retry+Config Timeout, 실패 처리 매트릭스, Technical-Failure NEEDS_REVIEW 구분 |
| NFR-A3 | Deterministic Fast Path(demo fixture) |
| NFR-A4 | (logical-components: FeedbackStore JSONL 영속) |
| NFR-SEC1~4 | Early Single-Stage Filtering, Type-Enforced Non-Disclosure, Rationale Guard, Internal Audit |
| NFR-T1~3 | Pure-Core Isolation, LLM Seam, Fixture Provider |
| NFR-C1~C2 | Bounded Fan-out, Prompt 간결화, 명시적 demoMode |
| NFR-M1~3 | (logical-components: StructuredLogger, Config 모듈, OpenAPI) |

---

## 7. Code Generation 반영 필요 항목 (Follow-up)
- **BR-OVERALL 정제**: `NEEDS_REVIEW`에 `stateReason`(INSUFFICIENT_EVIDENCE / TECHNICAL_FAILURE) 도입, deriveOverall이 TECHNICAL_FAILURE를 DEVELOP 신호로 쓰지 않도록 규칙 갱신. (business-rules.md / domain-entities.md 갱신은 Code Gen 시 반영)
- 공개 응답 전용 Pydantic DTO 세트 정의(내부 타입과 분리).
- 데모 모드 미매칭 입력 → 명시적 오류 경로 구현.
