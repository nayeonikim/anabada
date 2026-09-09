# Business Rules — U1 Advisor Backend

> CONSTRUCTION - Functional Design (U1). 판정/필터/정렬 규칙 + PBT 불변식.
> 결정 근거: Q1~Q9 + Follow-up1(A)/Follow-up2(A). C6 규칙은 순수·결정적(NFR-5 PBT 대상).
> **NFR Design §7.3·§7.4 반영(Code Gen, 2026-09-09)**: C5 부분 실패 계약(evaluationStatus) 정합 — BR-STATE(UNAVAILABLE⇒NEEDS_REVIEW; COMPLETED만 Score 기반 판정), BR-OVERALL(기술 실패↛DEVELOP; UNAVAILABLE 존재∧COMPLETED REUSE/EXTEND 0 ⇒ NEEDS_REVIEW), BR-RANK(COMPLETED 먼저→UNAVAILABLE 뒤) 정제, PBT 불변식 **P1~P11**(P5·P8 개정, P10·P11 신규)로 확장.

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
- **Evidence 노출**: 접근 불가 자산의 Evidence는 결과에서 제외(EvidenceChain에 미포함). 권한 판정은 **Asset 단위**이며 Evidence는 소속 Asset의 접근성을 상속(Source-level 권한 레이어 없음, A-2).
- **공개 응답 미노출 (FR-8/NFR-4)**: 권한 필터링은 기본 동작이므로, 공개 API 응답에는 제외 관련 정보를 **일절 포함하지 않는다** — 미인가 자산의 id·name·link·summary·rawMeta·Evidence는 물론 제외 **플래그·개수**도 미노출. 제외 상세(ExcludedCandidate)는 **서버 내부 로그/감사 전용**. 별도 UI 안내도 두지 않는다.
- **overallRationale 가드**: Overall 근거 서술에도 미인가 자산명/식별정보를 포함하지 않는다(접근 가능 후보 기준으로만 서술).

## BR-TOPN — 후보 선별 (C4) · US-2.2 / A-3 확정
- **N = 3** (config.topN, Q3=A). 접근 가능 후보를 **relevance 내림차순** 상위 3개 선별.
- 접근 가능 후보 수 < 3 → 있는 만큼 모두 선별.
- **접근 가능 후보 0개** → Top-N=[], DEVELOP 경로(BR-OVERALL 참조).

## BR-SCORE — 재사용성 점수 (C5) · Q1
- reusabilityScore ∈ **[0.0, 1.0]** 실수(소수 둘째 자리 권장).
- relevance(검색 관련도)와 **구분**: relevance는 선별용, reusabilityScore는 재검증 판정용.
- reasoning에 **Role/Task 맥락 반영을 명시**(US-3.1 AC), "단순 유사 ≠ 재사용성" 반영.
- **판단 입력(구조화)**: 후보의 `capabilities`·`lifecycleStatus`·`constraints` + 다중 Source `evidence`를 근거로 사용. deprecated/상충 constraints/Known Limitation 등 부정 신호는 `evidenceSufficient=false`로 이어질 수 있음(BR-STATE P2와 연계).

## BR-STATE — 후보 State 판정 (C6, 순수 로직) · US-3.2/3.3
설정: `reuseThreshold`(기본 0.75), `extendThreshold`(기본 0.50) — **환경변수로 override 가능(Q2=D)**.
제약: `0 < extendThreshold ≤ reuseThreshold ≤ 1`; 위반 시 기본값 폴백 + 경고.

