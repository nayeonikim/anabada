# User Stories — Rebuild or Reuse Advisor

> Evidence source: `docs/aidlc/discovery-input.md` + `requirements.md` (FR-1..FR-10, NFR-1..NFR-7).
> **Approach**: Epic 그룹 + 각 Epic 내부는 User Journey 순서(Intent → 구조화 → 검색 → Permission Filter → Top-N → LLM 재검증 → Decision → Evidence → 피드백).
> **INVEST** 준수. 모든 스토리에 **[MVP]** 또는 **[Later]** 태그. **Hero Scenario** 스토리에는 대표 mock 데이터 예시 첨부.
> **AC 형식**: Given / When / Then.
> **Personas**: P1 Developer, P2 Business User (둘 다 = 공통).

---

## 🎯 Hero Scenario (Persona 무관 공통 흐름)

한 사용자가 만들려는 S/W를 자연어로 입력 → AI가 구조화 → 사내 자산(mock) 검색 → **권한 필터(Permission Filter)로 접근 불가 자산 제외** → 접근 가능 후보 중 상위 N개(Top-N) 선별 → 상위 후보 LLM 재검증 → Decision(후보별 State + Overall) 분류 → 랭킹 + Evidence를 웹 화면에서 비교. Hero 스토리: **US-1.1, US-1.2, US-2.1, US-2.2, US-3.1, US-3.2, US-4.1, US-4.2**.

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
- **모호함 기준(명시적)**: 구조화 결과에서 **Role / Goal / Function / Data / Output 5개 필수 필드 중 하나 이상이 누락(빈 값)** 되면 "의도 불명확"으로 판단한다.
- **AC**
  - Given 구조화 결과에 Role/Goal/Function/Data/Output 중 누락된 필수 필드가 있으면, When 구조화하면, Then 누락된 각 필드에 대한 명료화 질문을 제시한다.
  - Given 5개 필수 필드가 모두 채워지면, When 구조화하면, Then 추가 질문 없이 사용자 확인 단계로 진행한다.
  - Given 사용자가 답하거나 구조를 수정하면, When 승인하면, Then 승인된 구조로만 다음 단계를 진행한다.

---

## Epic 2 — Asset Retrieval (Multi-Source, mock)
*목적: 구조화된 Intent로 자산 후보를 찾고, **권한 필터로 접근 불가 자산을 먼저 제외한 뒤** 재검증 대상 상위 N개를 선별한다.*
*순서: 검색(US-2.1) → Permission Filter + Top-N 선별(US-2.2) → (Epic 3 재검증).*

### US-2.1 Multi-Source 자산 검색 **[MVP]** · Hero
- **As a** 사용자, **I want** 구조화된 Intent로 여러 Source(GitHub/Confluence/Jira/IMS/BizForce/EDM 대표 mock)를 검색해 후보 자산을 찾고 싶다, **so that** 흩어진 자산을 한 번에 확인한다.
- **AC**
  - Given 승인된 구조화 Intent, When 검색을 수행하면, Then 여러 Source의 mock 자산에서 관련 후보 **전체 목록**을 반환한다.
  - Given 각 후보, Then Source·자산 식별자·요약이 함께 유지된다.
- **Example (mock)**: 후보 예 — GitHub `forecast-gap-lib`, Confluence `고객대시보드 표준 가이드`, BizForce `Sales Forecast 리포트 템플릿`.

### US-2.2 권한 필터 후 Top-N 선별 (Permission Filter → Top-N) **[MVP]** · Hero · Unhappy
- **As a** 사용자, **I want** 접근 권한이 없는 자산을 **재검증 전에** 먼저 제외하고, 접근 가능한 후보 중에서만 상위 N개를 재검증 대상으로 선별하길 원한다, **so that** 볼 수 없는 자산에 재검증/추천 비용을 쓰지 않고 잘못 추천받지도 않는다. (FR-8, discovery §5.3)
- **AC**
  - Given US-2.1의 후보 전체 목록 + mock permission context(Role + 자산별 접근 권한), When 결과를 구성하면, Then 사용자가 접근 불가한 자산과 그 Evidence를 **LLM 재검증 이전에** 제외한다.
  - Given 접근 가능한 후보들, When 선별하면, Then 상위 N개(기본 3~5)만 재검증 대상으로 다음 단계(Epic 3)로 넘긴다.
  - Given 접근 가능 자산이 하나도 없으면, Then 접근 가능한 후보가 없음을 명시한다(권한 확장하지 않으며, Overall Decision은 US-3.4의 DEVELOP로 이어진다).
