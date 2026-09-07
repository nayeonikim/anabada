# AI-DLC Stage Operation Prompt Library

해커톤 당일 AI-DLC workflow를 여러 stage에 걸쳐 진행할 때 반복해서 사용할 운영용 Prompt 모음이다.

이 문서는 AI-DLC 자체의 stage routing이나 state transition을 대체하지 않는다. `aidlc-state.md`와 audit 기록은 AI-DLC engine이 관리하는 Source of Truth로 두고, 아래 Prompt는 stage 간 Context drift, 데이터 불일치, 잘못된 가정, 재개 시 누락을 줄이기 위한 보조 운영 규칙으로 사용한다.

## 권장 운영 순서

```text
Stage 시작
  ↓
Stage Kickoff Check
  ↓
Stage 작업
  ↓
Consistency / Evidence Check
  ↓
Human Gate 검토
  ↓
승인
  ↓
Checkpoint Check
  ↓
필요 시 /clear
  ↓
/aidlc 로 재개
  ↓
Resume Verification
  ↓
다음 Stage
```

> `/clear`는 stage 산출물이 생성되었다는 이유만으로 바로 수행하지 않는다. Human Gate 승인과 state/artifact 반영을 확인한 뒤 수행한다.

---

## 1. Stage 시작 — Kickoff Check

새 stage가 시작될 때 이전 stage 결과와 현재 목표를 다시 맞추기 위한 Prompt.

```text
현재 AI-DLC stage를 시작하기 전에 active intent의 aidlc-state.md와 이번 stage가 필요로 하는 이전 산출물을 확인해줘.

다음을 짧게 정리한 뒤 stage를 진행해줘.
1. 현재 Phase / Stage
2. 이번 Stage의 목적
3. 입력으로 사용하는 이전 Stage 산출물
4. 이전 Human Gate에서 확정된 결정
5. 아직 미확정이거나 추가 확인이 필요한 사항

이전 산출물과 현재 state가 모순되거나 필요한 파일이 누락되어 있으면 임의로 가정하지 말고 먼저 알려줘.
```

---

## 2. Evidence / Hypothesis Guard

우리 프로젝트에서 사전 Evidence와 팀의 가설이 섞이지 않도록 하기 위한 Prompt.

```text
이번 Stage에서 사용하는 정보들을 Evidence / Confirmed Decision / Hypothesis / New Assumption으로 구분해서 다뤄줘.

- 실제 조사된 Use Case, Happy Path, Unhappy Path 및 승인된 이전 Stage 결과는 근거로 사용해줘.
- 아직 검증되지 않은 Problem / Solution / Target / Decision Model 가설은 사실처럼 확정하지 말아줘.
- 새 가정이 필요하면 숨겨서 진행하지 말고 명시해줘.
- 기존 Evidence와 충돌하는 내용이 있으면 어느 파일/결정과 충돌하는지 알려줘.
```

---

## 3. Stage 종료 전 — Data / Artifact Consistency Check

Stage 산출물을 Human Gate에 올리기 전에 정합성을 확인하는 공통 Prompt.

```text
이번 Stage 산출물을 Human Gate에 올리기 전에 데이터 및 문서 정합성을 점검해줘.

다음을 확인해줘.
1. 이번 Stage 산출물이 이전 승인된 Requirements / Decisions / Constraints와 모순되지 않는지
2. 같은 개념의 이름, ID, 상태값, Source 명칭이 문서 간 일관적인지
3. 새로 추가된 Requirement / Assumption / Constraint가 근거 없이 생기지 않았는지
4. 삭제되거나 변경된 결정이 downstream 문서에 남아 있지 않은지
5. 필수 입력/산출물 또는 reference가 빠지지 않았는지
6. SSO / Permission / Enterprise Source 제약이 관련 Stage에서 누락되지 않았는지

문제가 있으면 Critical / Major / Minor로 나누고, Human Gate 전에 수정해야 할 항목만 먼저 제시해줘.
문제가 없으면 어떤 항목을 확인했는지 짧게 요약해줘.
```

---

## 4. Mock Enterprise Data 전용 Consistency Check

Mock Asset / Evidence / Permission을 사용하는 Stage에서 추가로 실행한다.

