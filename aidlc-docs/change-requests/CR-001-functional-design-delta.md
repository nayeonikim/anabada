# CR-001 Action Handoff — U1 Functional Design Delta (증분)

> **U1 Functional Design (증분) 산출물** for CR-001 Product Scope Change.
> 기존 `construction/u1-advisor-backend/functional-design/*`에 append-only 반영(각 파일 CR-001 마커). 본 문서가 CR-001 상세 로직 증분의 **authoritative 요약·근거**.
> 근거: `CR-001-application-design-delta.md`(C11·DTO 계약·D1~D3), `CR-001-requirements-delta.md`(FR-11/FR-12/NFR-8+§3.1), `stories.md` US-6.1/US-6.2.
> Prompt **생성 방식(LLM/템플릿/혼합)·PBT 적용 지점·demoMode 결정성**은 U1 NFR Design(증분)에서 확정. 구현·테스트는 Code Generation(증분).

---

## 1. 신규 도메인 엔티티

### 1.1 ActionPrompt (C11 산출 — 공개 DTO 원천)
| Field | 개념 타입 | 설명 | 제약 |
|---|---|---|---|
| decisionState | OverallDecision | 이 Prompt가 대응하는 **현재 산출된 Overall Decision** (REUSE/EXTEND_EXISTING/DEVELOP/NEEDS_REVIEW) | 항상 = 해당 요청의 overallDecision (INV-HANDOFF-1) |
| promptText | string | 도구 비종속 **자연어 Prompt 전문**(사용자 입력 언어). **목표·근거·다음 작업·확인 사항** 포함. Copy 대상 | 비어 있지 않음(생성 성공 시) |
| targetAssetNames | string[] | REUSE/EXTEND의 **대상 Asset명**(접근 가능 ranking에서 도출). DEVELOP/NEEDS_REVIEW는 `[]` | REUSE/EXTEND ⇒ 접근 가능 후보명 부분집합·비어있지 않음 (INV-HANDOFF-2) |

> **언어**: promptText는 사용자 Intent 입력 언어를 따른다(기본 한국어, 기술용어 영문 혼용). StructuredIntent 필드 언어에서 도출.
> **비노출 구조(NFR-8)**: ActionPrompt에는 후보 id·미인가 자산·technicalFailureReason·제외 개수/플래그 필드가 **부재**(기존 §3.2 Type-Enforced Non-Disclosure 계승).

### 1.2 AdviceResult 확장 (append-only)
- `AdviceResult`에 **`actionPrompt: ActionPrompt | null`** 추가. 기존 필드(resultId/ranking/overallDecision/overallRationale/isRecommendation/evidenceChains) **불변**.
- 생성 실패/부재 시 `actionPrompt = null` — 나머지 결과는 정상(비차단, INV-HANDOFF-4).

---

## 2. BR-HANDOFF — Action Prompt 생성 (C11, C7 직후) · US-6.1 / FR-11 / NFR-8

**입력(grounding — 접근 가능 공개 투영만)**: `intent`(확정 StructuredIntent), `overallDecision`, `overallRationale`, `ranking`(RankedCandidate[], 미인가 제외·내부사유 미투영), `evidenceChains`(접근 가능 Evidence만).
**출력**: `ActionPrompt` (실패 시 예외 → orchestrator가 None 처리).

### 2.1 Overall Decision → Prompt 목적 매핑 (결정적·순수 선택)
| overallDecision | Prompt 목적 | 대상 Asset | 핵심 근거 |
|---|---|---|---|
| **REUSE** | 선택된 기존 Asset **활용·통합** | ✅ 최상위 접근 가능 후보(driving candidate) | 대상 Asset의 evidenceChains + overallRationale |
| **EXTEND_EXISTING** | 기존 Asset과 요구의 **Gap 기반 수정·확장** | ✅ 최상위 접근 가능 후보 | 대상 Asset evidence + intent 대비 Gap(**확인 질문화**) |
| **DEVELOP** | **개발 시작** | ❌ (`[]`) | **확정된 Structured Intent**(핵심) + overallRationale |
| **NEEDS_REVIEW** | **개발 미시작** Review Prompt — 추가 Evidence·질문 정리 | ❌ (`[]`) | overallRationale + (§2.4) 평가 미완료 시 후보 비식별 일반 문구 |

