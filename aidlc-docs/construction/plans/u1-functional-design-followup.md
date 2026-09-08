# Functional Design — U1 Follow-up Clarifications

> 답변(Q1~Q9) 분석 결과, 아래 2건에 확인이 필요합니다. `[Answer]:` 태그를 채워주세요.
> 나머지 답변(Q1 A, Q2 D=A방향+임계값 env 변수화, Q3 A(N=3), Q5 A, Q7 A, Q8 A, Q9 A)은 명확 → 그대로 반영합니다.

---

## Follow-up 1 — 랭킹 정렬 vs 스토리 AC 충돌 (Q6 관련) ⚠️

**충돌 내용**:
- Q6 답변 = **C**: 랭킹을 `State 우선(REUSE>EXTEND>NEEDS REVIEW) → Score → assetName` 순으로 정렬.
- 그러나 **US-4.1 AC**는 "**Score 순 랭킹**으로 Source·자산명·Capability Match·Score·Candidate State를 표시"라고 명시.
- aidlc-state.md 정책: 스토리와 분기 시 **stories.md가 authoritative**.

두 요구가 상충하므로 확정이 필요합니다:

A) **Q6=C 유지 (State→Score→assetName)로 진행하고 US-4.1 AC를 갱신** — "State 우선 정렬 + State 내 Score 순"으로 스토리 문구를 맞춤. (사용자 Q6 의도 존중) **(사용자 답변 방향)**

B) **US-4.1 AC 존중 → 순수 Score 내림차순 랭킹**(tie-break assetName). State는 각 행에 표시만 하고 정렬 키는 아님.

C) **혼합**: 화면 랭킹은 Score 순(US-4.1 준수)으로 표시하되, 별도 "권장 순서" 뷰에서 State 우선 정렬 제공.

D) Other

[Answer]: A.

---

## Follow-up 2 — Overall Decision 산출 정의 확정 (Q4=B 관련)

Q4 답변 = **B** ("최고 Score 후보의 State를 Overall로 승격, 단 적합 0 → DEVELOP") + "최종 판단은 사용자" 명시.

"최고 Score 후보"의 범위와 DEVELOP 조건을 아래로 확정해도 될까요?

A) **다음 결정적 규칙으로 확정 (Recommended)**:
   1. 접근 가능 후보 0개 → **DEVELOP**
   2. State가 REUSE 또는 EXTEND EXISTING인 후보가 하나도 없음(적합 0) → **DEVELOP** (US-3.4 정합)
   3. 그 외 → **전체 Top-N 중 Reusability Score 최고 후보의 State**를 Overall로 채택
      (동점 시 State 우선순위 REUSE>EXTEND>NEEDS REVIEW, 그다음 assetName)
   4. Overall은 **권고(recommendation)** 이며 최종 결정은 사용자 몫임을 결과에 명시.
   - ※ 이 규칙에선 최고 Score 후보가 NEEDS REVIEW면 적합 후보가 있어도 Overall=NEEDS REVIEW가 될 수 있음(US-3.4 허용 범위).

B) 규칙 3을 "**적합(REUSE/EXTEND) 후보 중** 최고 Score 후보의 State"로 한정 (NEEDS REVIEW가 최고 Score여도 무시하고 적합 후보 우선).

C) Other

[Answer]: A.
