# Requirements Clarification Questions — Rebuild or Reuse Advisor

> 이 질문들은 `docs/aidlc/discovery-input.md`를 유일한 Evidence로 분석한 결과, MVP·요구사항·우선순위를 확정하기 위해 팀 결정이 필요한 지점들입니다.
> discovery-input.md가 "요구사항·MVP는 AI-DLC 과정에서 도출한다"고 명시했으므로, 아래 답변으로 그 도출을 진행합니다.
> 각 질문의 `[Answer]:` 뒤에 letter(A/B/C...)를 채워주세요. 맞는 항목이 없으면 마지막 옵션(Other)을 고르고 설명을 적어주세요.

---

## Question 1
6시간(MVP 4시간 + 리뷰 2시간) 제약 하에서, **Demo/Hero Scenario**를 어느 흐름 중심으로 좁힐까요? (discovery-input.md는 Persona 우선순위가 아니라 데모 범위 좁히기 목적이라면 허용한다고 명시)

A) Developer 중심 — DEV-01 (기존 프로젝트 기능 개발/개선 시 자산 탐색·재사용 판단)

B) Developer 중심 — DEV-02 (Tool/Script/Agent/Skill 생성 시 재사용 판단)

C) Business User 중심 — SALES-01(Dashboard) 또는 SALES-05(반복업무 자동화)

D) 두 Persona 공통 Reusability 흐름 하나로 — Persona 무관 단일 데모(입력→탐색→Decision State)

X) Other (please describe after [Answer]: tag below)

[Answer]: D - 이 서비스는 직군과 무관하게 개발 전에 재사용 여부를 판단하는 목적입니다. 공통 시나리오로 1차 달성 후 추가 여유가 있을 경우 확장한다.  

## Question 2
사용자가 "만들려는 S/W(의도)"를 시스템에 입력하는 방식은?

A) 자연어로 만들고 싶은 것 설명 (예: "고객 Forecast Gap을 분석하는 대시보드")

B) 구조화된 폼 입력 (제목/목적/입력·출력/주요 기능)

C) 자연어 + 선택적 구조화 필드 (하이브리드)

X) Other (please describe after [Answer]: tag below)

[Answer]: C - 사용자는 자연어로 시작하되, AI가 Role·Goal·Function·Data·Output 등으로 구조화한다. 사용자의 의도를 파악하기 어려운 경우 추가 질문한 후 사용자의 승인을 받는다.

## Question 3
MVP에서 탐색 대상으로 다룰 **자산 Source 범위**는? (discovery-input.md 기준: GitHub / Confluence / Jira / IMS / BizForce / EDM)

A) GitHub + Confluence 2개 Source 중심

B) GitHub 단일 Source 중심

C) 전체 Source(GitHub/Confluence/Jira/IMS/BizForce/EDM) — representative mock data 기반

D) Source 범위는 Workflow Planning 단계에서 다시 결정

X) Other (please describe after [Answer]: tag below)

[Answer]: C -최종 서비스는 Multi-Source 탐색을 지향한다. MVP에서는 GitHub·Confluence·Jira·IMS·BizForce·EDM을 대표하는 Mock Asset을 사용하여 구조와 확장 가능성을 검증한다. 사용자별 source에 대한 권한여부가 다를 수 있으므로 해당 사항은 이후 workflow planning 단계에서 다시 결정한다.

## Question 4
Reusability 판단 방식은? (discovery-input.md의 "단순 유사도 ≠ 실제 재사용성" 가설 반영)

A) 검색 유사도 + LLM 기반 Context 판단(Role/Task 반영) 결합

B) 검색으로 후보 선별 후 상위 N개만 LLM으로 재사용성 재검증

C) 전적으로 LLM 판단 (검색 랭킹 미사용)

X) Other (please describe after [Answer]: tag below)

[Answer]: X : Question 2의 답변에서 작성한 사용자가 만들고자 하는 S/W에 의도를 파악하였으므로 이를 기반으로 검색하여 후보 선별 후 상위 n개만 LLM으로 재사용성을 재검증한다.이후 사용자에게 상위 n개 표시에 대한 피드백을 받는다. 사용자 피드백을 통해 선별 방식을 고도화해나간다.

## Question 5
판단 결과 **출력 형태**는? (Decision State 4종: REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW은 확정값)

A) 단일 최적 추천 + Decision State + 근거

B) 복수 후보 자산 랭킹 + 후보별 Decision State + Evidence(Source·링크·근거)

C) Decision State 판정만 (후보 목록 없이)

X) Other (please describe after [Answer]: tag below)

[Answer]: B "REUSE입니다”만 보여주는 것보다 N개의 후보 랭킹 비교 → Decision → Evidence가 서비스 가치를 훨씬 명확하게 보여줌. NEEDS REVIEW도 자연스럽게 표현 가능.각 후보에는 Source, Asset Link, Capability Match, 판단 근거 등을 표시하여 "왜 REUSE인지", "왜 EXTEND EXISTING인지"를 추적할 수 있도록 한다. 이는 서비스의 신뢰성과 자기설명성을 높이고 Evidence chain 평가에도 유리하다.