`classifyCandidate(vc)`:
```
if vc.evaluationStatus == UNAVAILABLE:    → NEEDS_REVIEW      # §7.4 P1: 기술 실패(score=null)는 항상 NEEDS_REVIEW
# 이하는 COMPLETED 후보에만 적용:
if vc.evidenceSufficient == false:        → NEEDS_REVIEW      # US-3.3 우선(Score 무관)
elif vc.reusabilityScore >= reuseThreshold:   → REUSE
elif vc.reusabilityScore >= extendThreshold:  → EXTEND_EXISTING
else:                                          → NEEDS_REVIEW
```
- 후보 단위에는 **DEVELOP 없음**.
- **evaluationStatus 구분(§7.1/§7.4)**: `UNAVAILABLE`(기술 실패, score=null) → 항상 NEEDS_REVIEW. `COMPLETED`(정상 완료)만 Score/evidenceSufficient 기반 판정. 두 경로 모두 NEEDS_REVIEW를 낼 수 있으나 evaluationStatus로 구분(공개 사유: UNAVAILABLE=일반 '평가 미완료'만, COMPLETED=insufficiencyReason/저Score).
- NEEDS_REVIEW 시 stateRationale: COMPLETED이면 insufficiencyReason(또는 저Score 사유), UNAVAILABLE이면 일반적 '평가 미완료' 문구만(내부 technicalFailureReason은 서버 로그 전용).

## BR-OVERALL — Overall Decision 산출 (C6, 순수 로직) · US-3.4 / Follow-up2=A
`deriveOverall(states, verified, hasAnyAccessible)` — **§7.3 정제(기술 실패↛DEVELOP)**:
```
1) hasAnyAccessible == false (접근 가능 0) 또는 검색 0            → DEVELOP   # 진짜 '적합 자산 없음'
2) COMPLETED 후보만으로 판단:
   a) COMPLETED 중 REUSE/EXTEND_EXISTING 후보 존재
        → COMPLETED 후보만으로 기존 규칙: reusabilityScore 최고 COMPLETED 후보의 State 채택
          동점 시 State 우선순위(REUSE>EXTEND_EXISTING>NEEDS_REVIEW) → assetName 사전순
   b) COMPLETED 중 REUSE/EXTEND_EXISTING 없음:
        - UNAVAILABLE 후보가 하나라도 존재  → NEEDS_REVIEW   # §7.4 P5/P10: 아직 평가 못한 후보 있음 → DEVELOP 금지
        - 전 후보가 COMPLETED(UNAVAILABLE 0) ∧ REUSE/EXTEND 0  → DEVELOP   # US-3.4 정합
```
- **기술 실패(UNAVAILABLE)를 재사용 부적합으로 간주하여 DEVELOP을 산출하지 않는다**(§1.5/§7.3). DEVELOP은 (접근/검색 0) 또는 (전 후보 COMPLETED ∧ REUSE/EXTEND 0)일 때만.
- 규칙 2a 결과로 최고 Score COMPLETED 후보가 NEEDS_REVIEW면 적합 후보가 있어도 Overall=NEEDS_REVIEW 가능(US-3.4 허용 범위).
- 일부 평가 실패(UNAVAILABLE 존재) 시 overallRationale에 **'일부 평가 미완료' 제한을 일반적 표현**으로 명시(구체 기술 사유 비노출).
- **Overall은 권고(recommendation)**: AdviceResult.isRecommendation=true, overallRationale에 "최종 결정은 사용자" 명시(Q4).

## BR-RANK — 랭킹 정렬 (S1 조립) · US-4.1(갱신) / Follow-up1=A · **§7.3 2계층 정제**
2계층 정렬(모두 결정적): **COMPLETED 후보 먼저, UNAVAILABLE 후보 뒤**(UNAVAILABLE은 점수 비교 제외).

COMPLETED 후보 내부 정렬 키:
```
1) Candidate State 우선순위:  REUSE(0) < EXTEND_EXISTING(1) < NEEDS_REVIEW(2)  # 오름차순=상위
2) reusabilityScore 내림차순
3) assetName 사전순(오름차순)
```
UNAVAILABLE 후보 내부 정렬 키(score=null → 점수 비교 배제):
```
1) assetName 사전순(오름차순)
2) candidateId 사전순(오름차순)
```
- 최종 순서 = [COMPLETED 정렬] ++ [UNAVAILABLE 정렬]. rank는 1-based로 부여.
- (스토리 US-4.1 AC 갱신 완료: State→Score→name / UNAVAILABLE 후미 배치는 §7.3)

