# Rebuild or Reuse — AI-DLC Discovery Input

> 해커톤 사전 조사에서 수집한 9개 Use Case 중 중복을 줄이고 서로 다른 재사용 문제를 대표하는 4개 Use Case를 선정한 Discovery 입력 자료.
> 아래 Use Case / Happy Path는 실제 업무 Context를 전달하기 위한 Evidence이며, 요구사항·MVP는 해커톤 당일 AI-DLC 과정에서 도출한다.

## 1. Project Context

### Hackathon Theme
AI 기반 S/W 개발 생산성 향상

### Problem Hypothesis
생성형 AI로 S/W·Tool·Agent·Skill 생성 비용과 진입장벽이 낮아지면서, 개발자뿐 아니라 다양한 직군이 업무에 필요한 S/W를 직접 만들 수 있게 되었다.
반면 기존 사내 S/W/자산을 충분히 확인하지 않고 유사한 것을 다시 만드는 중복 개발 가능성도 증가할 수 있다.

### Solution Hypothesis
사용자가 AI로 새로운 S/W를 만들기 전에 Role / Task Context를 이해하고 기존 사내 자산을 탐색·비교하여 재사용 가능성을 판단한다.

### Decision Model
- REUSE: 기존 자산을 그대로 활용
- EXTEND EXISTING: 기존 자산을 기반으로 필요한 부분을 수정/확장
- DEVELOP: 적절한 기존 자산이 없어 신규 개발
- NEEDS REVIEW: 자동 판단이 어려워 추가 검토 필요

### Target Hypothesis
AI를 활용해 자신의 업무에 필요한 S/W / Tool을 만드는 개발자 및 비개발 직군.

### Sampling Note
팀 구성상 Sales/Business Use Case가 더 많이 수집되었으며, Use Case 개수는 Target의 중요도나 우선순위를 의미하지 않는다.

---

## 2. Representative Use Cases

### DEV-01 — 기존 프로젝트 기능 개발 / 개선

**Role**  
Developer

**Business Context / Goal**  
기존 프로젝트에 신규 기능 추가, 성능/버그 개선, 지원 범위 확장.

**As-Is Happy Path**  
요구사항 발생 → 문제/요구사항 파악 → 프로젝트 구조/관련 코드 파악 → Code·문서·Issue·PR 탐색 → 활용 가능성 검토 → 재사용/확장/신규 판단 → 구현 → 테스트/리뷰

**Unhappy Path / Risk**  
관련 자산 탐색에 실패한 뒤 구현을 진행하고, 뒤늦게 유사 기능/PR을 발견하거나 후보 간 Gap 판단에 많은 시간이 소요됨.

---

### DEV-02 — 개발 업무 자동화 Tool / Skill 생성

**Role**  
Developer

**Business Context / Goal**  
반복되는 개발 업무를 Tool, Script, Agent, Skill 등으로 자동화.

**As-Is Happy Path**  
비효율 발견 → 자동화 대상 정의 → 기능/I·O 정리 → 기존 Tool·Script·Agent·Skill 탐색 → 적용 가능성 확인 → 사용/수정/신규 판단 → 구현 → 적용/개선

**Unhappy Path / Risk**  
기존 자산을 모르고 새로 생성하거나, 여러 유사 자산 중 현재 업무에 가장 적합한 것을 선택하는 데 시간이 소요됨.

---

### SALES-01 — 고객 현황 Dashboard

**Role**  
Sales

**Business Context / Goal**  
고객의 Project / Forecast / Risk / 요청사항을 한 화면에서 파악하기 위한 Dashboard 또는 업무용 Tool 구성.

**As-Is Happy Path**  
Need 발생 → 항목 정의 → Data Source 확인 → 기존 Dashboard/Tool 검색 → 재사용 가능성 확인 → 수정/개발 → 검증

**Unhappy Path / Risk**  
기존 Dashboard를 모르고 신규 개발하거나, 유사한 Dashboard를 발견해도 Data Source/API 차이 또는 노후화로 실제 재사용에 실패할 수 있음.

---

### SALES-06 — DDI 경쟁사 센싱

**Role**  
Sales / Marketing

**Business Context / Goal**  
경쟁사 제품 Roadmap, 판매 전망, 시장/고객 동향을 반복적으로 조사·분석하는 업무를 효율화.

