# Domain Entities — U1 Advisor Backend

> CONSTRUCTION - Functional Design (U1). 기술 중립 도메인 모델. 구체 기술스택/직렬화 형식은 NFR 단계에서 확정.
> 결정 반영: Q1(Score 0.0~1.0), Q2/Q5(evidenceSufficient + 임계 env 변수화), Q3(N=3), Q4·FU2(Overall=최고 Score 후보 State), Q6·FU1(랭킹 State→Score→name), Q8(mock 범위), Q9(feedback).
> Minimal 정합 개정(2026-09-09): mock/adapter-contract 정합을 위해 **Evidence 엔티티 도입**(한 Asset이 다중 Source Evidence 보유), Asset에 핵심 구조화 필드(capabilities/lifecycle_status/constraints) 추가, Candidate를 **asset 단위**로 조정, EvidenceChain을 실제 Evidence 레코드에서 구성. 권한은 A-2(per-asset allowedRoles/allowedUsers) 유지 — Source-level 권한 레이어 없음(mock의 source-level 예시는 superseded).

---

## 1. 엔티티 관계 개요 (텍스트)

```
Asset(1) ──has──> Evidence(N, 다중 Source)          # mock 저장 구조 (C10)
rawText ──(C1)──> StructuredIntent ──(C2/Adapter+MockDataStore)──> Candidate[] (asset 단위, Evidence 동반)
StructuredIntent ─(C1 누락검출)─> ClarificationRequest (선택)
Candidate[] + PermissionContext ─(C3)─> { accessible: Candidate[], excluded: ExcludedCandidate[] }
accessible ─(C4, N=3)─> Candidate[] (Top-N)
Top-N + StructuredIntent ─(C5, LLM)─> VerifiedCandidate[]
VerifiedCandidate[] ─(C6 순수로직)─> { candidateStates: Map, overallDecision }
VerifiedCandidate[] + states + PermissionContext ─(C7)─> EvidenceChain[] (Candidate.evidence에서 구성)
→ (S1 조립) AdviceResult
(resultId, candidateId, verdict) ─(C8)─> Feedback
```

- **Asset**(mock 저장 원본) ↔ **Evidence**: 1:N. 한 Asset은 여러 Source(GitHub/Confluence/Jira/…)에 걸친 Evidence를 가짐(mock/adapter-contract 정합).
- **Asset** ↔ **Candidate**(검색 결과 뷰): Candidate는 **asset 단위**로 Asset에서 파생(id로 연결)하며, 해당 Asset의 Evidence[]를 동반. 단일 source 개념 없음 — 후보는 다중 Source Evidence를 가짐.
- **VerifiedCandidate**는 Candidate를 감싸 재검증 결과(score/근거/충분성)를 부가.
- **RankedCandidate**는 VerifiedCandidate + 확정된 CandidateState + capabilityMatch의 표현용 결합.
- **AdviceResult**는 ranking·overallDecision·evidenceChains를 담는 최종 공개 응답 집합체. 권한 제외(ExcludedCandidate) 정보는 포함하지 않음(서버 내부 전용).

---

## 2. 엔티티 정의 (개념 필드)

### 2.1 StructuredIntent
| Field | 개념 타입 | 설명 | 제약 |
|---|---|---|---|
| role | string | 사용자 직무/역할 | 5 필수 필드 중 하나 (빈 값 허용, 누락 판정 대상) |
| goal | string | 달성 목표 | 동상 |
| function | string | 만들려는 기능 | 동상 |
| data | string | 사용 데이터 | 동상 |
| output | string | 산출물 형태 | 동상 |

> 5필드 중 하나라도 빈 값이면 "의도 불명확" → ClarificationRequest 생성 (US-1.3).

### 2.2 ClarificationRequest
| Field | 개념 타입 | 설명 |
|---|---|---|
| missingFields | string[] | 누락된 필드명(role/goal/function/data/output 중) |
| questions | string[] | 누락 필드별 명료화 질문 (필드 1:1 대응) |