## BR-EVIDENCE — Evidence chain (C7) · US-4.2 / FR-7
- 후보별 {candidateId, evidenceItems[], stateRationale} 구성. evidenceItems는 후보 Asset의 실제 **Evidence 레코드**에서 투영: `{source, evidenceType, title, sourceRef}` (다중 Source).
- **접근 가능한 Asset의 Evidence만** 포함(FR-8 연계). per-asset 권한(A-2)이므로 접근 가능 후보는 그 Asset의 전 Evidence를 노출, 접근 불가 Asset은 후보/Evidence 모두 제외.
- 모든 추천은 추적 가능한 Evidence 보유(Black-box 금지, NFR-1) — 자유 텍스트가 아니라 Source별 Evidence 항목으로 근거화.

## BR-FEEDBACK — 피드백 (C8) · US-4.3 [MVP]
- 기록: `{resultId, candidateId, verdict∈{useful,notFit}, timestamp}` append.
- MVP는 **수집만**; 선별/랭킹 반영은 [Later] US-5.1.

---

## PBT 불변식 (NFR-5 — C6 순수 로직 대상) — **§7.4 evaluationStatus 정합(P1~P11)**

> C6는 후보별 `evaluationStatus(COMPLETED|UNAVAILABLE)`를 입력으로 받는다. 점수 기반 불변식(P2~P4)은 **COMPLETED 후보에만** 적용(UNAVAILABLE은 score=null).

| ID | 불변식 |
|---|---|
| **P1** | classifyCandidate는 항상 {REUSE, EXTEND_EXISTING, NEEDS_REVIEW} 중 하나 반환(예외 없음). **UNAVAILABLE ⇒ 항상 NEEDS_REVIEW**(추가 규칙, 치역 불변). |
| **P2** | (COMPLETED에만) evidenceSufficient=false ⇒ Score 무관 결과 = NEEDS_REVIEW. |
| **P3** | (COMPLETED에만) evidenceSufficient=true일 때 Score 단조성: score↑ 시 State가 REUSE 방향으로만 이동(역행 없음). |
| **P4** | (COMPLETED에만) evidenceSufficient=true ∧ score ≥ reuseThreshold ⇒ REUSE. |
| **P5** (개정) | deriveOverall: **DEVELOP ⇔ (접근가능 0 ∨ 검색 0) ∨ (전 후보 COMPLETED ∧ REUSE/EXTEND 0)**. UNAVAILABLE이 하나라도 있고 COMPLETED 중 REUSE/EXTEND가 없으면 ⇒ NEEDS_REVIEW(DEVELOP 금지). |
| **P6** | COMPLETED REUSE/EXTEND_EXISTING 후보가 하나라도 존재하면 deriveOverall ≠ DEVELOP. |
| **P7** | classifyAll 결과 크기 = 입력 후보 수(UNAVAILABLE 포함, 누락/중복 없음). |
| **P8** (개정) | BR-RANK 정렬 결과는 입력의 순열이며 결정적. **정렬 계층**: 모든 UNAVAILABLE은 임의의 COMPLETED보다 뒤. COMPLETED 내부 State→Score→name, UNAVAILABLE 내부 name→candidateId. UNAVAILABLE은 점수 비교 제외. |
| **P9** | 임계값이 `0 < extend ≤ reuse ≤ 1` 위반 시 기본값(0.50/0.75)으로 폴백 후 P1~P8 유지. |
| **P10** (신규) | 기술실패↛DEVELOP: `∃ UNAVAILABLE ∧ (COMPLETED 중 REUSE/EXTEND 없음) ⇒ Overall = NEEDS_REVIEW`(P5 개정의 양성 표현). |
| **P11** (신규) | score-status 정합: `evaluationStatus=UNAVAILABLE ⇔ reusabilityScore=null`, `COMPLETED ⇔ reusabilityScore ∈ [0,1]`. |

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
- NFR-5 → PBT 불변식 P1~P11 (§7.4 evaluationStatus 정합)
