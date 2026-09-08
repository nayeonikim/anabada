# User Stories — Rebuild or Reuse Advisor

> Evidence source: `docs/aidlc/discovery-input.md` + `requirements.md` (FR-1..FR-10, NFR-1..NFR-7).
> **Approach**: Epic 그룹 + 각 Epic 내부는 User Journey 순서(Intent → 구조화 → 검색 → Permission Filter → Top-N → LLM 재검증 → Decision → Evidence → 피드백).
> **INVEST** 준수. 모든 스토리에 **[MVP]** 또는 **[Later]** 태그. **Hero Scenario** 스토리에는 대표 mock 데이터 예시 첨부.
> **AC 형식**: Given / When / Then.
> **Personas**: P1 Developer, P2 Business User (둘 다 = 공통).

---

## 🎯 Hero Scenario (Persona 무관 공통 흐름)

한 사용자가 만들려는 S/W를 자연어로 입력 → AI가 구조화 → 사내 자산(mock) 검색 → 상위 후보 LLM 재검증 → Decision State 분류 → 권한 필터 → 랭킹 + Evidence를 웹 화면에서 비교. Hero 스토리: **US-1.1, US-1.2, US-2.1, US-3.1, US-3.2, US-4.1, US-4.2**.

---

## Epic 1 — Intent Capture & Structuring
*목적: 사용자의 만들려는 의도를 구조화된 형태로 확보한다.*

### US-1.1 자연어 Intent 입력 **[MVP]** · Hero
- **As a** 사용자(P1/P2), **I want** 만들려는 S/W를 자연어로 입력하고 싶다, **so that** 형식을 몰라도 바로 재사용 판단을 시작할 수 있다.
- **AC**
  - Given 웹 화면의 Intent 입력 영역, When 자연어 설명을 입력하고 제출하면, Then 시스템이 입력을 접수하고 구조화 단계로 전달한다.
  - Given 빈 입력, When 제출하면, Then 입력을 요구하는 안내를 표시한다.
- **Example (mock)**: `"고객별 Forecast와 내부 기준의 Gap을 한 화면에서 보는 대시보드를 만들고 싶다"` (SALES-01 계열)

### US-1.2 Intent 구조화 (Role/Goal/Function/Data/Output) **[MVP]** · Hero
- **As a** 사용자, **I want** AI가 내 자연어 의도를 Role/Goal/Function/Data/Output으로 정리해주길 원한다, **so that** 검색과 판단이 내 맥락에 맞게 이뤄진다.
- **AC**
  - Given 자연어 Intent, When 구조화를 수행하면, Then Role·Goal·Function·Data·Output 5개 필드로 요약해 사용자에게 보여준다.
  - Given 구조화 결과, When 사용자가 확인하면, Then 해당 구조를 검색 입력으로 사용한다.
- **Example (mock)**: Role=Sales, Goal=고객 Forecast Gap 파악, Function=Forecast vs 기준 비교/시각화, Data=고객 Forecast·내부 기준, Output=대시보드.

### US-1.3 모호한 의도에 대한 추가 질문 & 승인 **[MVP]**
- **As a** 사용자, **I want** 의도가 불명확할 때 AI가 임의 가정 대신 되물어 확인받길 원한다, **so that** 잘못된 검색/판단을 피한다.
- **AC**
  - Given 구조화 신뢰도가 낮거나 필드가 비면, When 구조화하면, Then 부족한 필드에 대한 명료화 질문을 제시한다.
  - Given 사용자가 답하거나 구조를 수정하면, When 승인하면, Then 승인된 구조로만 다음 단계를 진행한다.

---

## Epic 2 — Asset Retrieval (Multi-Source, mock)
*목적: 구조화된 Intent로 접근 가능한 사내 자산 후보를 찾는다.*

### US-2.1 Multi-Source 자산 검색 & 후보 선별 **[MVP]** · Hero
- **As a** 사용자, **I want** 구조화된 Intent로 여러 Source(GitHub/Confluence/Jira/IMS/BizForce/EDM 대표 mock)를 검색해 후보 자산을 찾고 싶다, **so that** 흩어진 자산을 한 번에 확인한다.
- **AC**
  - Given 승인된 구조화 Intent, When 검색을 수행하면, Then 여러 Source의 mock 자산에서 관련 후보 목록을 반환한다.
  - Given 후보 목록, When 선별하면, Then 재검증 대상 상위 N개(기본 3~5)를 다음 단계로 넘긴다.
  - Given 각 후보, Then Source·자산 식별자·요약이 함께 유지된다.
