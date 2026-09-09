# UI 재디자인 — 요구사항 확인 질문

**작성일**: 2026-09-09
**대상**: U2 Web UI (`frontend/`) — Anabada 검색형 라이트 UI로 재디자인
**참고**: `aidlc-docs/inception/ui-design-comparison.md`, 목표 목업(바탕화면 PNG)

각 질문의 `[Answer]:` 태그 뒤에 알파벳(A/B/C…)을 적어주세요. 보기 중 맞는 게 없으면 마지막 "Other"를 고르고 설명을 적어주세요. 다 하시면 "완료"라고 알려주세요.

---

## Question 1 — 기존 대시보드 처리
현재 다크 3컬럼 대시보드를 어떻게 할까요?

A) 완전히 교체 — 새 Anabada 검색형 UI만 남기고 기존 대시보드/다크테마 제거

B) 새 UI로 교체하되, 다크/라이트 테마 토글은 유지(기본 라이트)

C) 기존 대시보드는 별도 경로/모드로 보존하고 새 UI를 기본으로 추가

X) Other (please describe after [Answer]: tag below)

[Answer]: A, 경로준 사진를 참조해서 최대한 유사하게 만들어

---

## Question 2 — `/intent` 구조화 편집 단계 (가장 중요한 결정)
현재는 자연어 입력 → **구조화된 의도(role/goal/function/data/output)를 사용자가 직접 편집** → `/advise` 순서입니다. 목표 목업의 검색형 흐름에는 이 수동 편집 화면이 없습니다. 어떻게 할까요?

A) 자동 진행 — 검색 제출 시 `/intent`→`/advise`를 연속 호출하고 구조화 편집 화면은 숨김(가장 목업에 가까움). 단, 백엔드가 clarification(추가 질문)을 요구하면 그때만 노출

B) 진행 스텝바 안에서 구조화된 의도를 **읽기 전용**으로 보여주되 편집은 없음

C) 결과 화면에 "의도 수정" 접이식 영역을 두어 필요 시 편집 후 재분석 가능

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 검색 제출 후 /intent → /advise를 자동 연속 호출하고 구조화 의도 편집 화면은 노출하지 않는다. 단, /intent가 clarification이 필요하다고 판단한 경우에만 사용자에게 추가 질문 UI를 노출한다.

---

## Question 3 — AI 진행 스텝바 (4단계, 90%)
목업의 "질문 이해 → 자료 탐색 → 후보 분석 → 판단 생성 (90%)" 진행 표시를 어떻게 구현할까요? (백엔드는 스트리밍 없이 순차 호출입니다)

A) 실제 호출 경계에 매핑 — `/intent` 완료=1·2단계, `/advise` 진행 중=3단계, 응답 도착=4단계 완료(퍼센트는 애니메이션으로 부드럽게)

B) 순수 시각 애니메이션 — 실제 호출 시간에 맞춰 단계가 순차적으로 채워지는 연출(퍼센트는 연출값)

C) 최소 구현 — 단계 아이콘만 표시하고 퍼센트/애니메이션은 생략

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 실제 호출 경계와 진행 단계를 연결하되 percentage는 UX용 애니메이션으로 부드럽게 표현. /advise 응답 대기 중에는 90% 수준에서 유지하고 실제 응답 도착 시 100% 완료 후 결과 화면을 표시.

---

## Question 4 — 권한 컨텍스트(userId / role) 입력 위치
`/advise`에는 사용자 역할(role) 등 권한 컨텍스트가 필요하지만 목업 검색 홈에는 노출되어 있지 않습니다(우상단 "김지훈님" 계정 표시만 있음). 어떻게 할까요?

A) 우상단 계정 메뉴(드롭다운)에서 역할 선택 — 목업의 "김지훈님 ▾"를 실제 역할 전환 UI로 사용

B) 데모 기본값으로 고정(현재처럼 role=Sales 등)하고 UI에 노출하지 않음

