# Tech Stack Decisions — U1 Advisor Backend

> Stage: CONSTRUCTION - NFR Requirements (U1). NFR Requirements plan(Q1~Q8) 답변에 근거한 기술 스택 확정.
> 관련 NFR: `nfr-requirements.md`. 제약: 해커톤 MVP ~6h, Token Budget USD 1,000, mock 데이터, 동기 순차 in-process.

---

## 결정 요약표

| # | 영역 | 결정 | 근거 NFR |
|---|---|---|---|
| D1 | 언어/런타임 | **Python 3.11+** | NFR-2, NFR-5, NFR-M1 |
| D2 | 웹 API 프레임워크 | **FastAPI** | NFR-M1, NFR-U1 |
| D3 | LLM 제공자/SDK | **Amazon Bedrock — Claude** | NFR-3, NFR-C1 |
| D4 | PBT 프레임워크 | **Hypothesis** | NFR-5, NFR-T1 |
| D5 | 데이터/피드백 저장 | **mock=JSON 로드+in-memory / feedback=JSONL append-only(영속)** | NFR-A4, NFR-2 |
| D6 | 성능 목표 | **Hard SLA 없음, best-effort + 데모 모드 즉시 응답** | NFR-P1~P2 |
| D7 | 토큰/비용 가드 | **구조적 가드 + 명시적 데모 모드(demoMode)** | NFR-C1, NFR-C2 |
| D8 | 로깅/관측 | **표준 구조화 로그(콘솔/파일) + 서버 내부 제외 감사** | NFR-M2, NFR-SEC4 |

---

## D1. 언어/런타임 — Python 3.11+ (Q1=A)

- **결정**: 백엔드 구현 언어는 Python 3.11+.
- **근거**: LLM SDK 성숙, PBT(Hypothesis) 표현력, 6h MVP 생산성. 타입 힌트로 자기설명(NFR-M1) 유리.
- **함의**: 타입 힌트 적극 사용, 표준 `logging`, 가상환경/`requirements.txt` 또는 `pyproject.toml`로 의존성 관리(Code Gen에서 확정).

## D2. 웹 API 프레임워크 — FastAPI (Q2=A)

- **결정**: `/intent`, `/advise`, `/feedback` 로컬 HTTP API를 FastAPI로 구현.
- **근거**: Pydantic 타입 기반 요청/응답 스키마, 자동 OpenAPI 문서(NFR-M1/U1), 경량·빠른 구현.
- **함의**:
  - 응답 모델은 Pydantic으로 정의 → 미인가 자산 정보가 스키마에 **존재하지 않도록** 설계(NFR-SEC2).
  - ExcludedCandidate 등 서버 내부 타입은 응답 모델에서 분리.
  - 로컬 개발 서버(uvicorn) 실행.

## D3. LLM 제공자/SDK — Amazon Bedrock (Claude) (Q3=A)

- **결정**: C1 `structure()`·C5 `reverify()`의 LLM 호출은 Amazon Bedrock의 Claude 모델 사용(`boto3` bedrock-runtime).
- **근거**: AWS AI-DLC 해커톤 컨텍스트 정합, 사내 정책·크레딧 활용 자연스러움.
- **함의**:
  - LLM 호출은 **추상 인터페이스(LLMClient) 뒤로 격리**(NFR-T3) → mock/fixture 대체 가능, 데모 모드 분기 용이.
  - 모델 ID·리전·타임아웃은 config/env로 외부화(NFR-M3).
  - 자격증명은 표준 AWS 자격증명 체인 사용(환경변수/프로파일). 코드에 하드코딩 금지.
  - 최신·가장 유능한 Claude 모델을 기본값으로 지향(구체 모델 ID는 Code Gen에서 config로 확정).

## D4. PBT 프레임워크 — Hypothesis (Q4=A)

- **결정**: C6 순수 판단 로직(business-rules P1~P9)의 Property-Based Testing은 Hypothesis.
- **근거**: Python 정합, 성숙·표현력. NFR-5(부분 적용) 충족.
- **함의**: PBT는 **순수 로직에만** 적용(스코어링·State 분류·랭킹 정렬·결정성). LLM 경계·I/O는 예제 기반 단위 테스트로 커버.

## D5. 데이터/피드백 저장 — JSON 로드 + JSONL 피드백 (Q5=A 보강)

- **결정**:
  - **mock Asset/Evidence/permission context**: 시작 시 JSON 파일 로드 → **in-memory 보관(read-only)**.
  - **사용자 피드백(FR-9)**: **JSONL(append-only) 파일에 기록** → 서버 재시작 후에도 유지(영속), 시작 시 로드.
- **근거**: 6h MVP·재현성에 충분, DB 불필요. 피드백 영속 요구(NFR-A4)는 JSONL로 경량 충족.
- **함의**:
  - mock JSON은 domain-Mock 정합 결정에 따라 **per-asset allowedRoles/allowedUsers + Asset/Evidence 구조**로 작성(Code Gen).
  - JSONL은 한 줄 = 한 피드백 이벤트(요청ID·후보·평가·타임스탬프). append-only, 동시 쓰기는 데모 수준에서 단순 파일 append로 처리.
  - 파일 경로는 config로 외부화.

## D6. 성능 목표 — best-effort, Hard SLA 없음 (Q6=A)

- **결정**: 정량 SLA 없음. 통상 `/intent` ~10초, `/advise` ~15초 이내 지향(best-effort). 데모 모드 fixture 경로는 즉시 응답.
- **근거**: MVP·데모 관점 현실적, 부하 테스트 불필요.
- **함의**: 부하/스트레스 테스트 미수행. 단계별 소요시간 로깅으로 관찰.

## D7. 토큰/비용 가드 — 구조적 가드 + 명시적 데모 모드 (Q7=A 보강)

- **결정**:
  - 구조적 가드: **Top-N 상한(데모 기본=3, `TOP_N` config/env로 조정 가능, 하드코딩 금지)** + 프롬프트 간결화 + 대표 데모 fixture 우선. 별도 토큰 미터링 미구현.
  - fixture 경로는 암묵 분기가 아니라 **명시적 데모 모드**로 구분.
- **데모 모드 사양**:
  - `demoMode` 플래그(환경변수 `DEMO_MODE` 등)로 제어.
  - **ON**: 대표 시나리오(Hero + 3 Unhappy) 입력은 결정적 fixture 응답 반환(LLM 미호출) → 결정성(NFR-A3)·비용 0.
  - **OFF**: 실제 Bedrock LLM 호출.
  - Top-N 상한·프롬프트 간결화는 두 모드 공통.
- **근거**: 토큰 예산(USD 1,000) 구조적 통제 + 데모 재현성·투명성 확보(암묵 fixture 회피).

## D8. 로깅/관측 — 구조화 로그 + 내부 감사 (Q8=A)

- **결정**: 표준 구조화 로그(콘솔/파일). 요청ID·파이프라인 단계·미인가 제외 감사(서버 내부). 외부 관측 스택 없음.
- **근거**: NFR-1(자기설명) + FR-8/NFR-SEC4(감사) 충족, MVP 경량.
- **함의**:
  - Python `logging` + 구조화 포맷(JSON line 또는 key=value).
  - 제외 감사 로그는 **서버 내부 전용** — 공개 응답에 절대 포함하지 않음(NFR-SEC2).
  - 로그 레벨·출력 대상은 config.

---

## 확정 스택 스냅샷 (Code Generation 입력)

```text
Language      : Python 3.11+
Web API       : FastAPI (+ uvicorn), Pydantic 스키마
LLM           : Amazon Bedrock — Claude (boto3 bedrock-runtime), LLMClient 추상화 뒤 격리
PBT           : Hypothesis (C6 순수 로직 P1~P9)
Unit Test     : pytest (예제 기반, LLM mock)
Storage       : mock=JSON→in-memory(read-only) / feedback=JSONL append-only(영속)
Config        : 환경변수/config 모듈 — reuseThreshold=0.75, extendThreshold=0.50, topN(기본3·TOP_N override), DEMO_MODE, LLM 모델/리전/타임아웃, 파일 경로, 로그 설정
Logging       : 표준 structured logging(콘솔/파일) + 서버 내부 제외 감사
Perf/Cost     : Hard SLA 없음(best-effort) / 구조적 가드(Top-N=3, fixture 데모 모드, 프롬프트 간결화)
```

## 확장 규칙 컴플라이언스 요약 (활성 확장만)

| 확장 | 상태 | 본 단계 적용 |
|---|---|---|
| Security Baseline | Disabled(No) | N/A — blocking 미적용. 단, 권한 필터·미인가 비노출·감사(NFR-SEC1~4)는 일반 요구로 반영. |
| Resiliency Baseline | Disabled(No) | N/A — Production HA/Failover 비목표(NFR-A1). LLM 실패 강등(NFR-A2)만 반영. |
| Property-Based Testing | Partial | 적용 — C6 순수 로직에 한해 Hypothesis(NFR-T1). LLM/I/O는 대상 아님. |

> Disabled 확장(Security/Resiliency)은 blocking 미적용으로 skip 처리(aidlc-state Extension Configuration 근거). Partial PBT는 순수 로직 범위로 한정 적용.