- **Example (mock)**: 후보 예 — GitHub `forecast-gap-lib`, Confluence `고객대시보드 표준 가이드`, BizForce `Sales Forecast 리포트 템플릿`.

### US-2.2 권한 없는 자산 제외 (Permission Filter) **[MVP]** · Unhappy
- **As a** 사용자, **I want** 내가 접근 권한이 없는 자산은 결과에서 제외되길 원한다, **so that** 볼 수 없는 자산을 잘못 추천받지 않는다. (FR-8, discovery §5.3)
- **AC**
  - Given mock permission context(Role + 자산별 접근 권한), When 검색 결과를 구성하면, Then 사용자가 접근 불가한 자산과 그 Evidence를 결과에서 제외한다.
  - Given 접근 가능 자산이 없으면, Then 접근 가능한 후보가 없음을 명시한다(권한 확장하지 않음).
- **최소 구현**: 접근 불가 자산 제외를 검증하는 대표 mock/test case 1개.

---

## Epic 3 — Reusability Re-verification & Decision
*목적: 유사도가 아니라 실제 재사용 가능성을 Role/Task 맥락에서 판단한다.*

### US-3.1 상위 후보 LLM 재사용성 재검증 **[MVP]** · Hero
- **As a** 사용자, **I want** 상위 후보를 내 Role/Task 맥락으로 재검증받고 싶다, **so that** "단순 유사 ≠ 실제 재사용 가능"을 걸러낸다. (FR-4, discovery §4)
- **AC**
  - Given 상위 N개 후보 + 구조화 Intent, When LLM 재검증을 수행하면, Then 각 후보에 Reusability Score와 판단 근거를 부여한다.
  - Given 재검증 결과, Then Role/Task 맥락 반영 여부가 근거에 드러난다.
- **Example (mock)**: `forecast-gap-lib`는 Data Source가 일치해 높은 Score, `고객대시보드 가이드`는 문서라 부분 참고로 낮은 Score.

### US-3.2 Decision State 분류 **[MVP]** · Hero
- **As a** 사용자, **I want** 각 후보가 REUSE/EXTEND EXISTING/DEVELOP/NEEDS REVIEW로 분류되길 원한다, **so that** 다음 행동을 바로 정한다. (FR-5)
- **AC**
  - Given 재검증된 후보, When 분류하면, Then 각 후보에 4개 Decision State 중 하나를 부여한다.
  - Given 분류 결과, Then 각 State 부여 근거가 Evidence와 연결된다.
- **Example (mock)**: `forecast-gap-lib` → EXTEND EXISTING, `Forecast 리포트 템플릿` → REUSE.

### US-3.3 근거 부족 시 NEEDS REVIEW **[MVP]** · Unhappy
- **As a** 사용자, **I want** Evidence가 부족하거나 모호할 때 AI가 억지 결론 대신 NEEDS REVIEW로 표시하길 원한다, **so that** 잘못된 자동 판단을 신뢰하지 않는다.
- **AC**
  - Given 후보의 Evidence가 불충분/상충, When 분류하면, Then NEEDS REVIEW로 표시하고 부족한 근거를 명시한다.
- **최소 구현**: NEEDS REVIEW를 유발하는 대표 mock/test case 1개.

### US-3.4 적합 자산 없음 → DEVELOP 권고 **[MVP]** · Unhappy
- **As a** 사용자, **I want** 재사용 가능한 적합 자산이 없을 때 신규 개발(DEVELOP)을 권고받고 싶다, **so that** 없는 자산을 억지로 재사용하지 않는다.
- **AC**
  - Given 접근 가능 후보 중 적합한 것이 없으면, When 분류하면, Then 전체 판단을 DEVELOP로 제시하고 그 이유를 밝힌다.
- **최소 구현**: DEVELOP를 유발하는 대표 mock/test case 1개.