C) 예시 질문 칩/데모 프리셋이 역할을 함께 설정(현재 presets 방식 유지, 홈에 프리셋 노출)

X) Other (please describe after [Answer]: tag below)

[Answer]: B. 현재 데모에서는 role=Sales 등 기본값으로 처리하고 검색 홈에는 노출하지 않는다. 향후 실제 SSO 연동 시 로그인 사용자의 권한/role을 자동으로 받아 /advise context에 전달하도록 확장 가능한 구조로 유지한다 김지훈은 DevRel로 바꿔줘

---

## Question 5 — 화면 전환 방식(홈 ↔ 결과)
2단계 흐름의 화면 전환을 어떻게 구현할까요?

A) 상태 기반 뷰 전환 — 라우터 없이 React 상태로 홈/결과 화면 토글(의존성 추가 없음, 현재 구조와 일치)

B) 클라이언트 라우팅 도입 — `react-router` 추가(`/` 홈, `/result` 결과, 뒤로가기·URL 공유 지원)

X) Other (please describe after [Answer]: tag below)

[Answer]: A. React 상태 기반으로 홈 ↔ 분석/결과 화면을 전환한다. 별도 router 의존성은 추가하지 않는다. 결과 화면의 ‘새 질문’으로 홈 상태로 복귀한다

---

## Question 6 — 후보 상세 탭 3개의 내용 매핑
목업 카드 펼침 시 탭 3개(**판단 근거 / 적합도 분석 / 참고 자료**)의 내용을 기존 데이터에서 어떻게 채울까요?

A) 판단 근거=결정 이유(rationale/evidence 요약 불릿), 적합도 분석=점수 근거·상태(evaluationStatus)·강약점, 참고 자료=Evidence의 Source 링크/출처 목록

B) 위 매핑을 따르되, 데이터가 없는 탭은 "정보 없음"으로 비활성 표시

X) Other (please describe after [Answer]: tag below)

[Answer]: X. 기본 매핑은 A를 따른다. 판단 근거=rationale/evidence 기반 판정 이유(REUSE/EXTENSION/NEED REVIEW/DEVELOP), 적합도 분석=점수 근거·evaluationStatus·강점/차이점, 참고 자료=Evidence Source/링크

---

## Question 7 — 브랜딩/카피 변경 범위
브랜드·문구를 목업대로 바꿀까요?

A) 전체 적용 — 앱명 `Rebuild or Reuse Advisor` → **Anabada**, 홈 카피("무엇을 찾고 계신가요?" 등)·푸터("Your Knowledge, Smarter with AI.")·예시 질문 칩 모두 목업대로. package.json name 등 코드 식별자는 유지

B) 화면 표시 문구만 변경하고 예시 질문 칩은 현재 데모 프리셋 내용을 사용

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 사용자에게 노출되는 브랜딩과 카피는 Anabada 기준으로 전체 변경한다. package.json name, API명, 내부 코드 identifier 등 비노출 기술 식별자는 기존 값을 유지

---

## Question 8 — 확장(Extension) 설정 확인
이번 변경에도 기존 확장 설정을 유지할까요? (현재: Security=No, Resiliency=No, Property-Based Testing=Partial). UI 전용 변경이라 대부분 N/A입니다.

A) 기존 설정 그대로 유지

B) 변경 원함 (X에 설명)

X) Other (please describe after [Answer]: tag below)

[Answer]: A. 기존 확장 설정을 그대로 유지

---

## Question 9 — 반응형 대상
목업은 넓은 데스크톱 2-패널처럼 보입니다. 반응형 지원 범위는?

A) 데스크톱 우선 + 모바일 축소(세로 1열) 대응 — 검색 홈은 중앙 정렬, 결과는 세로 흐름

B) 데스크톱 전용(현재처럼 넓은 화면 가정, 모바일 최적화 생략)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

