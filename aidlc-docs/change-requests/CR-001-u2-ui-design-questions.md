# CR-001 U2 UI Design — 열린 결정 질문

각 질문에 `[Answer]:` 뒤 letter로 답해 주세요. (배치 Q1은 이미 사용자 승인으로 확정 → 아래 미포함)
권장안을 표기했으나 **자동 확정하지 않습니다.** 답을 채우시면 UI Design 문서 §7을 확정으로 갱신합니다.

## Question 1 (Q-TARGET) 대상 자산 줄
REUSE/EXTEND일 때 `targetAssetNames`(예: Customer 360 Dashboard)를 "대상 자산: ..." 줄로 별도 표시할까요?

A) 표시한다 — Decision 배지 옆/아래에 "대상 자산: ..." 한 줄 (권장, 최소 유용성 · 어떤 자산에 대한 실행인지 명확)

B) 표시하지 않는다 — 프롬프트 본문이 자산명을 이미 포함하므로 생략

C) Other (please describe after [Answer]: tag below)

[Answer]:

## Question 2 (Q-NULL) 프롬프트 부재(null) 안내 위치
`actionHandoff = null`(생성 실패)일 때 부재 안내를 어디에 둘까요?

A) 최종 판정 배너 **안** 하단에 흐린 1줄 (권장, 판정과 함께 묶여 맥락 유지)

B) 최종 판정 배너 **아래** 별도 줄/블록

C) Other (please describe after [Answer]: tag below)

[Answer]:

## Question 3 (Q-LABEL) NEEDS_REVIEW / DEVELOP 패널 라벨
REUSE/EXTEND가 아닌 경우(NEEDS_REVIEW·DEVELOP) 프롬프트 패널 라벨을 어떻게 할까요?

A) "실행 프롬프트" 고정 (권장, 최소 변경 · Decision 배지와 (참고용) 컨텍스트가 성격을 전달)

B) Decision별 적응 — NEEDS_REVIEW/DEVELOP는 "다음 단계 프롬프트"로 라벨 변경

C) Other (please describe after [Answer]: tag below)

[Answer]:

## Question 4 (Q-TEST) 검증 범위
frontend는 현재 유닛 테스트 하네스가 없습니다. 검증을 어디까지 할까요?

A) `tsc --noEmit` + `vite build` + demoMode 수동 스모크로 한정 (권장, NFR-minimization 준수 · 하네스 미도입)

B) 최소 유닛 테스트 하네스(vitest 등) 신규 도입 + Copy/부재 로직 테스트 추가

C) Other (please describe after [Answer]: tag below)

[Answer]:
