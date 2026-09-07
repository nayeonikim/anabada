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
기존 사내 S/W / 자산 탐색
  ↓
현재 Task와 기존 자산 비교
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

## 해커톤 제약

- 주제: AI 기반 S/W 개발 생산성 향상
- AWS AI-DLC 사용
- 실제 개발 가능 시간: 약 1일
- 팀 Token Budget: USD 1,000
- 실제 사내 시스템 접근에는 제한이 있을 수 있음
- 필요 시 representative / mock enterprise data 사용

## Repository 구조

```text
.
├── README.md
├── app/                  # MVP application code
├── docs/
│   ├── use-cases/        # Role / Use Case / Happy Path 원자료
│   ├── aidlc/            # AI-DLC Discovery Input 및 산출물
│   └── presentation/     # Demo / 발표 자료
├── scripts/              # Utility scripts
└── tests/                # Tests
```

## 현재 단계

현재는 팀에서 수집한 실제 업무 Use Case와 Happy Path를 정리하여 **AI-DLC Discovery Input을 준비하는 단계**입니다. 이후 요구사항 도출, 우선순위화, MVP 결정은 해커톤 당일 AI-DLC workflow와 Human Gate를 통해 진행할 예정입니다.
