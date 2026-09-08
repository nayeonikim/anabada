# Rebuild or Reuse — AI-DLC Discovery Input

> 해커톤 사전 조사에서 수집한 9개 Use Case 중, 두 Core Persona의 대표적인 S/W 생성 상황과 서로 다른 재사용 문제를 보여주는 4개 Use Case를 상세 Evidence로 선정한 Discovery 입력 자료.
> 나머지 Use Case도 동일한 조사 Evidence로 보존하며, 아래 Use Case / Happy Path는 실제 업무 Context를 전달하기 위한 입력이다. 요구사항·MVP는 해커톤 당일 AI-DLC 과정에서 도출한다.

## 1. Project Context

### Hackathon Theme
AI 기반 S/W 개발 생산성 향상

### Problem Hypothesis
생성형 AI로 S/W·Tool·Agent·Skill 생성 비용과 진입장벽이 낮아지면서, 개발자뿐 아니라 다양한 직군이 업무에 필요한 S/W를 직접 만들 수 있게 되었다.
반면 기존 사내 S/W/자산을 충분히 확인하지 않고  무질서하게 많은 데이터나 코딩이 생겨남에 따라 회사와 개인의  토큰 낭비 뿐만 아니라 효율성에 대한 고민이 생기고 있다. 또한 유사한 코딩이나 프로그램들이 수없이 생겨 나고 있어 중복이 생기고 있어 이를 저장하고 관리하는 것도  회사 입장에서는 엄청난 낭비 일수 밖에 없다. 이에 따라  코딩전에 사내에 있는 자원이 있는지 검색하고 검증해서 코딩 전에 재사용, 결합 및 확장, 신규 개발, 추가 검토를 판단 하기 위함 이다.  

- 현재 우리가 개발 하려는 서비스는 기존 소프트웨어 개발 단계인 '요구사항 → 설계 → 구현 → 테스트 → 배포 → 운영/유지보수' 에서 추가적인 단계를 만들어서 운영 하는 것이다. 개발 혁신을 위해 기존 '요구사항' 단계 와 '설계' 단계 사이에서, 이미 만들어져 있는 사내의 소프트웨어 자산를 검색 후 '재사용','확장', '개발', '재검토'를 제안함으로서 전체적인 개발의 효율화를 제공한다.

### Solution Hypothesis
사용자가 AI로 새로운 S/W를 만들기 전에 Role / Task Context를 이해하고 기존 사내 자산을 탐색·비교하여 재사용 가능성을 판단한다.

### Current Product Decision — Decision States
현재 팀에서 합의한 서비스의 결과 상태는 아래 4가지이다.

- REUSE: 기존 자산을 그대로 활용
- EXTEND EXISTING: 기존 자산을 기반으로 필요한 부분을 수정/확장
- DEVELOP: 적절한 기존 자산이 없어 신규 개발
- NEEDS REVIEW: 자동 판단이 어려워 추가 검토 필요

이 4개 상태는 현재 Product Decision으로 취급한다.
AI-DLC는 Evidence와 명확히 충돌하는 경우 이를 지적할 수 있고, 분류로 설명하기 어려운 사례가 있다면, 그 이유와 함께 팀에 알려준다.

### Target Hypothesis
AI를 활용해 자신의 업무에 필요한 S/W / Tool을 만드는 사용자.

현재 두 Core Persona Group을 동등한 주요 사용자군으로 본다.

- **Developer**
  - 기존 프로젝트 기능 개발 / 개선
  - Tool / Script / Agent / Skill 생성

- **Business User**
  - Dashboard / 업무용 Tool 생성
  - 반복 업무 자동화를 위한 S/W 생성
  - Tool / Script / Agent / Skill 생성

두 Persona 중 하나를 사전에 Primary / Secondary로 구분하지 않는다.

### Sampling Note
현재 수집된 Use Case 수는 팀 구성의 영향을 받았으며 Persona의 중요도나 우선순위를 의미하지 않는다.

Developer와 Business User는 모두 본 서비스의 Core Persona이다.
Use Case의 빈도보다는 두 Persona에서 공통으로 나타나는 문제와 Role / Task별 차이를 분석하는 데 사용한다.

---

## 2. Representative Use Cases — Core Persona Evidence

### DEV-01 — 기존 프로젝트 기능 개발 / 개선

**Role**  
Developer

**Source**  
NY

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

**Source**  
NY

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

**Source**  
영수

**Business Context / Goal**  
고객의 Project / Forecast / Risk / 요청사항을 한 화면에서 파악하기 위한 Dashboard 또는 업무용 Tool 구성.

**As-Is Happy Path**  
Need 발생 → 항목 정의 → Data Source 확인 → 기존 Dashboard/Tool 검색 → 재사용 가능성 확인 → 수정/개발 → 검증

**Unhappy Path / Risk**  
기존 Dashboard를 모르고 신규 개발하거나, 유사한 Dashboard를 발견해도 Data Source/API 차이 또는 노후화로 실제 재사용에 실패할 수 있음.

---

### SALES-05 — 반복업무 자동화 Tool

**Role**  
Sales / Business

**Source**  
영수

**Business Context / Goal**  
정기적으로 반복되는 Excel 취합·가공·메일/보고 업무를 자동화하는 업무용 Tool 구성.

**As-Is Happy Path**  
반복 Step 정리 → Input / Output 확인 → 기존 Macro·Script·Tool 검색 → 사용 가능성 확인 → 재사용/수정 판단 → 자동화 Tool 구성 → 운영