### 2.2 대상 Asset 선택 규칙 (REUSE / EXTEND)
- 대상 = **ranking 최상위 후보(ranking[0])** — BR-OVERALL상 Overall을 결정한 최고 Score COMPLETED 후보. `ranking`은 접근 가능 후보만 포함하므로 대상 Asset명은 노출 가능.
- `targetAssetNames = [ranking[0].assetName]` (동점으로 같은 driving state 후보가 복수면 포함 가능). 본문에서도 해당 Asset을 명확히 식별.
- **정합 가드**: overallDecision이 REUSE/EXTEND인데 접근 가능 대상 후보를 식별할 수 없으면(비정상), **Asset을 지어내지 않고** 생성 실패로 처리(→ 비차단 None, §2.5). (파이프라인 정상 시 BR-OVERALL 보장으로 미발생)

### 2.3 최소 유용성 (모든 Decision 공통) · US-6.1 AC
promptText는 다음 4요소를 포함한다:
- **목표(Goal)**: Decision 목적에 맞는 다음 개발 목표.
- **근거(Rationale)**: overallRationale + 접근 가능 evidence 요약(근거 밖 금지).
- **다음 작업(Next Actions)**: 사용자가 외부 AI 개발 도구에서 수행할 실행 단계(도구 비종속).
- **확인 사항(Checks)**: 진행 전 확인/검증 항목. **확인되지 않은 Gap·전제는 사실 단정 금지 → 확인 질문 형태**로 표현.

### 2.4 NEEDS_REVIEW Review Prompt + §3.1 경계
- 개발을 **시작하지 않고**, 판단 확정에 필요한 **추가 Evidence·질문**을 정리.
- 평가 미완료(UNAVAILABLE)가 원인인 경우(= ranking에 evaluationStatus=UNAVAILABLE 존재): 후보 식별정보·후보별 상세·내부 기술사유 **없이**, **"일부 후보의 평가가 완료되지 않아 판단 확정을 위해 추가 검토가 필요하다"** 수준의 **후보 비식별·집계 일반 문구**만 포함 가능. (NFR-8 §3.1)
- UNAVAILABLE 존재 여부는 ranking의 `evaluationStatus`로 판정(공개 투영 범위 내). `technicalFailureReason`은 근거·본문에서 배제.

### 2.5 Evidence-Grounding & 비노출 (NFR-8)
- **근거 한정**: intent · overallDecision · overallRationale · 접근 가능 ranking · 접근 가능 evidenceChains **만** 근거로 사용. 근거 밖 생성(환각) 금지.
- **비노출**: 미인가·권한 제외 후보, 후보별 내부정보, technicalFailureReason, 제외 개수/플래그를 promptText·targetAssetNames·근거에 **포함 금지**. (입력이 이미 공개 투영이라 구조적으로 유입 불가 — 추가로 생성 산출물에서도 재확인)
- **확인 질문화**: 확인되지 않은 Gap/전제는 확인 질문으로 표현(EXTEND의 Gap 포함).

### 2.6 생성 실패 격리 (비차단) — BR-HANDOFF-FAIL · FR-11 / delta §4
- C11 생성이 실패(예: 생성 방식이 LLM이면 LLM 오류/타임아웃, 또는 §2.2 정합 가드 위반)하면 **예외를 던지고**, orchestrator가 이를 잡아 `actionPrompt=None`으로 처리(내부 감사 로깅). 
- 기존 Decision·Evidence·ranking 결과는 **유지·정상 반환**(HTTP 200). Action Handoff는 핵심 결과의 선행 조건이 아니다.

