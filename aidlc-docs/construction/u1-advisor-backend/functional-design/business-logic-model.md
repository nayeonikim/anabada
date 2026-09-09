# Business Logic Model — U1 Advisor Backend

> CONSTRUCTION - Functional Design (U1). 파이프라인 단계별 알고리즘·데이터 흐름 (기술 중립).
> 오케스트레이터 S1(AdvisorOrchestratorService)이 컴포넌트를 동기 순차 호출. LLM 경계는 Q7=A(실제 LLM + 데모용 결정적 fixture 병행).
> **NFR Design §1.3~1.6·§7 반영(Code Gen, 2026-09-09)**: C5 부분 실패 계약(evaluationStatus COMPLETED/UNAVAILABLE), 실패 처리 매트릭스(C1 실패→오류 종료 / C5 일부→후보 강등 / C5 전체→공통 오류), HTTP↔code 매핑(§1.6)을 흐름에 반영. §6 경계/오류 처리를 계약형으로 갱신.

---

## 1. 논리 엔드포인트 3개 (U1 노출 계약)

| Endpoint | 메서드 | 입력 | 출력 |
|---|---|---|---|
| `POST /intent` | S1.submitIntent | rawText | StructuredIntent \| ClarificationRequest |
| `POST /advise` | S1.advise | approvedIntent + PermissionContext | AdviceResult |
| `POST /feedback` | S1.submitFeedback | resultId, candidateId, verdict | 기록 확인(id) |

---

## 2. submitIntent 흐름 (C1) — US-1.1/1.2/1.3

```
1) structure(rawText)                → StructuredIntent (LLM: 5필드 추출; 실패/불명 필드는 빈 값)
2) detectMissingFields(intent)       → string[] (빈 값 필드 목록)
3) if missing.length > 0:
       buildClarification(missing)   → ClarificationRequest (필드별 질문) → 반환 (여기서 종료)
   else:
       StructuredIntent 반환 (사용자 확인/승인 단계로)
```

- **LLM 경계(Q7)**: `structure()`는 실제 LLM 호출. 대표 mock 시나리오(Hero+3 Unhappy)는 결정적 fixture로 재현 보장(데모 안정성).
- **applyUserRevision(intent, answers)**: 사용자가 답/수정 후 재제출 시 승인 구조 확정 → 이후 `advise`로 전달.
- 빈 rawText → 입력 요구 안내(US-1.1 AC): 구조화 이전에 가드.

---

## 3. advise 흐름 (S1 오케스트레이션) — US-2.1~US-4.2

```
IN: approvedIntent(StructuredIntent), ctx(PermissionContext)

1) AssetSearchComponent.search(intent)
     - SourceAdapterRegistry.getAll() 순회 → 각 Adapter.search(intent) → Evidence[] 반환(Source별)
     - Evidence를 assetId로 묶어 **asset 단위 Candidate**로 집계 (한 Asset이 다중 Source Evidence 보유)
     - 각 Candidate에 relevance(0~1) 부여 (keyword/summary/capabilities 매칭 기반)
     → allCandidates: Candidate[] (각 후보는 evidence[]·sources[]·capabilities·lifecycleStatus·constraints 동반)

2) PermissionFilterComponent.filter(allCandidates, ctx)
     - 각 후보 Asset에 대해 isAccessible(asset, ctx):
         role ∈ allowedRoles  OR  userId ∈ allowedUsers  → 접근 가능
     - 접근 불가 → ExcludedCandidate(reason=NOT_ACCESSIBLE) 로 분리
     → { accessible: Candidate[], excluded: ExcludedCandidate[] }
     (권한 확장 금지: 규칙에 없는 접근 허용 안 함)

3) CandidateSelectionComponent
     - hasAnyAccessible(accessible)?
         false → topN = [] , DEVELOP 경로 플래그
         true  → selectTopN(accessible, config.topN=3): relevance 내림차순 상위 3
     → topN: Candidate[]

4) ReVerificationComponent.reverify(topN, intent)   (LLM) — **evaluationStatus 계약(§1.4/§7.1)**
     - 후보별 LLM 호출(재시도 없음, 타임아웃 config; §1.1):
         · 성공 → evaluationStatus=COMPLETED, reusabilityScore(0~1), reasoning, roleTaskContextNote,
                  evidenceSufficient(+insufficiencyReason?) 부여
                  (근거 부족으로 인한 NEEDS_REVIEW도 COMPLETED)
         · 실패(기술) → evaluationStatus=UNAVAILABLE, reusabilityScore=null, candidateState=NEEDS_REVIEW,
                  technicalFailureReason(서버 내부 전용; 공개 미노출)
     - "단순 유사 ≠ 재사용성" → Role/Task 맥락을 reasoning에 명시(COMPLETED)
     - deprecated 상태·상충 constraints·Known Limitation 등 부정 신호 → evidenceSufficient=false 근거로 반영
     - **전체 실패 판정**: 대상 ≥1인데 전부 UNAVAILABLE → §1.6 공통 오류 신호(REVERIFICATION_UNAVAILABLE) → 요청 종료
     → verified: VerifiedCandidate[]   (accessible 0개면 [])

5) DecisionClassifierComponent (순수 로직, PBT 대상) — **§7.3/§7.4 정제**
     - classifyAll(verified) → Map<candidateId, CandidateState>   (BR-STATE: UNAVAILABLE⇒NEEDS_REVIEW, COMPLETED만 Score 판정)
     - deriveOverall(states, verified, hasAnyAccessible) → OverallDecision  (BR-OVERALL: 기술 실패↛DEVELOP)

6) EvidenceBuilderComponent.build(verified, states, ctx)
     - 후보별 EvidenceChain 구성: Candidate.evidence[] → EvidenceItem[]{source, evidenceType, title, sourceRef}
       (접근 가능 Asset의 Evidence만 노출; per-asset 권한이므로 접근 가능 후보의 전 Evidence 노출)
     - COMPLETED NEEDS_REVIEW 후보는 stateRationale에 insufficiencyReason 포함
     - **UNAVAILABLE 후보는 stateRationale에 일반적 '평가 미완료' 문구만**(내부 technicalFailureReason 비노출; §1.4)
     → evidenceChains: EvidenceChain[]

7) 조립 (S1)
     - ranking = sort(verified+states) by BR-RANK: **COMPLETED(State→Score→name) → UNAVAILABLE(name→candidateId)**, rank 부여 → RankedCandidate[]
     - capabilityMatch = reasoning 요약(intent.function 대비 적합 서술)
     - excluded 상세(ExcludedCandidate[])는 **서버 내부 로그/감사에만 기록**, 응답에 미포함 (FR-8/NFR-4)
       (권한 필터링은 기본 동작이므로 제외 플래그·개수도 응답에 두지 않음)
     - AdviceResult{ resultId, ranking, overallDecision, overallRationale,
                     isRecommendation=true, evidenceChains } 반환 (공개 응답)
```

