# Rebuild or Reuse Advisor

AI로 새로운 S/W를 만들기 전에 **기존 사내 자산을 재사용할 수 있는지 먼저 판단**하도록 돕는 해커톤 프로젝트입니다.

생성형 AI로 개발자뿐 아니라 다양한 직군이 Dashboard, 업무용 Tool, Script, Agent, Skill 등을 빠르게 만들 수 있게 되면서 S/W 개발의 진입장벽은 낮아졌습니다. 반면 이미 존재하는 사내 자산을 충분히 확인하지 않고 유사한 것을 다시 만드는 중복 개발도 더 쉽게 발생할 수 있습니다.

Rebuild or Reuse Advisor는 사용자의 **Role / Task Context**를 이해하고 관련 기존 자산을 탐색·비교하여, 바로 새로 만들기 전에 재사용 가능성을 검토하는 것을 목표로 합니다.

## 핵심 질문

> AI가 이것을 만들 수 있는가? 보다 먼저, 이것을 정말 새로 만들어야 하는가?

## Decision Model

- **REUSE** — 기존 자산을 그대로 활용
- **EXTEND EXISTING** — 기존 자산을 기반으로 필요한 부분을 수정·확장
- **DEVELOP** — 적절한 기존 자산이 없어 신규 개발
- **NEEDS REVIEW** — 자동 판단이 어려워 추가 검토 필요

## 기본 흐름

```text
Task 입력
  ↓
Role / Task Context 이해
  ↓
접근 가능한 사내 Source에서 Evidence 탐색
  ↓
Evidence를 Asset 단위로 결합
  ↓
현재 Task와 기존 Asset 비교
  ↓
Reusability 판단
  ↓
REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW
  ↓
재사용 / 수정·확장 / 신규 개발 범위와 근거 제시
```

단순히 유사한 자료나 S/W를 찾아주는 Retrieval/RAG에 그치지 않고, **검색된 자산이 현재 Task Context에서 실제로 재사용 가능한지 판단하는 것**을 핵심 문제로 봅니다.

## Target

초기 아이디어는 개발자 중심의 Build or Reuse에서 시작했지만, 생성형 AI로 S/W를 만드는 주체가 확대되고 있다는 점을 고려하여 다음과 같은 사용자를 함께 탐색합니다.

- Developer — 기능 / API / 서비스 개발, 개발 자동화 Tool·Agent·Skill 생성
- Sales / Business — Dashboard / 업무용 Tool 생성
- 기타 직군 — AI를 활용한 업무용 S/W / 자동화 Tool 생성

직군과 Task Context에 따라 탐색 대상과 Reusability 판단 기준이 달라질 수 있다는 가설을 AI-DLC Discovery 과정에서 검증합니다.

## AI-DLC 활용 방향

해커톤 전에 실제 업무의 Use Case / As-Is Happy Path / Unhappy Path 등 **업무 Context를 Evidence로 준비**하고, 요구사항과 MVP를 미리 확정하지 않습니다.

해커톤 당일에는 준비한 Discovery Input을 AI-DLC에 제공하여 다음 과정을 진행합니다.

```text
Evidence / Context
  ↓
AI-DLC Intent / Discovery
  ↓
User Need / Requirements
  ↓
Priority
  ↓
MVP 후보
  ↓
Human Gate
  ↓
Design / Build / Test / Evaluation
```

Problem / Solution / Target 및 Reusability 관련 사전 생각은 **Hypothesis**로 구분하며, 실제 Use Case Evidence를 기준으로 AI-DLC에서 검증·수정합니다.

## Enterprise Integration 방향

실제 사내 환경에서는 사용자를 SSO로 인증하고, 각 사내 시스템 및 개별 자산/페이지에 대한 **기존 접근 권한 범위 안에서만** 검색해야 합니다. Advisor는 사용자의 권한을 확장하지 않습니다.

해커톤에서는 실제 사내 시스템 대신 representative Mock 데이터를 사용하지만, 이후 실제 Source Adapter로 교체할 수 있도록 Source / Evidence / Asset을 분리합니다.

### Source → Evidence → Asset → Decision

```text
SSO User / Permission Context
            ↓
   Source Adapter Layer
            ↓
┌───────────┼───────────┬─────────┬──────────┬─────────┐
GitHub   Confluence    Jira      IMS      BizForce    EDM
└───────────┼───────────┴─────────┴──────────┴─────────┘
            ↓
      Normalized Evidence
            ↓
       Asset Aggregation
            ↓
          Asset
            ↓
   Rebuild or Reuse Advisor
            ↓
REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW
```

- **Source**: GitHub, Confluence, Jira, IMS, BizForce, EDM처럼 원본 정보가 존재하는 사내 시스템
- **Evidence**: 각 Source에서 확인된 기능, 설계, 이력, 운영 Risk, 고객/시장 Context 등의 근거
- **Asset**: Dashboard, API, Repository, Tool, Script, Agent, Skill 등 실제 재사용 판단 대상
- **Decision**: Task Context와 Asset/Evidence를 비교하여 Advisor가 도출하는 결과

Asset과 Evidence를 분리함으로써 하나의 Asset을 여러 Source의 근거로 판단할 수 있고, 해커톤의 Mock Source를 실제 사내 Adapter로 교체하더라도 Advisor의 판단 로직을 유지할 수 있도록 합니다.

## 해커톤 제약

- 주제: AI 기반 S/W 개발 생산성 향상
- AWS AI-DLC 사용
- 실제 개발 가능 시간: 약 1일
- 팀 Token Budget: USD 1,000
- 실제 사내 시스템 접근에는 제한이 있을 수 있음
- 실제 SSO / 권한 시스템 대신 Mock Identity / Permission Context 사용 가능
- 실제 Source 대신 representative Mock Enterprise Data 사용

## Repository 구조

```text
.
├── README.md
├── docs/
│   ├── aidlc/
│   │   ├── discovery-input.md       # AI-DLC Discovery 시작 입력
│   │   └── start-prompt.md          # AI-DLC 첫 실행 Prompt
│   └── integration/
│       ├── mock-enterprise-data.md  # Mock Enterprise Data 설계
│       └── asset-adapter-contract.md# Adapter / Asset / Evidence Contract 초안
└── mock/
    ├── users.json                   # Mock SSO user / permission context
    ├── assets.json                  # Normalized Asset 데이터
    └── evidence/
        ├── github.json
        ├── confluence.json
        ├── jira.json
        ├── ims.json
        ├── bizforce.json
        └── edm.json
```

구현 단계에서 `app/`, `tests/` 등 실제 Application 구조는 AI-DLC Design 결과에 따라 추가합니다.

## 현재 단계

해커톤 사전 준비 단계에서 다음을 완료했습니다.

- 실제 업무 Use Case / Happy Path 조사 및 통합
- AI-DLC Discovery Input 및 시작 Prompt 준비
- AI-DLC 로컬 실행 환경 확인
- SSO / Permission Constraint 정리
- Mock Identity / Permission Context 준비
- 12개 representative Asset 준비
- GitHub / Confluence / Jira / IMS / BizForce / EDM Mock Evidence 준비
- 실제 Source로 교체 가능한 Adapter Contract 초안 준비

Requirements, MVP, Architecture 및 실제 구현은 해커톤 당일 AI-DLC workflow와 Human Gate를 통해 결정합니다.
