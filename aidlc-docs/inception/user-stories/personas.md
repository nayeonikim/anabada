# Personas — Rebuild or Reuse Advisor

> Evidence source: `docs/aidlc/discovery-input.md` (§1 Target, §2 Use Cases).
> 두 Persona는 동등한 Core Persona이며 사전 우선순위가 없다. MVP는 Persona별 별도 서비스를 구현하지 않고 공통 Reusability 흐름을 제공한다. 단, 동일한 자산이라도 사용자의 Role과 Task Context에 따라 실제 재사용 가능성에 대한 판단은 달라질 수 있다.

---

## P1 — Developer (개발자)

- **대표 Use Case**: DEV-01(기존 프로젝트 기능 개발/개선), DEV-02(개발 업무 자동화 Tool/Skill 생성)
- **Goal**: 코딩 전에 사내 Code·API·Script·Agent·Skill 등 자산을 확인하여 재사용/확장/신규 개발을 판단, 중복 개발과 토큰 낭비 방지.
- **주요 Task Context**:
  - 신규 기능 추가, 성능/버그 개선, 지원 범위 확장
  - 반복 개발 업무를 Tool/Script/Agent/Skill로 자동화
- **Pain (As-Is)**: 관련 자산 탐색 실패 후 구현 → 뒤늦게 유사 기능/PR 발견, 후보 간 Gap 판단에 시간 소요.
- **주로 사용하는 Data Sources**: GitHub(코드·Issue·PR) 중심, Confluence 문서. Advisor 탐색 범위는 여기에 제한되지 않고, 권한이 있는 전체 Source를 검색한다.
- **재사용 판단 주요 Context**: Capability Fit. Code/API/Interface Compatibility. Maintenance Status. Modification Effort

## P2 — Business User (Sales / Business)

- **대표 Use Case**: SALES-01(고객 현황 Dashboard), SALES-05(반복업무 자동화 Tool)
- **Goal**: 업무에 필요한 Dashboard/자동화 Tool을 만들기 전에 기존 자산을 찾아 재사용 여부를 판단.
- **주요 Task Context**:
  - 고객 Project/Forecast/Risk/요청사항을 한 화면에서 보는 Dashboard 구성
  - 반복 Excel 취합·가공·보고 업무 자동화
- **Pain (As-Is)**: 기존 Dashboard/Tool을 모르고 신규 개발, 또는 발견해도 Data Source/API 차이·노후화로 재사용 실패.
- **주로 사용하는 Data Sources**: Confluence, BizForce, 업무 데이터. 코드보다 완성 Tool/Template 관점. Advisor 탐색 범위는 여기에 제한되지 않고, 권한이 있는 전체 Source를 검색한다.
- **재사용 판단 주요 Context**: Business Purpose Fit. Data Source/Input-Output. Compatibility. Freshness. Business Applicability. Modification Effort.

---

## 공통점 (Common Need)
- 만들기 전에 "이미 있는가?"를 빠르고 신뢰 있게 확인하고 싶다.
- 단순 유사도가 아니라 **내 Role/Task 맥락에서 실제 재사용 가능한지** 판단과 근거(Evidence)를 원한다.

## 차이점 (Role/Task Difference)
- 재사용 대상 자산 유형: Developer=Code/API/Script/Agent/Skill, Business=Dashboard/Tool/Template.
- 판단 기준 강조점: Developer=코드 호환·유지보수, Business=Data Source·최신성·업무 적합성.