### 2.3 Asset (mock 원본 — C10 MockDataStore)
| Field | 개념 타입 | 설명 |
|---|---|---|
| id | string | 자산 고유 식별자 |
| name | string | 자산 이름 |
| type | AssetType | dashboard/api/repository/tool/library/script/agent/skill/workflow/capability |
| summary | string | 요약 설명 (검색 매칭·재검증 근거원) |
| capabilities | string[] | 자산이 제공하는 역량 목록 (검색·capabilityMatch·재검증 근거) |
| lifecycleStatus | enum `active`\|`experimental`\|`deprecated`\|`unknown` | 자산 생애주기 상태 (재사용성 판단 핵심; deprecated→재사용 부적합 신호) |
| constraints | string[] | 알려진 제약/한계(호환성·환경·Known Limitation 등; evidenceSufficient 판단 입력) |
| keywords | string[] | 검색 관련도 계산용 태그(선택) |
| evidenceRefs | string[] | 이 Asset을 설명하는 Evidence.id 목록 (다중 Source) |
| allowedRoles | string[] | 접근 허용 Role 목록 (per-asset, A-2) |
| allowedUsers | string[] | 접근 허용 userId 목록 (per-asset, A-2) |

> **단일 source 필드 없음**: 출처는 Asset이 아니라 각 Evidence가 가짐(한 Asset이 다중 Source에 걸침).

### 2.3b Evidence (mock 원본 — C10 / Adapter 반환 단위)
| Field | 개념 타입 | 설명 |
|---|---|---|
| id | string | Evidence 고유 식별자 |
| assetId | string | 소속 Asset.id |
| source | SourceId | 출처 Source (GitHub/Confluence/Jira/IMS/BizForce/EDM) |
| evidenceType | string | 근거 유형(예: implementation/api_guide/known_limitation/incident/forecast …) |
| title | string | Evidence 제목 |
| summary | string | Evidence 요약(재검증 근거원) |
| sourceRef | string | 출처 링크/참조(mock URL) |
| lastUpdated | date? | 최종 갱신일(선택; 노후화 신호) |

> 권한(A-2): Evidence 접근성은 **소속 Asset의 접근성**을 따름(별도 Source-level 권한 레이어 없음). 접근 불가 Asset의 Evidence는 결과에서 제외(FR-8).

### 2.4 Candidate (검색 결과 뷰 — C2, **asset 단위**)
| Field | 개념 타입 | 설명 |
|---|---|---|
| id | string | 원본 Asset.id |
| assetName | string | 자산명 |
| type | AssetType | 자산 유형 |
| summary | string | 요약 |
| capabilities | string[] | 역량 목록(capabilityMatch·재검증 입력) |
| lifecycleStatus | enum | 자산 상태(재검증 입력) |
| constraints | string[] | 제약(재검증 입력) |
| evidence | Evidence[] | 해당 Asset의 Evidence(다중 Source; 검색·재검증·EvidenceChain 원천) |
| sources | SourceId[] | evidence에서 도출한 distinct 출처 목록(표시용) |
| relevance | number(0.0~1.0) | 검색 관련도(Top-N 선별 기준, 재사용성 Score와 별개) |

### 2.5 PermissionContext
| Field | 개념 타입 | 설명 |
|---|---|---|
| userId | string | 사용자 식별자 |
| role | string | 사용자 Role |

### 2.6 ExcludedCandidate — ⚠️ **서버 내부 전용 (공개 API 미노출)**
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidate | Candidate | 제외된 후보 |
| reason | enum `NOT_ACCESSIBLE` | 제외 사유(MVP: 권한 불가 단일 사유) |
| evidenceRef | string | 제외 근거 참조(권한 미충족 설명) |

> **경계 규칙(FR-8/NFR-4)**: ExcludedCandidate는 **서버 내부 로깅/감사 용도로만** 사용한다. 미인가 자산의 id·name·link·summary·rawMeta·Evidence는 **어떤 공개 API 응답에도 포함하지 않는다**. 권한 필터링은 기본 동작이므로 AdviceResult에는 제외 관련 정보를 **일절 노출하지 않는다**(플래그·개수 포함, §2.12).

### 2.7 VerifiedCandidate (C5 재검증 산출)
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidate | Candidate | 원 후보 |
| reusabilityScore | number(0.0~1.0, 소수 둘째) | 재사용성 점수 (Q1) |
| reasoning | string | 판단 근거(Role/Task 맥락 반영 서술) |
| roleTaskContextNote | string | Role/Task 맥락 반영 여부 명시(US-3.1 AC) |
| evidenceSufficient | boolean | 근거 충분성 (false → NEEDS REVIEW 강제, Q5/US-3.3) |
| insufficiencyReason | string? | evidenceSufficient=false일 때 부족/상충 사유 |

