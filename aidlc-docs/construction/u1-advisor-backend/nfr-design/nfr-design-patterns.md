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

## 1. Resilience Patterns (회복성) — Q1=C (확정 계약), NFR-A2

### 1.1 No-Retry + Config Timeout (재시도 없음, 타임아웃 config)
- LLM 호출(C1 structure, C5 reverify)은 **재시도하지 않는다**. 타임아웃은 config(`LLM_TIMEOUT_SECONDS`)로 관리하며 초과 시 실패로 처리.
- 근거: MVP 단순성 + 예측 가능한 지연. 재시도로 인한 토큰/지연 증가 회피.

### 1.2 데모 모드 폴백 정책
- **demoMode OFF**: 실제 LLM 호출 실패 시 **fixture 폴백 없음** — 아래 계약대로 오류/강등 처리(운영 진실성).
- **demoMode ON**: 대표 시나리오(Hero + 3 Unhappy)는 fixture 결정적 응답. **fixture 미매칭 입력은 명시적 오류**(암묵적 실제 호출 폴백 금지 → 재현성·투명성).

### 1.3 실패 처리 매트릭스

| 지점 | 실패 범위 | 처리 | Overall/HTTP |
|---|---|---|---|
| **C1 structure()** | 실패/타임아웃 | **명확한 오류 응답으로 요청 종료** (폴백 없음) | 비정상 HTTP + 공통 오류 |
| **C5 reverify()** | **일부** 후보 실패 | 정상 응답에 후보 포함, `evaluationStatus=UNAVAILABLE`로 구분(1.4) | 정상 200 (AdviceResult) |
| **C5 reverify()** | **전체** 후보 실패(대상 ≥1) | AdviceResult 미반환, 공통 오류 응답(1.6) | 비정상 HTTP + 공통 오류 |
| 검색 0 / 접근 가능 0 | (실패 아님) | 정상 흐름 | 정상 200, Overall=DEVELOP |

### 1.4 Evaluation-Status Contract (C5 부분 실패 — 핵심)
후보별 재검증 상태를 **`evaluationStatus`** 필드로 명시 구분한다:

| evaluationStatus | reusabilityScore | candidateState | 의미 |
|---|---|---|---|
| **COMPLETED** | `[0,1]` 숫자 | 기존 BR-STATE 규칙 적용 | LLM 평가 정상 완료 (근거 부족으로 인한 NEEDS_REVIEW도 **COMPLETED**) |
| **UNAVAILABLE** | **`null`** | **NEEDS_REVIEW** | LLM 평가 실패(기술적) — 점수 없음 |

- **근거 부족 NEEDS_REVIEW**(비즈니스 판정)와 **평가 실패 NEEDS_REVIEW**(기술)를 `evaluationStatus`로 분리. 전자는 COMPLETED, 후자는 UNAVAILABLE.
- **공개 비노출**: UNAVAILABLE 후보의 공개 사유는 **일반적 '평가 미완료' 설명만**. `TECHNICAL_FAILURE` 코드·내부 예외 상세는 **서버 내부(로그)** 에만 유지(NFR-SEC 정신 연장). 공개 DTO에 내부 예외 문자열 미포함.

### 1.5 랭킹·Overall 규칙 (평가 실패 반영)
- **랭킹**: 평가 실패(UNAVAILABLE) 후보는 **점수 비교에서 제외**하고 **완료 후보 뒤에 정렬**.
  - COMPLETED 후보: 기존 **State → Score → name** 정렬 유지(BR-RANK).
  - UNAVAILABLE 후보끼리: **name → candidateId** 정렬.
- **Overall(deriveOverall)**:
  - 정상 평가된 **REUSE/EXTEND 후보가 있으면** → **COMPLETED 후보만으로** 기존 Overall 규칙 적용.
  - REUSE/EXTEND가 없고 **평가 실패 후보가 있으면** → **Overall = NEEDS_REVIEW**.
  - 일부 평가 실패 시 → `overallRationale`에 **평가 미완료 제한을 일반적 표현**으로 명시(구체 기술 사유 비노출).
  - **기술 실패를 재사용 부적합으로 간주하여 `DEVELOP`을 산출하지 않는다.**
  - 진짜 "적합 자산 없음"(검색 0 / 접근 가능 0 / 비즈니스적 부적합)일 때만 `DEVELOP` 유지.