## Question 6
MVP에서 **권한/SSO** 처리 수준은? (discovery-input.md: 사용자의 기존 접근 권한을 확장하지 않고 존중해야 함)

A) representative mock user / permission context 사용 — Role·자산 권한에 따라 검색 결과 필터 (discovery 제안대로)

B) mock SSO 로그인 화면 + Role 기반 필터까지 구현

C) 권한 개념 없이 모든 자산 검색 허용 (MVP 단순화)

X) Other (please describe after [Answer]: tag below)

[Answer]: A. MVP에서는 mock user 기반으로 하되, 최종적으로는 삼성전자 DS 전체 AD SSO 입니다.  SSO 화면 자체는 MVP에서 구현하려는 서비스 핵심이 아닙니다.

## Question 7
사용자 인터페이스 형태는?

A) 웹 애플리케이션 (검색 입력 + 결과/근거 화면)

B) Chat 기반 대화형 인터페이스

C) CLI / 스크립트

X) Other (please describe after [Answer]: tag below)

[Answer]: A + B 우 웹 애플리케이션 형태로 구현한다. 자연어 Intent 입력 영역과 함께 검색된 Asset Ranking, Decision State, Reusability Score, Evidence 등을 한 화면에서 시각적으로 비교할 수 있도록 한다. 본 서비스의 핵심은 단순 Q&A가 아니라 Search → Compare → Decide → Evidence이므로 Chat UI보다 웹 기반 결과 화면이 서비스의 가치와 판단 과정을 직관적으로 전달하기에 적합하다.

## Question 8
평가 기준(산출물 자기설명성, Evidence chain)을 고려한 **Evidence 노출 수준**은?

A) 각 추천마다 Source·자산 링크·판단 근거를 명시적으로 제공 (추적 가능한 Evidence chain)

B) 핵심 근거 요약만 제공

X) Other (please describe after [Answer]: tag below)

[Answer]: A 각 추천 결과마다 Source, Asset 이름/링크, 관련 Evidence, 판단 근거를 명시적으로 제공한다. 사용자가 AI의 판단을 그대로 신뢰해야 하는 Black-box 형태를 피하고 어떤 Evidence를 기반으로 Decision State가 결정되었는지 추적 가능하게 만든다. 

---

# Extension Opt-In Questions

> 아래는 AI-DLC 확장 규칙 적용 여부입니다. 프로젝트 성격(해커톤 MVP vs 프로덕션)에 맞게 선택해주세요.

## Question 9: Security Extensions
이 프로젝트에 Security 확장 규칙을 강제할까요?

A) Yes — 모든 SECURITY 규칙을 blocking 제약으로 강제 (프로덕션급 애플리케이션 권장)

B) No — SECURITY 규칙 전체 skip (PoC/프로토타입/실험 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]:  B  프로젝트는 6시간 내 구현하는 Hackathon PoC이므로 AI-DLC의 전체 SECURITY Extension을 blocking constraint로 적용하지 않는다. 다만 Security 개념 자체를 제외하는 것은 아니며, MVP 핵심 요구사항인 Asset Permission Filtering은 mock permission context를 통해 구현한다. Unauthorized asset exclusion 같은 핵심 보안 요구사항은 일반 requirement로 유지한다.

## Question 10: Resiliency Extensions
Resiliency Baseline(AWS Well-Architected 신뢰성 기둥 기반의 설계 시점 best practice)을 적용할까요?

A) Yes — resiliency baseline을 설계 지침으로 적용 (business-critical 워크로드 권장, 이후 검증·강화 필요한 첫 초안 개념)

B) No — resiliency baseline skip (빠른 반복이 중요한 PoC/프로토타입/실험 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]:  B 현재 단계는 Production workload가 아니라 Rebuild or Reuse Advisor의 핵심 가설을 검증하는 Hackathon MVP이므로 Resiliency Baseline은 적용하지 않는다. 장애 복구, Failover, Production-level Availability 등의 설계보다 Intent 입력, Asset Retrieval, Reusability 판단, Evidence 제공이라는 핵심 End-to-End Flow를 완성하는 것을 우선한다. 향후 Production 전환 단계에서 별도 적용하는 것이 적절하다.

## Question 11: Property-Based Testing Extension
Property-Based Testing(PBT) 규칙을 강제할까요?

A) Yes — 모든 PBT 규칙을 blocking 제약으로 강제 (비즈니스 로직/데이터 변환/직렬화/상태 컴포넌트가 있는 프로젝트 권장)

B) Partial — 순수 함수와 직렬화 round-trip에만 PBT 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

C) No — PBT 규칙 전체 skip (단순 CRUD, UI-only, 얇은 통합 계층에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: B 전체 PBT를 blocking constraint로 적용하지 않고 핵심 순수 로직에 한해 제한적으로 적용한다. 입력과 출력 관계가 명확한 로직을 대상으로 한다. 이를 통해 개발 시간을 과도하게 사용하지 않으면서도 핵심 판단 로직의 안정성과 AI-DLC 적용 Evidence를 확보할 수 있다.
