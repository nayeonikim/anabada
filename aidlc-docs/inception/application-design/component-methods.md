# Component Methods — Rebuild or Reuse Advisor

> 메서드 시그니처 + 고수준 목적 + I/O 타입. **상세 비즈니스 룰/알고리즘은 Functional Design(CONSTRUCTION)에서 확정.**
> 타입은 언어 중립 개념 스키마(구체 기술스택은 NFR Requirements에서 확정).

---

## 공통 개념 타입 (개념 수준)

| Type | Fields (개념) |
|---|---|
| `StructuredIntent` | role, goal, function, data, output |
| `ClarificationRequest` | missingFields[], questions[] |
| `Candidate` | id, source, assetName, assetLink, summary, rawMeta |
| `PermissionContext` | userId, role |
| `Asset` (mock) | id, source, name, summary, allowedRoles[], allowedUsers[] |
| `ExcludedCandidate` | candidate, reason(=접근 불가), evidenceRef |
| `VerifiedCandidate` | candidate, reusabilityScore, reasoning, roleTaskContextNote |
| `CandidateState` | REUSE / EXTEND EXISTING / NEEDS REVIEW |
| `OverallDecision` | REUSE / EXTEND EXISTING / NEEDS REVIEW / DEVELOP |
| `EvidenceChain` | candidateId, source, assetLink, evidenceItems[], stateRationale |
| `AdviceResult` | ranking[], overallDecision, evidenceChains[], excluded[]*, **actionPrompt?** *(CR-001 증분; excluded는 서버 내부 전용)* |
| `ActionPrompt` *(CR-001 증분)* | decisionState, promptText, targetAssetNames[] |

---

## C1. IntentStructuringComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `structure(rawText)` | 자연어 → 5필드 구조화 (LLM) | string | StructuredIntent (일부 필드 빈 값 가능) |
| `detectMissingFields(intent)` | 필수 필드 누락 판정 | StructuredIntent | string[] (누락 필드) |
| `buildClarification(missing)` | 누락 필드별 명료화 질문 생성 | string[] | ClarificationRequest |
| `applyUserRevision(intent, answers)` | 사용자 답변/수정 반영 후 승인 구조 확정 | StructuredIntent, answers | StructuredIntent |

## C2. AssetSearchComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `search(intent)` | 모든 SourceAdapter로 후보 전체 검색·병합 | StructuredIntent | Candidate[] |

## C3. PermissionFilterComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `filter(candidates, ctx)` | 접근 가능/불가 분리 (재검증 前) | Candidate[], PermissionContext | { accessible: Candidate[], excluded: ExcludedCandidate[] } |
| `isAccessible(asset, ctx)` | per-asset 권한 판정 (allowedRoles/allowedUsers) | Asset, PermissionContext | boolean |

## C4. CandidateSelectionComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `selectTopN(accessible, n)` | 관련도 상위 N 선별 | Candidate[], int(기본 3~5) | Candidate[] |
| `hasAnyAccessible(accessible)` | 접근 가능 후보 유무 (0개 → DEVELOP 경로) | Candidate[] | boolean |

## C5. ReVerificationComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `reverify(topN, intent)` | LLM 재검증: Score + 근거 (Role/Task 반영) | Candidate[], StructuredIntent | VerifiedCandidate[] |

## C6. DecisionClassifierComponent (순수 로직 — PBT 대상)
| Method | Purpose | Input | Output |
|---|---|---|---|
| `classifyCandidate(vc)` | 후보별 State 판정 (근거 부족/상충 → NEEDS REVIEW) | VerifiedCandidate | CandidateState |
| `classifyAll(vcs)` | 전체 후보 State 판정 | VerifiedCandidate[] | Map<candidateId, CandidateState> |
| `deriveOverall(states, hasAccessible)` | Overall Decision 산출 (적합 후보 0 → DEVELOP) | Map, boolean | OverallDecision |

## C7. EvidenceBuilderComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `build(vcs, states, ctx)` | 후보별 Evidence chain 구성 (접근 가능 항목만) | VerifiedCandidate[], Map, PermissionContext | EvidenceChain[] |

## C8. FeedbackComponent
| Method | Purpose | Input | Output |
|---|---|---|---|
| `record(resultId, candidateId, feedback)` | 피드백 기록 (MVP: 수집) | ids, feedback(useful/notFit) | 확인/기록 id |

## C9. SourceAdapter (interface) + Registry
| Method | Purpose | Input | Output |
|---|---|---|---|
| `SourceAdapter.search(intent)` | 단일 Source mock 후보 반환 | StructuredIntent | Candidate[] |
| `SourceAdapter.sourceId()` | Source 식별자 | — | string |
| `SourceAdapterRegistry.getAll()` | 등록된 모든 어댑터 조회 | — | SourceAdapter[] |
| `SourceAdapterRegistry.register(adapter)` | 어댑터 등록 (확장 지점) | SourceAdapter | void |

## C10. MockDataStore
| Method | Purpose | Input | Output |
|---|---|---|---|
| `getAssets(source?)` | mock 자산 조회 | source? | Asset[] |
| `getPermissionContext(userIdOrRole)` | mock 권한 context 조회 | id/role | PermissionContext |

## C11. ActionHandoffBuilder *(CR-001 증분)*
| Method | Purpose | Input | Output |
|---|---|---|---|
| `build(intent, overallDecision, overallRationale, ranking, evidenceChains)` | Overall Decision별 목적의 단일 Action Prompt 생성(evidence-grounding 준수, 최소 유용성 포함) | StructuredIntent, OverallDecision, string, RankedCandidate[], EvidenceChain[] | ActionPrompt (실패 시 예외 → orchestrator None 처리·비차단) |

> 내부 보조 로직(Decision→목적 매핑, 대상 Asset 선택, §3.1 문구 판정, 생성 방식 LLM/템플릿)은 U1 Functional/NFR Design(증분)에서 확정. 계약 상세: `change-requests/CR-001-application-design-delta.md`.

---

## AdvisorOrchestratorService (서비스 진입점 — services.md 참조)
| Method | Purpose | Input | Output |
|---|---|---|---|
| `submitIntent(rawText)` | 구조화 + 필요 시 명료화 요청 | string | StructuredIntent \| ClarificationRequest |
| `advise(approvedIntent, ctx)` | 검색→권한필터→TopN→재검증→Decision→Evidence→**Action Handoff(C11)** 일괄 조율 *(CR-001 증분: C7 직후 C11 비차단 호출)* | StructuredIntent, PermissionContext | AdviceResult (+ actionPrompt?) |
| `submitFeedback(resultId, candidateId, feedback)` | 피드백 위임 | ids, feedback | 확인 |
