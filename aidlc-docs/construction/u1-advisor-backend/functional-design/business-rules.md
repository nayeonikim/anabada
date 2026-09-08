# Business Rules — U1 Advisor Backend

> CONSTRUCTION - Functional Design (U1). 판정/필터/정렬 규칙 + PBT 불변식.
> 결정 근거: Q1~Q9 + Follow-up1(A)/Follow-up2(A). C6 규칙은 순수·결정적(NFR-5 PBT 대상).

---

## BR-CLARIFY — 의도 명료화 (C1) · US-1.3
- **필수 필드**: role, goal, function, data, output (5개).
- **규칙**: 5필드 중 **하나 이상 빈 값 → "의도 불명확"** → 누락 필드별 명료화 질문을 담은 ClarificationRequest 반환.
- 5필드 모두 채워짐 → 추가 질문 없이 사용자 확인 단계.
- 사용자 답변/수정 승인 후 **승인된 구조로만** advise 진행.
- 빈 rawText → 입력 요구 안내(구조화 미수행).

## BR-PERMISSION — 권한 필터 (C3) · US-2.2 / FR-8 / NFR-4
- **판정(isAccessible)**: `ctx.role ∈ asset.allowedRoles` **OR** `ctx.userId ∈ asset.allowedUsers` → 접근 가능.
- 둘 다 불충족 → 접근 불가 → ExcludedCandidate(reason=`NOT_ACCESSIBLE`)로 분리.
- **적용 시점**: LLM 재검증 **이전** (비용 낭비·오추천 방지).
- **권한 확장 금지**: 규칙에 명시되지 않은 접근을 임의 허용하지 않음.
- **Evidence 노출**: 접근 불가 자산의 Evidence는 결과에서 제외(EvidenceChain에 미포함).

## BR-TOPN — 후보 선별 (C4) · US-2.2 / A-3 확정
- **N = 3** (config.topN, Q3=A). 접근 가능 후보를 **relevance 내림차순** 상위 3개 선별.
- 접근 가능 후보 수 < 3 → 있는 만큼 모두 선별.
- **접근 가능 후보 0개** → Top-N=[], DEVELOP 경로(BR-OVERALL 참조).

## BR-SCORE — 재사용성 점수 (C5) · Q1
- reusabilityScore ∈ **[0.0, 1.0]** 실수(소수 둘째 자리 권장).
- relevance(검색 관련도)와 **구분**: relevance는 선별용, reusabilityScore는 재검증 판정용.
- reasoning에 **Role/Task 맥락 반영을 명시**(US-3.1 AC), "단순 유사 ≠ 재사용성" 반영.

## BR-STATE — 후보 State 판정 (C6, 순수 로직) · US-3.2/3.3
설정: `reuseThreshold`(기본 0.75), `extendThreshold`(기본 0.50) — **환경변수로 override 가능(Q2=D)**.
제약: `0 < extendThreshold ≤ reuseThreshold ≤ 1`; 위반 시 기본값 폴백 + 경고.

`classifyCandidate(vc)`:
```
if vc.evidenceSufficient == false:        → NEEDS_REVIEW      # US-3.3 우선(Score 무관)
elif vc.reusabilityScore >= reuseThreshold:   → REUSE
elif vc.reusabilityScore >= extendThreshold:  → EXTEND_EXISTING
else:                                          → NEEDS_REVIEW
```
- 후보 단위에는 **DEVELOP 없음**.
- NEEDS_REVIEW 시 insufficiencyReason(또는 저Score 사유)을 stateRationale에 노출.

## BR-OVERALL — Overall Decision 산출 (C6, 순수 로직) · US-3.4 / Follow-up2=A
`deriveOverall(states, verified, hasAnyAccessible)`:
```
1) hasAnyAccessible == false (접근 가능 0)                     → DEVELOP
2) REUSE/EXTEND_EXISTING 후보가 하나도 없음 (적합 0)           → DEVELOP   # US-3.4 정합
3) 그 외 → 전체 Top-N 중 reusabilityScore 최고 후보의 State 채택
        동점 시: State 우선순위(REUSE>EXTEND_EXISTING>NEEDS_REVIEW) → assetName 사전순
```
- 규칙 3의 결과로 최고 Score 후보가 NEEDS_REVIEW면 적합 후보가 있어도 Overall=NEEDS_REVIEW 가능(US-3.4 허용 범위).
- **Overall은 권고(recommendation)**: AdviceResult.isRecommendation=true, overallRationale에 "최종 결정은 사용자" 명시(Q4).

## BR-RANK — 랭킹 정렬 (S1 조립) · US-4.1(갱신) / Follow-up1=A
정렬 키 순서(모두 결정적):
```
1) Candidate State 우선순위:  REUSE(0) < EXTEND_EXISTING(1) < NEEDS_REVIEW(2)  # 오름차순=상위
2) reusabilityScore 내림차순
3) assetName 사전순(오름차순)
```
- rank는 1-based로 부여. (스토리 US-4.1 AC 갱신 완료: State→Score→name)

## BR-EVIDENCE — Evidence chain (C7) · US-4.2 / FR-7
- 후보별 {source, assetLink, evidenceItems[], stateRationale} 구성.
- **접근 가능한 Evidence 항목만** 포함(FR-8 연계).
- 모든 추천은 추적 가능한 Evidence 보유(Black-box 금지, NFR-1).

## BR-FEEDBACK — 피드백 (C8) · US-4.3 [MVP]
- 기록: `{resultId, candidateId, verdict∈{useful,notFit}, timestamp}` append.
- MVP는 **수집만**; 선별/랭킹 반영은 [Later] US-5.1.

---

## PBT 불변식 (NFR-5 — C6 순수 로직 대상)

| ID | 불변식 |
|---|---|
| **P1** | classifyCandidate는 항상 {REUSE, EXTEND_EXISTING, NEEDS_REVIEW} 중 하나 반환(전역 함수, 예외 없음). |
| **P2** | evidenceSufficient=false ⇒ Score와 무관하게 결과 = NEEDS_REVIEW. |
| **P3** | evidenceSufficient=true일 때 Score 단조성: score↑ 시 State가 REUSE 방향으로만 이동(역행 없음). |
| **P4** | evidenceSufficient=true ∧ score ≥ reuseThreshold ⇒ REUSE. |
| **P5** | deriveOverall: (접근가능 0) 또는 (REUSE/EXTEND 후보 0) ⇒ DEVELOP. |
| **P6** | REUSE 또는 EXTEND_EXISTING 후보가 하나라도 존재하면 deriveOverall ≠ DEVELOP. |
| **P7** | classifyAll 결과 크기 = 입력 후보 수(누락/중복 없음). |
| **P8** | BR-RANK 정렬 결과는 입력의 순열(후보 손실/추가 없음)이며 동일 입력에 대해 결정적. |
| **P9** | 임계값이 `0 < extend ≤ reuse ≤ 1` 위반 시 기본값(0.50/0.75)으로 폴백 후 P1~P4 유지. |

---

## FR/스토리 트레이스
- FR-2/US-1.3 → BR-CLARIFY
- FR-3/US-2.1 → business-logic-model §3 step1
- FR-8/US-2.2 → BR-PERMISSION, BR-TOPN
- FR-4/US-3.1 → BR-SCORE
- FR-5/US-3.2/3.3 → BR-STATE
- US-3.4 → BR-OVERALL
- FR-6/US-4.1 → BR-RANK
- FR-7/US-4.2 → BR-EVIDENCE
- FR-9/US-4.3 → BR-FEEDBACK
- NFR-5 → PBT 불변식 P1~P9