**Unhappy Path / Risk**  
유사한 자동화 Tool이나 Script가 이미 존재하지만 이를 모르고 새로 만들거나, 파일 형식·실행환경·권한 차이로 기존 자산을 그대로 활용하지 못할 수 있음.

---

## 3. Other Collected Use Cases

아래 Use Case도 동일한 사전 조사에서 수집된 Evidence이다.
대표 4개보다 중요도가 낮다는 의미는 아니며, 상세 분석의 초점을 좁히기 위해 요약 형태로 보존한다.

- SALES-02 — Forecast 분석 Tool (Source: 영수): 고객 Forecast와 내부 기준 간 Gap/Risk 자동 분석.
- SALES-03 — 주간보고 / Report 자동화 (Source: 영수): 메일·회의록·메신저 등에서 Fact를 수집해 표준 보고서 자동 생성.
- SALES-04 — 고객 요청사항 Tracker (Source: 영수): 고객 요청, Owner, Due Date, Status를 한곳에서 관리.
- SALES-06 — DDI 경쟁사 센싱 (Source: JH): 경쟁사 제품 Roadmap, 판매 전망, 시장/고객 동향의 반복 조사·분석을 자동화 Tool로 효율화하려는 사례.
- SALES-07 — 중국 Set사 TAM 조사 (Source: JH): 출하량·시장 자료를 기반으로 TAM을 산출하고 시장 변화를 분석.

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

## 5. Hackathon Context

### 5.1 Implementation Constraints

- 해커톤 주제: AI 기반 S/W 개발 혁신 서비스 만들기
- AWS AI-DLC 사용
- 실제 개발 가능 시간: 약 6시간 (MVP 4시간, 리뷰 및 수정 2시간) 
- 팀 Token Budget: USD 1,000
- 실제 사내 시스템 접근에는 제한이 있을 수 있음
- 필요 시 representative/mock enterprise data 사용


### 5.2 Evaluation Context

> 아래 항목은 User Evidence나 Product Requirement가 아니라,
> 해커톤 결과물의 범위와 우선순위를 판단할 때 참고하는 평가 Context이다.

- AI-DLC 활용: 25
- Problem / Solution: 20
- Creativity: 15
- Completeness: 15
- Usability: 15
- Maintainability / Security: 10

**Evaluation Method**
- AI 평가 + 상호평가
- 별도 발표 없음
- 따라서 Repository, README, AI-DLC 산출물, Evidence chain, 실제 서비스가 스스로 이해 가능하도록 구성하는 것을 중요 제약으로 본다.

평가기준은 User Need나 Requirement를 인위적으로 만들기 위한 근거로 사용하지 않는다.
Requirement 우선순위, MVP 범위, Design / Build / Test 단계의 trade-off를 판단할 때 참고한다.

### 5.3 Enterprise Integration Constraints

- 실제 사내 환경에서는 사용자 인증을 위해 SSO 기반 로그인이 필요하다.
- 사용자의 Role뿐 아니라 각 사내 시스템 및 개별 자산/페이지에 대한 기존 접근 권한에 따라 조회 가능한 정보가 달라질 수 있다.
- Rebuild or Reuse Advisor는 사용자의 기존 권한을 확장하지 않으며, 사용자가 원래 접근할 수 없는 자산이나 Evidence를 검색 결과에 노출하지 않아야 한다.
- GitHub, Confluence, Jira, IMS, BizForce, EDM 등 각 Source의 기존 접근 권한을 존중하여 검색 및 Evidence를 제공해야 한다.
- 사내 문서 Source는 Integration 관점에서 `Confluence`로 통합해 취급한다.
- 해커톤에서는 실제 SSO 및 사내 권한 시스템 대신 representative mock user / permission context를 사용할 수 있다.

---

## 6. AI-DLC Discovery Guidance

이 문서는 **AI-DLC Intent / Discovery 단계의 입력 Context**이며,
확정된 Requirement, Priority 또는 MVP 정의서가 아니다.

### Evidence
Primary evidence로 취급:
- Source
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

### Product Decision
`Current Product Decision — Decision States`의 4개 결과 상태는 현재 팀 합의값이다.
AI-DLC는 Evidence와 충돌하는 경우 문제를 제기할 수 있으나 임의로 변경하지 않는다.

### Persona Analysis Guidance
Developer와 Business User 중 하나를 우선 Persona로 선정하는 것을 Discovery의 기본 목표로 삼지 않는다.

대신 다음을 분석한다.

- 두 Persona에서 공통으로 나타나는 User Need
- 공통으로 제공할 수 있는 Core Capability
- Role / Task Context에 따라 달라지는 Need와 판단 기준
- 하나의 공통 Reusability 흐름으로 처리 가능한 영역
- Role-specific extension이 필요한 영역

대표 Use Case의 수나 전체 수집 Use Case의 빈도를 Persona 우선순위의 근거로 사용하지 않는다.

1일 개발 제약으로 실제 Demo / Hero Scenario를 좁힐 수는 있으나,
이는 Persona의 중요도나 서비스 Target의 우선순위와 동일한 의미로 해석하지 않는다.

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

- [2026 디디톤 - Google Sheets](https://docs.google.com/spreadsheets/d/1-CH23F6K0JXEuXBd4_2LTONNhBD2DBFmrMDaHb74rLs/edit?gid=1700000001#gid=1700000001)