### 1.6 전체 실패 공통 오류 응답 (C5 전부 실패 / C1 실패)
- 재검증 대상이 1개 이상이고 **전부 실패**하면 AdviceResult 대신 **비정상 HTTP 상태 + 공통 오류 응답**:
  ```json
  { "error": { "code": "...", "message": "...", "requestId": "..." } }
  ```
- **내부 예외 문자열 미포함**. message는 일반적 설명만.
- **HTTP 상태 ↔ 오류 코드 매핑** (설계 확정):

  | 상황 | HTTP | error.code |
  |---|---|---|
  | C1 structure 실패(LLM 오류) | 502 | `INTENT_STRUCTURING_FAILED` |
  | C1/C5 LLM 타임아웃 | 504 | `LLM_TIMEOUT` |
  | C5 전체 후보 재검증 실패 | 502 | `REVERIFICATION_UNAVAILABLE` |
  | demoMode ON 미매칭 입력 | 422 | `DEMO_FIXTURE_NOT_FOUND` |
  | 빈 rawText | 400 | `EMPTY_INTENT` |

  (검색 0 / 접근 가능 0 은 오류가 아니며 정상 200 DEVELOP 경로)

### 1.7 비목표 (Resiliency 확장 skip)
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
| NFR-A2 | No-Retry+Config Timeout, 실패 처리 매트릭스, Evaluation-Status Contract(COMPLETED/UNAVAILABLE), 전체 실패 공통 오류 |
| NFR-A3 | Deterministic Fast Path(demo fixture) |
| NFR-A4 | (logical-components: FeedbackStore JSONL 영속) |
| NFR-SEC1~4 | Early Single-Stage Filtering, Type-Enforced Non-Disclosure, Rationale Guard, Internal Audit |
| NFR-T1~3 | Pure-Core Isolation, LLM Seam, Fixture Provider |
| NFR-C1~C2 | Bounded Fan-out, Prompt 간결화, 명시적 demoMode |
| NFR-M1~3 | (logical-components: StructuredLogger, Config 모듈, OpenAPI) |

---

## 7. 설계 정합성 — 모델/DTO/규칙/PBT 변경 명세 (Q1=C 반영)

### 7.1 후보 도메인 모델 변경
- `VerifiedCandidate`(및 RankedCandidate)에 **`evaluationStatus: COMPLETED | UNAVAILABLE`** 필드 추가.
- `reusabilityScore`를 **nullable**(`float | null`)로 변경 — UNAVAILABLE이면 `null`.
- UNAVAILABLE의 내부 사유(`TECHNICAL_FAILURE` 코드/예외)는 **서버 내부 필드**로만 보관(공개 DTO 미포함).
- `candidateState`: UNAVAILABLE → 항상 `NEEDS_REVIEW`. COMPLETED → 기존 BR-STATE.

### 7.2 공개 응답 DTO
- 공개 RankedCandidate DTO: `evaluationStatus`, nullable `reusabilityScore`, 일반적 '평가 미완료' 문구만 노출. 내부 예외/기술 코드·미인가 정보 필드 부재.
- 전체 실패/치명 오류: 공통 오류 DTO `{ error: { code, message, requestId } }` (§1.6 매핑).

### 7.3 Overall / 랭킹 규칙 (BR-OVERALL / BR-RANK) 정제
- deriveOverall: **COMPLETED 후보만**으로 REUSE/EXTEND 판단. REUSE/EXTEND 부재 + UNAVAILABLE 존재 → **NEEDS_REVIEW**(DEVELOP 아님). 검색0/접근0 → DEVELOP 유지.
- 랭킹: COMPLETED(State→Score→name) 먼저, UNAVAILABLE(name→candidateId) 뒤. UNAVAILABLE은 점수 비교 제외.

### 7.4 PBT 불변식 갱신 (NFR-T1) — business-rules.md P1~P9 정밀 매핑