### 데이터 흐름 요약 (ASCII)

```
rawText
  │  submitIntent
  ▼
StructuredIntent ──(승인)──► advise
                               │
   search ─► permissionFilter ─► selectTopN ─► reverify ─► classify+deriveOverall ─► buildEvidence ─► assemble
     │            │                 │            │              │                        │
 Candidate[]  {acc,excl}         Top-3     Verified[]   states + overall           EvidenceChain[]
                                                                                        │
                                                                                   AdviceResult
```

---

## 4. submitFeedback 흐름 (C8) — US-4.3 [MVP: 수집]

```
record(resultId, candidateId, verdict) → Feedback{...,timestamp} append (in-memory/경량 저장)
→ 기록 확인 반환
```
- 선별/랭킹 반영은 [Later] US-5.1 (MVP 범위 밖).

---

## 5. LLM 사용 지점 & 결정성 (Q7=A)

| 지점 | LLM 사용 | 결정성 보장 |
|---|---|---|
| C1 structure() | ✅ 자연어 5필드 추출 | demoMode ON = 대표 시나리오 결정적 fixture (실패 시 폴백 아님; 미매칭→명시적 오류, §1.2) |
| C5 reverify() | ✅ Score+근거 산출 | 동상 (Hero/Unhappy 재현). demoMode OFF 실패는 UNAVAILABLE 강등 또는 전체 실패 오류(§1.3) |
| C6 classify/deriveOverall | ❌ (순수 로직) | 완전 결정적(PBT 대상) |
| C2/C3/C4/C7/C8 | ❌ | 결정적 |

> C6를 LLM에서 분리한 이유: 판정 규칙을 순수·검증 가능하게 유지(NFR-5 PBT) + 데모 재현성.

---

## 6. 경계/오류 처리 (NFR Design §1.3~1.6 계약 반영)

**정상(예외 아님) 경로:**
- 접근 가능 후보 0개: 정상 흐름으로 Overall=DEVELOP 반환(HTTP 200).
- 검색 결과 0개: accessible 0개와 동일 경로 → DEVELOP(HTTP 200).

**실패 처리 매트릭스(§1.3):**

| 지점 | 실패 범위 | 처리 | 결과 |
|---|---|---|---|
| 빈 rawText | — | submitIntent 가드, 구조화 미수행 | 400 `EMPTY_INTENT` |
| C1 structure() | 실패/타임아웃 | 명확한 오류 응답으로 요청 종료(폴백 없음) | 502 `INTENT_STRUCTURING_FAILED` / 504 `LLM_TIMEOUT` |
| C5 reverify() | **일부** 후보 실패 | 후보를 UNAVAILABLE로 강등, 정상 응답에 포함(§1.4/§7.1) | 200 (AdviceResult) |
| C5 reverify() | **전체** 후보 실패(대상 ≥1) | AdviceResult 미반환, 공통 오류 | 502 `REVERIFICATION_UNAVAILABLE` |
| demoMode ON 미매칭 입력 | — | 명시적 오류(암묵적 실제 호출 폴백 금지) | 422 `DEMO_FIXTURE_NOT_FOUND` |

- **재시도 없음 + 타임아웃 config**(§1.1). **demoMode OFF는 fixture 폴백 없음**; demoMode ON은 대표 시나리오만 결정적 fixture(§1.2).
- 공통 오류 응답 형태: `{ error: { code, message, requestId } }` — 내부 예외 문자열 미포함(§1.6).
- **기술 실패(UNAVAILABLE)를 DEVELOP으로 오해하지 않는다**(§1.5/BR-OVERALL).

---

## 7. 스토리 커버리지 (U1 백엔드 책임)
US-1.1(접수), US-1.2(structure), US-1.3(clarify), US-2.1(search), US-2.2(filter+TopN),
US-3.1(reverify), US-3.2(classify), US-3.3(NEEDS_REVIEW), US-3.4(Overall DEVELOP),
US-4.2(evidence 구성), US-4.3(feedback 기록). US-4.1은 데이터(ranking/overall) 제공.
