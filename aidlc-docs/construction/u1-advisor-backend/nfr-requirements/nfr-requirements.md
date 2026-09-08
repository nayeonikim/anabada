# NFR Requirements — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Requirements (U1). Functional Design(APPROVED) 기반 비기능 요구 확정본.
> 근거: requirements.md(NFR-1~7, FR-8), functional-design(business-logic-model / domain-entities / business-rules), NFR Requirements plan(Q1~Q8 답변).
> 확장 설정(aidlc-state): Security Baseline=No, Resiliency Baseline=No, Property-Based Testing=Partial(순수 로직만).
> 제약: 해커톤 MVP ~6h, Token Budget USD 1,000, 동기 순차 in-process 파이프라인, representative mock 데이터.
> 기술 스택 결정 및 근거는 `tech-stack-decisions.md` 참조.

---

## 0. 적용 원칙

- 본 문서는 requirements.md의 상위 NFR-1~7을 **U1(백엔드) 관점에서 측정 가능하게 구체화**한다.
- MVP 성격상 **Hard SLA / 부하 목표는 두지 않으며**(Q6=A), best-effort 목표와 구조적 가드로 품질을 확보한다.
- Security / Resiliency 확장 규칙은 **blocking 미적용**(NFR-4). 단, 권한 필터·미인가 자산 비노출은 일반 기능/비기능 요구로 유지.
- 각 NFR은 **검증 방법**을 명시하여 Code Generation·Build/Test 단계에서 확인 가능하도록 한다.

---

## 1. Performance (성능) — NFR-P

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-P1** | `/intent` (Intent 구조화, C1 structure() = LLM 1회) 는 사용자 대기가 과하지 않아야 한다. | Best-effort, 통상 ~10초 이내 지향. Hard SLA 없음(Q6=A). | 수동 데모 관찰 + 로그의 단계 소요시간 |
| **NFR-P2** | `/advise` (검색 + Top-3 순차 LLM 재검증)는 데모 관점에서 수용 가능한 응답성을 가진다. | Best-effort, 통상 ~15초 이내 지향. **데모 모드 fixture 경로는 즉시 응답**(LLM 미호출). | 데모 모드/실호출 각각 로그 소요시간 측정 |
| **NFR-P3** | LLM 재검증 대상 수 Top-N에 상한을 둔다(구조적 성능·비용 가드). **N=3은 데모용 기본값이며 이후 조정 가능**해야 한다. | topN 기본=3, **하드코딩 금지** — config/env(`TOP_N`)로 수정 가능. 코드 상수로 고정하지 않음. | config 검증 + override 동작 테스트 + 코드 리뷰(하드코딩 부재) |
| **NFR-P4** | 파이프라인은 **동기 순차 in-process**로 구현하며, 병렬화·비동기 큐는 MVP 범위 밖. | 단일 프로세스 순차 실행. | 아키텍처 리뷰 |

**비목표(Non-goal)**: p95/p99 지연 SLA, 처리량(TPS) 목표, 부하/스트레스 테스트.

---

## 2. Scalability (확장성) — NFR-S

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-S1 (동시성)** | MVP는 **단일 사용자/소수 동시 요청**(데모 수준) 기준. 수평 확장 설계는 범위 밖. | 데모 동시성 1~수 명. | N/A(설계 비목표 명시) |
| **NFR-S2 (Source 확장성)** | Multi-Source 검색은 **Source Adapter 구조**로 설계하여 mock → 실제 Source로 확장 가능해야 한다. (NFR-3) | 신규 Source 추가 시 Adapter 구현만으로 통합 가능(코어 로직 무변경). | Adapter 인터페이스 존재 + mock adapter 2개 이상으로 대체 가능성 확인 |
| **NFR-S3 (인증 확장성)** | mock user/permission context → 실제 AD SSO로 교체 가능한 경계를 둔다. (NFR-3) | 권한 판정 입력(PermissionContext)을 주입 지점으로 격리. | 코드 경계 리뷰 |
| **NFR-S4 (파라미터 확장성)** | 임계값·Top-N을 코드 상수가 아닌 **config/env override**로 노출. | reuseThreshold=0.75, extendThreshold=0.50, topN=3 (env override). | config 파일 + override 동작 테스트 |

---

## 3. Availability / Reliability (가용성·신뢰성) — NFR-A

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-A1** | Production 수준 Resiliency/Failover/HA는 **범위 밖**(Resiliency 확장 skip). | N/A. | 명시적 비목표 |
| **NFR-A2 (LLM 실패 처리)** | C1/C5 LLM 호출 실패·타임아웃 시 **파이프라인이 크래시하지 않고** 후보를 `NEEDS REVIEW`로 강등하거나 명확한 에러 응답을 반환한다. | LLM 예외 → 후보 `NEEDS REVIEW` + rationale에 사유 기록, 전체 요청 실패로 전파하지 않음(가능한 범위). | 단위 테스트(LLM mock 예외 주입) |
| **NFR-A3 (결정성)** | 대표 데모 시나리오(Hero + 3 Unhappy)는 **데모 모드에서 결정적 fixture**로 재현 가능해야 한다. | 데모 모드 ON → 동일 입력 = 동일 출력. | fixture 재현 테스트 |
| **NFR-A4 (피드백 영속)** | 사용자 피드백은 **서버 재시작 후에도 유지**되어야 한다. | 피드백 JSONL append-only 파일에 기록, 재시작 후 로드 가능. | 재시작 후 피드백 유지 확인 |

---

## 4. Security / Authorization (권한) — NFR-SEC