```text
Mock Enterprise Data 정합성을 확인해줘.

확인 대상:
- mock/users.json
- mock/assets.json
- mock/evidence/*.json
- docs/integration/asset-adapter-contract.md
- docs/integration/mock-enterprise-data.md

다음을 검증해줘.
1. Asset의 evidence_refs가 실제 Evidence ID와 모두 연결되는지
2. Evidence의 asset_id가 실제 Asset과 연결되는지
3. source_type이 github / confluence / jira / ims / bizforce / edm 중 하나로 일관되는지
4. Evidence의 access_scope와 Mock User permission scope가 논리적으로 일치하는지
5. 권한이 없는 Source의 Evidence가 해당 사용자에게 노출되는 가정이 없는지
6. lifecycle_status / owner / last_updated / constraints가 서로 모순되지 않는지
7. Mock 데이터에 decision / reuse_score처럼 Advisor가 판단해야 할 결과값이 미리 들어가 있지 않은지
8. 문서의 Adapter Contract와 실제 Mock JSON 구조가 어긋나지 않는지

발견한 문제는 파일명과 ID를 기준으로 알려줘.
```

---

## 5. Human Gate 검토용 Prompt

승인 전에 팀이 무엇을 판단해야 하는지 명확하게 만드는 Prompt.

```text
이번 Stage의 Human Gate 검토를 위해 아래 형식으로 정리해줘.

- Stage 목적
- 이번 Stage에서 확정하려는 핵심 결정
- 주요 산출물
- Evidence에 의해 뒷받침되는 내용
- 아직 남아 있는 가정 / Risk / Open Question
- 다음 Stage에 영향을 주는 결정

마지막에는 팀이 승인할 때 반드시 확인해야 할 항목만 3~5개로 압축해줘.
새로운 설계나 요구사항을 추가하지 말고 현재 산출물을 검토하는 데 집중해줘.
```

---

## 6. Human Gate 승인 후 — Checkpoint Check

`/clear` 또는 세션 전환 전에 state와 artifact가 제대로 보존되었는지 확인하기 위한 Prompt.

```text
이번 Stage의 Human Gate 승인 후 세션을 정리하기 전에 checkpoint 상태를 확인해줘.

1. active intent의 aidlc-state.md에서 이번 Stage가 승인 완료 상태로 반영되었는지
2. Current Status / Session Resume Point가 다음 Stage를 가리키는지
3. 이번 Stage의 필수 산출물이 실제 파일로 존재하는지
4. 이번 승인에서 확정된 핵심 결정이 산출물에 반영되어 있는지
5. audit 기록과 state/artifact 사이에 명백한 불일치가 없는지

직접 state를 임의로 수정하지 말고, 불일치가 있으면 무엇이 어긋났는지만 알려줘.
모두 정상이면 다음 세션에서 재개할 위치를 한 줄로 알려줘.
```

---

## 7. `/clear` 후 재개 — Resume Verification

새 Context에서 `/aidlc`로 workflow를 재개한 뒤 사용할 Prompt.

```text
이전 세션의 대화 내용을 추측하지 말고, 현재 active intent의 aidlc-state.md와 관련 Stage 산출물을 기준으로 작업을 재개해줘.

먼저 다음을 확인해줘.
1. 현재 Phase / Stage
2. 마지막으로 승인 완료된 Stage
3. 다음 Action
4. 이번 Stage에 필요한 이전 산출물
5. Pending artifact / Open Question / 미확정 결정

state와 artifact가 서로 맞지 않거나 승인 여부가 불명확하면 다음 Stage로 진행하지 말고 먼저 알려줘.
정상이라면 현재 Stage를 시작할 준비가 되었는지 짧게 요약해줘.
```

> 실제 재개는 AI-DLC의 기본 resume 동작을 우선 사용한다. Claude Code에서는 새 세션에서 `/aidlc`를 실행해 active intent의 state를 기준으로 이어가는 것을 기본 흐름으로 한다.

---

## 8. Phase 경계 — Cross-Stage Integrity Check

Ideation → Inception, Inception → Construction처럼 큰 경계를 넘기 전에 사용한다.

```text
다음 Phase로 넘어가기 전에 지금까지 승인된 Stage 산출물의 Cross-Stage 정합성을 확인해줘.

특히 다음 연결을 확인해줘.
- Use Case / User Need → Requirements
- Requirements → Priority / MVP
- Requirements → Design
- Design → Data Model / API / UI
- Enterprise Constraint → Authentication / Authorization / Adapter 설계
- Acceptance Criteria → Test Plan

앞 단계에서 승인되지 않은 내용이 뒤 단계에서 확정 사실처럼 사용된 경우를 찾아줘.
Requirement 또는 결정이 변경되었는데 downstream artifact가 갱신되지 않은 경우도 표시해줘.

문제가 없으면 다음 Phase로 넘어가도 되는 이유를 짧게 정리해줘.
```