---

## 3. 불변식 (검증 대상 — 상세 PBT/예제 배분은 NFR Design)

| ID | 불변식 |
|---|---|
| **INV-HANDOFF-1** | `ActionPrompt.decisionState == 요청의 overallDecision`. |
| **INV-HANDOFF-2** | `overall ∈ {REUSE, EXTEND_EXISTING} ⇒ targetAssetNames ≠ [] ∧ targetAssetNames ⊆ {접근 가능 ranking assetName}`; `overall ∈ {DEVELOP, NEEDS_REVIEW} ⇒ targetAssetNames == []`. |
| **INV-HANDOFF-3** | promptText·targetAssetNames는 미인가/제외 자산 식별자·technicalFailureReason·제외 개수/플래그를 포함하지 않는다(grounding-only). |
| **INV-HANDOFF-4** | 생성 실패 ⇒ `actionPrompt == None` ∧ AdviceResult의 ranking/overallDecision/overallRationale/isRecommendation/evidenceChains **불변**(비차단). |
| **INV-HANDOFF-5** | `overall == NEEDS_REVIEW ∧ ¬(∃ UNAVAILABLE in ranking) ⇒ promptText에 '평가 미완료' 일반 문구 미포함`(§3.1은 UNAVAILABLE 존재 시에만). |

> **PBT 후보(§NFR Design 확정)**: Overall→목적/대상요구/§3.1-허용 여부 **매핑 선택 로직**은 순수·결정적 → PBT 대상 후보(INV-HANDOFF-1/2/5). 실제 문안 생성(LLM/템플릿)은 예제 기반 검증. 배분은 NFR Design.

---

## 4. business-logic-model 증분 (advise 흐름)

`advise` 조립(7단계) **직후 8단계** 삽입:
```
7) 조립: ranking(BR-RANK) + rank + capabilityMatch
8) [CR-001] ActionHandoffBuilder.build(intent, overallDecision, overallRationale, ranking, evidenceChains)  (BR-HANDOFF)
     try   → actionPrompt (Decision별 목적, 최소 유용성, grounding 준수)
     except→ actionPrompt = None  (내부 감사 로깅; 비차단, BR-HANDOFF-FAIL)
9) AdviceResult{ …, actionPrompt } 반환 (공개 응답 actionHandoff)
```
**실패 매트릭스 추가 행**:
| 지점 | 실패 범위 | 처리 | 결과 |
|---|---|---|---|
| C11 ActionHandoffBuilder | 생성 실패(방식 LLM이면 오류/타임아웃, 또는 정합 가드) | actionPrompt=None, 기존 결과 유지(비차단) | 200 (AdviceResult, `actionHandoff=null`) |

---

## 5. 스토리·FR 트레이스
- US-6.1 / FR-11 → BR-HANDOFF(§2), ActionPrompt 엔티티(§1), INV-HANDOFF-1~5.
- NFR-8 / §3.1 → BR-HANDOFF §2.4·§2.5, INV-HANDOFF-3/5.
- delta §4 비차단 → BR-HANDOFF-FAIL(§2.6), INV-HANDOFF-4.
- US-6.2 / FR-12 → U2(표시·Copy); U1은 `actionPrompt`/`actionHandoff` 데이터 제공(계약: application-design-delta §4).

## 6. 다음 단계 이관
- **NFR Design(증분)**: Prompt 생성 방식(LLM vs 템플릿 vs 혼합), demoMode 결정성(fixture), PBT vs 예제 배분(INV-HANDOFF 매핑=PBT 후보), 공개 DTO 매핑 재확인.
- **Code Generation(증분)**: `ActionPrompt`/`AdviceResult.actionPrompt`/`ActionPromptDTO`/`AdviceResponse.actionHandoff` + `app/components/action_handoff.py`(C11) + orchestrator §8 통합(try/except) + 테스트(Decision 4종·INV-HANDOFF-1~5·비회귀).