- **최소 구현**: 접근 불가 자산이 재검증 전에 제외되는 것을 검증하는 대표 mock/test case 1개.

---

## Epic 3 — Reusability Re-verification & Decision
*목적: 유사도가 아니라 실제 재사용 가능성을 Role/Task 맥락에서 판단한다.*

> **Decision 적용 단위 (명확화)**
> - **Candidate State (후보별)**: 각 후보 자산에 부여 — `REUSE` / `EXTEND EXISTING` / `NEEDS REVIEW`. (후보 단위에는 DEVELOP 없음)
> - **Overall Decision (요청 전체)**: 요청 하나에 대한 최종 권고 — `REUSE` / `EXTEND EXISTING` / `NEEDS REVIEW` / `DEVELOP`.
>   - 접근 가능 후보 중 적합한(REUSE/EXTEND 가능한) 후보가 **하나도 없을 때만** Overall = `DEVELOP`.

### US-3.1 상위 후보 LLM 재사용성 재검증 **[MVP]** · Hero
- **As a** 사용자, **I want** 상위 후보를 내 Role/Task 맥락으로 재검증받고 싶다, **so that** "단순 유사 ≠ 실제 재사용 가능"을 걸러낸다. (FR-4, discovery §4)
- **AC**
  - Given 상위 N개 후보 + 구조화 Intent, When LLM 재검증을 수행하면, Then 각 후보에 Reusability Score와 판단 근거를 부여한다.
  - Given 재검증 결과, Then Role/Task 맥락 반영 여부가 근거에 드러난다.
- **Example (mock)**: `forecast-gap-lib`는 Data Source가 일치해 높은 Score, `고객대시보드 가이드`는 문서라 부분 참고로 낮은 Score.

### US-3.2 후보별 Candidate State 분류 **[MVP]** · Hero
- **As a** 사용자, **I want** 각 후보가 REUSE / EXTEND EXISTING / NEEDS REVIEW 중 하나로 분류되길 원한다, **so that** 후보별 다음 행동을 바로 정한다. (FR-5)
- **AC**
  - Given 재검증된 각 후보, When 분류하면, Then 해당 후보에 **Candidate State 3개(REUSE / EXTEND EXISTING / NEEDS REVIEW)** 중 하나를 부여한다. (후보 단위에는 DEVELOP 없음)
  - Given 분류 결과, Then 각 Candidate State 부여 근거가 Evidence와 연결된다.
- **Example (mock)**: `forecast-gap-lib` → EXTEND EXISTING, `Forecast 리포트 템플릿` → REUSE.

### US-3.3 근거 부족 시 Candidate State = NEEDS REVIEW **[MVP]** · Unhappy
- **As a** 사용자, **I want** 후보의 Evidence가 부족하거나 상충할 때 AI가 억지 결론(REUSE/EXTEND) 대신 해당 후보를 NEEDS REVIEW로 표시하길 원한다, **so that** 잘못된 자동 판단을 신뢰하지 않는다.
- **AC**
  - Given 특정 후보의 Evidence가 불충분/상충, When 분류하면, Then 그 후보의 Candidate State를 NEEDS REVIEW로 표시하고 부족한 근거를 명시한다. (후보 단위 판단이며 Overall Decision과 별개)
- **최소 구현**: NEEDS REVIEW Candidate State를 유발하는 대표 mock/test case 1개.

### US-3.4 적합 후보 없음 → Overall Decision = DEVELOP 권고 **[MVP]** · Unhappy
- **As a** 사용자, **I want** 접근 가능한 후보 중 재사용/확장 가능한 적합 자산이 하나도 없을 때 **요청 전체에 대한 Overall Decision으로** 신규 개발(DEVELOP)을 권고받고 싶다, **so that** 없는 자산을 억지로 재사용하지 않는다.
- **AC**
  - Given 접근 가능 후보 중 Candidate State가 REUSE 또는 EXTEND EXISTING인 후보가 하나도 없으면, When Overall Decision을 산출하면, Then Overall = DEVELOP를 제시하고 그 이유를 밝힌다.
  - Given 적합 후보가 하나 이상 있으면, Then Overall Decision은 후보 결과를 종합한 REUSE / EXTEND EXISTING / NEEDS REVIEW 중 하나로 산출된다(DEVELOP 아님).