**As-Is Happy Path**  
범위 정의 → 기존 업무/자료 확인 → Source 수집 → Cross-check → Outlier/Consensus 검증 → Fact/Estimate 구분 → 분석

**Unhappy Path / Risk**  
완성된 S/W가 없다는 이유로 News 수집, IR 분석, Consensus 등 이미 존재할 수 있는 부분 Capability를 확인하지 않고 전체를 새로 개발할 수 있음.

---

## 3. Other Collected Use Cases

아래 Use Case도 동일한 사전 조사에서 수집된 Evidence이다.
대표 4개보다 중요도가 낮다는 의미는 아니며, 상세 분석의 초점을 좁히기 위해 요약 형태로 보존한다.

- SALES-02 — Forecast 분석 Tool: 고객 Forecast와 내부 기준 간 Gap/Risk 분석. Logic / Schema / Rule 재사용 가능성.
- SALES-03 — 주간보고 / Report 자동화: 메일·회의록·메신저 등의 Fact를 수집해 표준 보고서 생성. Prompt / Connector / Template 재사용 가능성.
- SALES-04 — 고객 요청사항 Tracker: 고객 요청, Owner, Due Date, Status 관리. Workflow / Data Model 재사용 가능성.
- SALES-05 — 반복업무 자동화 Tool: 정기 Excel 취합·가공·메일/보고 자동화. Script / 실행환경 / I/O 재사용 가능성.
- SALES-07 — 중국 Set사 TAM 조사: 출하량·시장 자료 기반 TAM 산출. 수집·비교·Consensus·시각화 Logic 재사용 가능성.

---

## 4. Preliminary Hypotheses — Interpretation, Not Evidence

> 이 섹션은 팀이 수집 자료를 정리하면서 세운 **사전 가설**이다.
> 위 Use Case / Business Context / As-Is Happy Path / Unhappy Path와 구분하며,
> AI-DLC에서 사실로 전제하지 않고 검증·수정한다.

- 단순 Retrieval 결과의 유사도와 실제 Reusability는 다를 수 있다.
- 동일한 자산이라도 Role / Task Context에 따라 재사용 판단이 달라질 수 있다.
- 완성된 S/W뿐 아니라 Code, API, Script, Agent, Skill, Logic, Capability 등 부분 자산도 재사용 대상이 될 수 있다.
- Reusability 판단 기준은 사전에 확정하지 않고 실제 Use Case Evidence에서 도출한다.

---

## 5. Hackathon Constraints

- 해커톤 주제: AI 기반 S/W 개발 생산성 향상
- AWS AI-DLC 사용
- 실제 개발 가능 시간: 약 1일
- 팀 Token Budget: USD 1,000
- 실제 사내 시스템 접근에는 제한이 있을 수 있음
- 필요 시 representative/mock enterprise data 사용

---

## 6. AI-DLC Discovery Guidance

이 문서는 **AI-DLC Intent / Discovery 단계의 입력 Context**이며,
확정된 Requirement, Priority 또는 MVP 정의서가 아니다.

### Evidence
Primary evidence로 취급:
- Role
- Use Case
- Business Context / Goal
- As-Is Happy Path
- Unhappy Path / Risk
- Other Collected Use Cases

### Hypothesis
`Project Context`의 Problem / Solution / Target과
`Preliminary Hypotheses`는 현재 팀의 출발 가설이다.
Evidence와 비교하여 검증하거나 수정할 수 있다.

### AI-DLC가 수행할 일
AI-DLC workflow를 통해 Evidence를 분석하고,
필요한 정보가 부족하거나 모순되면 임의로 가정하지 않고
Clarification Question을 통해 팀의 Context를 추가로 확보한다.

User Need, Requirements, Priority, MVP는
이 입력 문서에서 미리 확정하지 않고 이후 AI-DLC 과정에서 도출한다.

### Human Gate
최종 Requirement 우선순위와 MVP 선택은 팀의 Human Gate로 남긴다.

---

## 7. Source / Reference

팀원별 Use Case / Happy Path 원자료와 통합 조사 결과는 아래 Google Spreadsheet에서 관리한다.

- [2026 디디톤 - Google Sheets](https://docs.google.com/spreadsheets/d/1-CH23F6K0JXEuXBd4_2LTONNhBD2DBFmrMDaHb74rLs/edit?gid=271579705#gid=271579705)