### 2.8 CandidateState (열거 — 후보 단위)
`REUSE` | `EXTEND_EXISTING` | `NEEDS_REVIEW`  — 후보 단위엔 DEVELOP 없음.

### 2.9 OverallDecision (열거 — 요청 단위)
`REUSE` | `EXTEND_EXISTING` | `NEEDS_REVIEW` | `DEVELOP`

### 2.10 RankedCandidate (표현용 — 랭킹 1행)
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidateId | string | 후보 id |
| sources | SourceId[] | 출처 목록(다중 Source) |
| assetName | string | 자산명 |
| lifecycleStatus | enum | 자산 상태(표시) |
| reusabilityScore | number | 점수 |
| candidateState | CandidateState | 후보 State |
| capabilityMatch | string | 역량 매칭 요약(FR-6; intent.function 대비 자산 역량 적합 서술) |
| rank | int | 정렬 후 순위(1-based) |

### 2.11 EvidenceChain (C7)
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidateId | string | 후보 id |
| evidenceItems | EvidenceItem[] | 후보 Asset의 Evidence에서 구성(접근 가능 Asset만, FR-8) |
| stateRationale | string | State 부여 근거(NEEDS REVIEW면 insufficiencyReason 포함) |

**EvidenceItem** (EvidenceChain 1행 — Evidence 레코드 투영): `{ source: SourceId, evidenceType: string, title: string, sourceRef: string }`. 자유 텍스트가 아니라 실제 Evidence(2.3b) 레코드에서 구성 — 다중 Source 근거를 추적 가능하게 노출(US-4.2/NFR-1).

### 2.12 AdviceResult (S1 최종 조립)
| Field | 개념 타입 | 설명 |
|---|---|---|
| resultId | string | 결과 식별자(피드백 연결용) |
| ranking | RankedCandidate[] | State→Score→name 순 정렬(FU1) |
| overallDecision | OverallDecision | 요청 전체 권고 |
| overallRationale | string | Overall 산출 근거 |
| isRecommendation | boolean(=true) | Overall은 권고이며 최종 결정은 사용자(Q4 명시) |
| evidenceChains | EvidenceChain[] | 후보별 Evidence(접근 가능 후보만) |

> **미노출 원칙(FR-8/NFR-4)**: AdviceResult는 **공개 API 응답 형태**다. 권한 필터링은 기본 동작이므로 제외 관련 필드(상세·플래그·개수)를 **일절 포함하지 않는다**. 미인가 자산의 id·name·link·summary·rawMeta·Evidence도 물론 미포함. 제외 상세는 ExcludedCandidate(§2.6)로 서버 내부에만 보관한다.

### 2.13 Feedback (C8, Q9)
| Field | 개념 타입 | 설명 |
|---|---|---|
| resultId | string | 대상 결과 |
| candidateId | string | 대상 후보 |
| verdict | enum `useful` \| `notFit` | 피드백 판정 |
| timestamp | datetime | 기록 시각 |

### 2.14 ClassificationConfig (Q2 — 임계값 환경변수화)
| Field | 개념 타입 | 기본값 | 설명 |
|---|---|---|---|
| reuseThreshold | number(0.0~1.0) | 0.75 | 이상이면 REUSE (env override) |
| extendThreshold | number(0.0~1.0) | 0.50 | 이상이면 EXTEND EXISTING (env override) |
| topN | int | 3 | 재검증 대상 수(Q3) |

> 제약: `0 < extendThreshold ≤ reuseThreshold ≤ 1`. 위반 시 기본값으로 폴백(그리고 경고 로깅).

---

## 3. SourceId (열거)
`GitHub` | `Confluence` | `Jira` | `IMS` | `BizForce` | `EDM` (NFR-3 확장 지점 — Adapter로 소스 추가 가능).

## 4. AssetType (열거)
`dashboard` | `api` | `repository` | `tool` | `library` | `script` | `agent` | `skill` | `workflow` | `capability` (adapter-contract §2 정합; 완성형 S/W 외 부분 Capability 포함).