> C6(classifyCandidate / classifyAll / deriveOverall / BR-RANK 정렬)는 이제 후보별 **`evaluationStatus`(COMPLETED|UNAVAILABLE)** 를 입력으로 받는다. 점수 기반 불변식은 **COMPLETED 후보에만** 적용된다(UNAVAILABLE은 score=null).

**⚠️ P5 충돌 — 반드시 개정:** 현재 P5 = "(접근가능 0) 또는 (REUSE/EXTEND 후보 0) ⇒ DEVELOP". UNAVAILABLE 때문에 REUSE/EXTEND=0이 되는 경우까지 DEVELOP을 강제하므로 새 계약과 **모순**. 아래처럼 개정한다.

| ID | 기존 | 개정/추가 (Code Gen 반영) |
|---|---|---|
| **P1** | classify ∈ {REUSE, EXTEND, NEEDS_REVIEW} | 유지. **UNAVAILABLE ⇒ 항상 NEEDS_REVIEW**(추가 규칙, P1 치역 불변). |
| **P2** | evidenceSufficient=false ⇒ NEEDS_REVIEW | **COMPLETED 후보에만 적용**(evidence 근거 부족). UNAVAILABLE은 P1의 별도 규칙으로 NEEDS_REVIEW. |
| **P3** | score 단조성 | **COMPLETED에만 적용**(UNAVAILABLE은 score=null → 대상 아님). |
| **P4** | score ≥ reuse ⇒ REUSE | **COMPLETED에만 적용**. |
| **P5** (개정) | (접근가능 0) ∨ (REUSE/EXTEND 0) ⇒ DEVELOP | **DEVELOP은 UNAVAILABLE 후보가 하나도 없을 때만 가능.** 즉 DEVELOP ⇔ (접근가능 0 ∨ 검색 0) ∨ (전 후보 COMPLETED ∧ REUSE/EXTEND 0). **UNAVAILABLE이 하나라도 있고 COMPLETED 중 REUSE/EXTEND가 없으면 ⇒ NEEDS_REVIEW**(DEVELOP 금지). |
| **P6** | REUSE/EXTEND 존재 ⇒ Overall ≠ DEVELOP | **COMPLETED 후보 기준**으로 유지(COMPLETED REUSE/EXTEND 존재 ⇒ Overall ≠ DEVELOP). |
| **P7** | classifyAll 크기 = 입력 수 | 유지(UNAVAILABLE 포함 누락/중복 없음). |
| **P8** (개정) | 정렬 결과는 입력의 순열 ∧ 결정적 | 유지 + **정렬 계층 추가**: 모든 UNAVAILABLE은 임의의 COMPLETED보다 뒤. COMPLETED 내부 State→Score→name, UNAVAILABLE 내부 name→candidateId. UNAVAILABLE은 점수 비교에서 제외. 순열성·결정성 유지. |
| **P9** | 임계값 위반 시 폴백 후 P1~P4 유지 | 유지(폴백 후에도 위 개정 P1~P8 성립). |

**신규 불변식 (추가 권장):**
- **P10 (기술실패↛DEVELOP)**: `∃ UNAVAILABLE ∧ COMPLETED 중 REUSE/EXTEND 없음 ⇒ Overall = NEEDS_REVIEW`. (P5 개정의 양성 표현)
- **P11 (score-status 정합)**: `evaluationStatus=UNAVAILABLE ⇔ reusabilityScore=null`, `COMPLETED ⇔ reusabilityScore ∈ [0,1]`.

- DecisionClassifier(C6)는 위를 반영해도 **순수·결정적** 유지(NFR-T1/T2).

### 7.5 Code Generation 반영 지시
- 위 7.1~7.4를 domain-entities.md / business-rules.md / business-logic-model.md에 **Code Gen 시 반영**(현 단계는 백엔드 응답 계약 확정까지; UI 문구/표시는 추후 검토).
- 공개 DTO 세트(내부 타입 분리) + demoMode 미매칭 오류 경로 + §1.6 HTTP↔code 매핑 구현.