> Security 확장 규칙은 blocking 미적용(NFR-4). 아래는 **일반 요구사항으로 유지되는 권한 항목**만 규정.

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-SEC1 (권한 필터)** | 사용자 permission context(Role + per-asset 접근권)에 따라 결과를 필터링한다. Advisor는 사용자 권한을 확장하지 않는다. (FR-8) | BR-PERMISSION 판정식에 따른 per-asset 필터 적용. | 단위 테스트(권한별 결과 차등) |
| **NFR-SEC2 (미인가 비노출)** | 미인가 자산의 id·name·link·summary·rawMeta·Evidence 및 **제외 개수/플래그**를 **공개 API 응답에 포함하지 않는다**. | AdviceResult 공개 응답에 exclusion 정보 전무. ExcludedCandidate는 서버 내부(log/audit) 전용. | 응답 스키마 검증 + 직렬화 리뷰 |
| **NFR-SEC3 (근거 누출 방지)** | overallRationale 등 서술 필드에 미인가 자산명이 포함되지 않는다. | 랭킹/근거 텍스트 가드. | 코드 리뷰 + 테스트 |
| **NFR-SEC4 (감사)** | 미인가 제외 판정은 **서버 내부 감사 로그**로 남긴다(공개 응답 아님). | 요청ID·제외 자산·사유 로깅. | 로그 확인 |

---

## 5. Testability (테스트 용이성) — NFR-T

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-T1 (PBT 부분 적용)** | 입출력 관계가 명확한 **순수 판단 로직(C6, business-rules P1~P9)**에 한해 Property-Based Testing을 적용한다. (NFR-5) | C6 스코어링/State 분류/랭킹 정렬 등 순수 함수에 PBT. LLM 경계(C1/C5)·I/O는 PBT 대상 아님. | Hypothesis 속성 테스트 P1~P9 존재·통과 |
| **NFR-T2 (결정성 보장)** | C6는 부작용 없는 결정적 순수 함수로 구현한다(동일 입력 = 동일 출력). | 결정성 속성 테스트. | PBT |
| **NFR-T3 (LLM 격리 테스트)** | LLM 호출부는 인터페이스 뒤로 격리하여 mock으로 대체·테스트 가능해야 한다. | LLM 클라이언트 추상화 + 테스트용 mock/fixture. | 단위 테스트 |

---

## 6. Maintainability / Observability (유지보수·관측) — NFR-M

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-M1 (자기설명)** | Repository·README·API 스키마·Evidence chain이 별도 발표 없이 이해 가능해야 한다. (NFR-1) | 자동 OpenAPI 문서(FastAPI) + README + Evidence chain 응답. | 문서 존재·정합 확인 |
| **NFR-M2 (구조화 로깅)** | 표준 구조화 로그(콘솔/파일): 요청ID·파이프라인 단계·미인가 제외 감사(서버 내부). 외부 관측 스택 없음. | 구조화 로그 출력. | 로그 샘플 확인 |
| **NFR-M3 (설정 외부화)** | 임계값·topN·데모 모드·LLM 설정·경로는 config/env로 외부화. | config 모듈 단일 소스. | config 리뷰 |

**비목표**: APM/트레이싱/메트릭 수집 등 외부 관측 스택.

---

## 7. Cost / Budget (비용) — NFR-C

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-C1 (토큰 예산)** | LLM 토큰/비용은 Token Budget USD 1,000 내에서 동작해야 한다. (NFR-2) | **구조적 가드**로 통제: Top-N 상한(데모 기본=3, config로 조정 가능) + 대표 데모 fixture 우선 + 프롬프트 간결화. 별도 미터링 미구현(Q7=A). | 구조적 가드 존재 확인 |
| **NFR-C2 (데모 모드)** | fixture 우선 경로는 암묵 분기가 아니라 **명시적 데모 모드**(demoMode 플래그/env)로 구분한다. | demoMode ON → 대표 시나리오 fixture 결정적 응답(LLM 미호출); OFF → 실제 LLM 호출. Top-N 상한·프롬프트 간결화는 공통. | 데모 모드 분기 테스트 |

---

## 8. Usability (백엔드 계약 관점) — NFR-U

| ID | 요구 | 목표/측정 | 검증 방법 |
|---|---|---|---|
| **NFR-U1 (API 계약 명확성)** | U2가 소비하는 `/intent`·`/advise`·`/feedback` 응답은 랭킹·Decision State·Score·Evidence chain을 단일 화면 비교에 충분한 구조로 제공한다. (NFR-6, FR-6/7/10) | 타입 기반 스키마 + 자동 문서. | OpenAPI 스키마 검증 |

---

## 9. NFR ↔ 검증(예정) 매핑 요약

| NFR 그룹 | 주 검증 단계 |
|---|---|
| Performance / Scalability | 아키텍처 리뷰 + 데모 관찰 + config 테스트 |
| Availability / Reliability | 단위 테스트(LLM 예외/재시작) + fixture 재현 |
| Security / Authorization | 응답 스키마 검증 + 권한별 단위 테스트 + 로그 확인 |
| Testability | Hypothesis PBT(P1~P9) + LLM mock 단위 테스트 |
| Maintainability / Cost / Usability | 문서·config·로그 리뷰 + 데모 모드 테스트 |

---

## 10. 미해결/이월 없음

- 본 단계 질문(Q1~Q8) 답변에 모호·모순 없음 → 후속 질문 불필요.
- 상세 기술 선택(언어/프레임워크/LLM/PBT/저장/로깅)은 `tech-stack-decisions.md`에서 확정.