---

## 9. Context / Token Guard

Stage가 길어지거나 Context 사용량이 커질 때 사용한다.

```text
현재 Stage 진행에 필요한 Context만 유지하도록 정리해줘.

- 현재 Stage에 직접 필요한 state와 upstream artifact만 우선 사용해줘.
- 이미 파일에 확정되어 있는 내용을 대화 Context에서 반복 생성하지 말아줘.
- 이전 전체 대화를 다시 요약하기보다 Source of Truth 문서를 우선 참조해줘.
- 불필요한 대규모 재분석이나 동일 문서 재생성을 피하고, 변경된 부분 중심으로 작업해줘.
- 중요한 결정이나 새 Context는 대화에만 남기지 말고 해당 AI-DLC 산출물에 반영되는지 확인해줘.
```

---

## 10. 문제 발생 시 — State / Artifact Mismatch Check

```text
현재 workflow 진행 상태에 이상이 있는지 확인해줘.

- aidlc-state.md의 Stage 상태
- 실제 Stage 산출물 존재 여부
- 현재/다음 Stage
- Human Gate 승인 여부
- 필요한 upstream artifact

을 서로 비교해줘.

불일치가 있으면 임의로 다음 Stage로 진행하거나 state를 직접 덮어쓰지 말고,
1. 어떤 항목이 불일치하는지
2. 안전하게 재실행해야 하는 Stage가 있는지
3. 기존 산출물 중 보존해야 할 것이 무엇인지
순서로 알려줘.
```

---

## 11. 구현 전 — Design-First Implementation Guard

구현 또는 코드 변경이 승인된 Design과 어긋나지 않도록 하기 위한 공통 Prompt.

```text
구현 또는 코드 변경을 시작하기 전에, 해당 변경이 현재 승인된 Requirements와 Design 산출물에 반영되어 있는지 먼저 확인해줘.

구현 중 새로운 설계 결정, Interface 변경, Data Model 변경, 동작 방식 변경이 필요해진 경우:
1. 먼저 관련 Design 문서를 수정해 변경 내용을 명확히 기록하고,
2. 기존 Requirements 및 다른 Design 산출물과의 정합성을 확인한 뒤,
3. 필요한 Human Gate 또는 승인 절차를 거치고,
4. 승인된 Design을 기준으로 구현을 진행해줘.

코드를 먼저 변경한 뒤 문서를 사후에 맞추는 방식은 피하고, Design artifact를 구현의 Source of Truth로 유지해줘.

단순 버그 수정처럼 기존 Design을 변경하지 않는 경우에는 Design 변경이 불필요한 이유를 확인한 뒤 구현해줘.
```

---

## 해커톤 당일 최소 사용 세트

시간이 부족하면 아래 5개를 우선 사용한다.

1. **Stage 시작**: `Stage Kickoff Check`
2. **Stage 종료**: `Data / Artifact Consistency Check`
3. **승인 후 clear 전**: `Checkpoint Check`
4. **새 세션 재개**: `/aidlc` 실행 후 `Resume Verification`
5. **구현 전/변경 시**: `Design-First Implementation Guard`

Mock/Adapter 관련 Stage에서는 `Mock Enterprise Data Consistency Check`를 추가한다.

## 운영 원칙

- `aidlc-state.md`는 workflow 진행 상태의 Source of Truth로 취급한다.
- Stage state transition을 수동으로 임의 변경하지 않는다.
- Human Gate 승인 전에는 stage가 끝났다고 간주하지 않는다.
- `/clear` 전에 승인 결과와 산출물이 파일에 남았는지 확인한다.
- 새 세션에서는 대화 기억보다 state와 artifact를 우선한다.
- 데이터 불일치나 상충하는 결정은 AI가 임의로 해석하지 않고 Human Gate로 올린다.
- 구현은 승인된 Requirements / Design을 기준으로 진행하고, 설계 변경이 필요한 경우 문서와 승인 절차를 먼저 갱신한다.
- Mock Source는 실제 Enterprise Source를 대표하지만, 최종 Decision 값은 Mock 데이터에 포함하지 않는다.