---

## Epic 4 — Results, Comparison & Evidence
*목적: 판단 결과를 근거와 함께 한 화면에서 비교·전달한다.*

### US-4.1 후보 랭킹 결과 화면 **[MVP]** · Hero
- **As a** 사용자, **I want** 후보 자산을 랭킹으로 비교(Source·Reusability Score·Decision State)하고 싶다, **so that** 최적 선택을 빠르게 한다. (FR-6, FR-10)
- **AC**
  - Given 분류된 후보들, When 결과 화면을 열면, Then Score 순 랭킹으로 Source·자산명·Capability Match·Score·Decision State를 한 화면에 표시한다.
  - Given 결과 화면, Then Search→Compare→Decide 흐름이 시각적으로 드러난다.
- **Example (mock)**: 1위 `Forecast 리포트 템플릿`(REUSE, 0.9), 2위 `forecast-gap-lib`(EXTEND, 0.8), 3위 `고객대시보드 가이드`(NEEDS REVIEW, 0.4).

### US-4.2 후보별 Evidence Chain **[MVP]** · Hero
- **As a** 사용자, **I want** 각 추천의 Source·자산 링크·관련 Evidence·판단 근거를 보고 싶다, **so that** Black-box 없이 판단을 신뢰·추적한다. (FR-7, FR-8, NFR-1)
- **AC**
  - Given 랭킹의 각 후보, When 상세를 열면, Then Source·자산 링크·관련 Evidence·Decision State 근거를 제공한다.
  - Given 결과에 포함된 Evidence, Then 사용자가 접근 가능한 것만 노출된다.
- **Example (mock)**: `Forecast 리포트 템플릿` → Source=BizForce, 근거="입출력/Data Source 일치, 최신 업데이트".

### US-4.3 결과 피드백 수집 **[MVP]** / 선별 고도화 **[Later]**
- **As a** 사용자, **I want** 상위 결과에 피드백(유용/부적합)을 주고 싶다, **so that** 추천 품질이 개선된다. (FR-9)
- **AC**
  - Given 랭킹 결과, When 사용자가 후보에 피드백하면, Then 피드백을 기록한다. **[MVP]**
  - Given 누적 피드백, When 이후 검색하면, Then 선별/랭킹 방식에 반영한다. **[Later]**

---

## Epic 5 — Extension & Real Integration **[Later]**
*목적: MVP 이후 확장. 삭제하지 않고 비전 위치를 표시.*

### US-5.1 Role-specific 추천 조정 **[Later]**
- **As a** 특정 Role 사용자, **I want** 내 Role에 맞춘 자산 유형/판단 기준 가중치를 원한다, **so that** Role별 재사용 판단이 정교해진다. (discovery Persona Analysis)

### US-5.2 실제 Source & SSO 연동 **[Later]**
- **As a** 조직, **I want** mock을 실제 GitHub/Confluence/Jira/IMS/BizForce/EDM 및 AD SSO로 대체하고 싶다, **so that** 실제 권한·자산 기반으로 동작한다. (NFR-3, discovery §5.3)

---

## Persona ↔ Story Mapping

| Story | P1 Developer | P2 Business User |
|---|---|---|
| US-1.1 / US-1.2 / US-1.3 | ✅ | ✅ |
| US-2.1 / US-2.2 | ✅ | ✅ |
| US-3.1 / US-3.2 / US-3.3 / US-3.4 | ✅ | ✅ |
| US-4.1 / US-4.2 / US-4.3 | ✅ | ✅ |
| US-5.1 | ✅ (Code/API/Skill 가중) | ✅ (Dashboard/Tool 가중) |
| US-5.2 | ✅ | ✅ |

*모든 MVP 스토리는 Persona 무관 공통 흐름으로 두 Persona가 공유한다 (핵심 가설: 직군 무관 재사용 판단 지원).*

---

## MVP / Later 요약

- **[MVP]**: US-1.1, US-1.2, US-1.3, US-2.1, US-2.2, US-3.1, US-3.2, US-3.3, US-3.4, US-4.1, US-4.2, US-4.3(피드백 수집)
- **[Later]**: US-4.3(선별 고도화), US-5.1, US-5.2
