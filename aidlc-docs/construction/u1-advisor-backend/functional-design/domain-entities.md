# Domain Entities — U1 Advisor Backend

> CONSTRUCTION - Functional Design (U1). 기술 중립 도메인 모델. 구체 기술스택/직렬화 형식은 NFR 단계에서 확정.
> 결정 반영: Q1(Score 0.0~1.0), Q2/Q5(evidenceSufficient + 임계 env 변수화), Q3(N=3), Q4·FU2(Overall=최고 Score 후보 State), Q6·FU1(랭킹 State→Score→name), Q8(mock 범위), Q9(feedback).

---

## 1. 엔티티 관계 개요 (텍스트)

```
rawText ──(C1)──> StructuredIntent ──(C2/Adapter+MockDataStore)──> Candidate[]
StructuredIntent ─(C1 누락검출)─> ClarificationRequest (선택)
Candidate[] + PermissionContext ─(C3)─> { accessible: Candidate[], excluded: ExcludedCandidate[] }
accessible ─(C4, N=3)─> Candidate[] (Top-N)
Top-N + StructuredIntent ─(C5, LLM)─> VerifiedCandidate[]
VerifiedCandidate[] ─(C6 순수로직)─> { candidateStates: Map, overallDecision }
VerifiedCandidate[] + states + PermissionContext ─(C7)─> EvidenceChain[]
→ (S1 조립) AdviceResult
(resultId, candidateId, verdict) ─(C8)─> Feedback
```

- **Asset**(mock 저장 원본) ↔ **Candidate**(검색 결과 뷰): Candidate는 Asset에서 파생(id로 연결).
- **VerifiedCandidate**는 Candidate를 감싸 재검증 결과(score/근거/충분성)를 부가.
- **RankedCandidate**는 VerifiedCandidate + 확정된 CandidateState + capabilityMatch의 표현용 결합.
- **AdviceResult**는 ranking·overallDecision·evidenceChains·excluded를 담는 최종 응답 집합체.

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
| source | SourceId | GitHub/Confluence/Jira/IMS/BizForce/EDM 중 하나 |
| name | string | 자산 이름 |
| summary | string | 요약 설명 (검색 매칭·재검증 근거원) |
| link | string | 자산 링크(mock URL) |
| keywords | string[] | 검색 관련도 계산용 태그(선택) |
| allowedRoles | string[] | 접근 허용 Role 목록 (per-asset) |
| allowedUsers | string[] | 접근 허용 userId 목록 (per-asset) |

### 2.4 Candidate (검색 결과 뷰 — C2)
| Field | 개념 타입 | 설명 |
|---|---|---|
| id | string | 원본 Asset.id |
| source | SourceId | 출처 |
| assetName | string | 자산명 |
| assetLink | string | 링크 |
| summary | string | 요약 |
| relevance | number(0.0~1.0) | 검색 관련도(Top-N 선별 기준, 재사용성 Score와 별개) |
| rawMeta | object | Source별 원시 메타(선택) |

### 2.5 PermissionContext
| Field | 개념 타입 | 설명 |
|---|---|---|
| userId | string | 사용자 식별자 |
| role | string | 사용자 Role |

### 2.6 ExcludedCandidate
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidate | Candidate | 제외된 후보 |
| reason | enum `NOT_ACCESSIBLE` | 제외 사유(MVP: 권한 불가 단일 사유) |
| evidenceRef | string | 제외 근거 참조(권한 미충족 설명) |

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
| source | SourceId | 출처 |
| assetName | string | 자산명 |
| assetLink | string | 링크 |
| reusabilityScore | number | 점수 |
| candidateState | CandidateState | 후보 State |
| capabilityMatch | string | 역량 매칭 요약(FR-6; intent.function 대비 자산 역량 적합 서술) |
| rank | int | 정렬 후 순위(1-based) |

### 2.11 EvidenceChain (C7)
| Field | 개념 타입 | 설명 |
|---|---|---|
| candidateId | string | 후보 id |
| source | SourceId | 출처 |
| assetLink | string | 링크 |
| evidenceItems | string[] | 관련 Evidence 항목(접근 가능 항목만, FR-8) |
| stateRationale | string | State 부여 근거(NEEDS REVIEW면 insufficiencyReason 포함) |

### 2.12 AdviceResult (S1 최종 조립)
| Field | 개념 타입 | 설명 |
|---|---|---|
| resultId | string | 결과 식별자(피드백 연결용) |
| ranking | RankedCandidate[] | State→Score→name 순 정렬(FU1) |
| overallDecision | OverallDecision | 요청 전체 권고 |
| overallRationale | string | Overall 산출 근거 |
| isRecommendation | boolean(=true) | Overall은 권고이며 최종 결정은 사용자(Q4 명시) |
| evidenceChains | EvidenceChain[] | 후보별 Evidence |
| excluded | ExcludedCandidate[] | 권한 제외 후보 |

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