- **최소 구현**: 적합 후보 부재로 Overall = DEVELOP가 산출되는 대표 mock/test case 1개.

---

## Epic 4 — Results, Comparison & Evidence
*목적: 판단 결과를 근거와 함께 한 화면에서 비교·전달한다.*

### US-4.1 후보 랭킹 결과 화면 **[MVP]** · Hero
- **As a** 사용자, **I want** 후보 자산을 랭킹으로 비교(Source·Reusability Score·후보별 Candidate State)하고, 요청 전체 Overall Decision도 함께 보고 싶다, **so that** 최적 선택을 빠르게 한다. (FR-6, FR-10)
- **AC**
  - Given 분류된 후보들, When 결과 화면을 열면, Then **Candidate State 우선순위(REUSE > EXTEND EXISTING > NEEDS REVIEW) → Score 내림차순 → 자산명** 순 랭킹으로 Source·자산명·Capability Match·Score·**Candidate State**를 한 화면에 표시한다. (Functional Design U1 Q6=C / Follow-up1=A 반영)
  - Given 결과 화면, Then 요청 전체에 대한 **Overall Decision**(REUSE/EXTEND EXISTING/NEEDS REVIEW/DEVELOP)을 랭킹과 함께 명확히 표시한다.
  - Given 결과 화면, Then Search→Compare→Decide 흐름이 시각적으로 드러난다.
- **Example (mock)**: Overall = EXTEND EXISTING. 1위 `Forecast 리포트 템플릿`(REUSE, 0.9), 2위 `forecast-gap-lib`(EXTEND EXISTING, 0.8), 3위 `고객대시보드 가이드`(NEEDS REVIEW, 0.4).

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

> **범위 명확화**: Role/Task Context를 Reusability 판단에 **반영하는 기능 자체는 MVP**에 이미 포함된다(US-1.2 구조화 시 Role, US-3.1 재검증 시 Role/Task 맥락 반영). 아래 US-5.1의 Later 범위는 "Role별 판단 여부"가 아니라, **실제 사용 데이터와 피드백을 기반으로 평가 항목의 가중치·추천 전략을 최적화**하는 것이다.

### US-5.1 Role/피드백 기반 가중치·추천 전략 최적화 **[Later]**
- **As a** 제품 운영자, **I want** 축적된 실제 사용 데이터와 사용자 피드백(US-4.3)을 기반으로 재사용 판단의 평가 항목 가중치와 추천 전략을 Role별로 최적화하고 싶다, **so that** Role별 재사용 판단 품질이 실사용 근거로 지속 개선된다. (discovery Persona Analysis)
- **전제**: Role/Task 반영 자체는 MVP(US-1.2, US-3.1)에서 이미 동작한다. 본 스토리는 그 위의 최적화 계층이다.
- **AC**
  - Given 누적된 사용 데이터·피드백, When 최적화를 수행하면, Then Role별로 평가 항목(예: Capability Fit, Compatibility, Freshness)의 가중치를 조정한다.
  - Given 조정된 가중치, When 이후 검색/재검증에 적용하면, Then 랭킹·Candidate State 산출에 반영되고 조정 근거가 기록된다.
  - Given 최적화 전/후, Then 추천 품질 변화를 비교할 수 있는 지표(예: 피드백 긍정률)를 제공한다.

### US-5.2 실제 Source & SSO 연동 **[Later]**
- **As a** 조직, **I want** mock을 실제 GitHub/Confluence/Jira/IMS/BizForce/EDM 및 AD SSO로 대체하고 싶다, **so that** 실제 권한·자산 기반으로 동작한다. (NFR-3, discovery §5.3)
- **AC**
  - Given 실제 Source 커넥터 설정, When 검색을 수행하면, Then mock 대신 실제 Source의 자산을 조회한다.
  - Given AD SSO 로그인 사용자, When 권한 필터(US-2.2)를 적용하면, Then mock permission context 대신 실제 SSO/권한 정보로 접근 가능 자산을 판별한다.
  - Given 실제 연동 전환, Then MVP의 재사용 판단 흐름(구조화→검색→권한 필터→재검증→Decision→Evidence)은 변경 없이 동일하게 동작한다.

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
