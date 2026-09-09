# Rebuild or Reuse Advisor

> **Before asking AI to build it, ask whether it should be built at all.**

생성형 AI와 바이브 코딩의 발전으로 누구나 빠르게 소프트웨어를 만들 수 있는 시대가 되었습니다. 하지만 개발 비용이 낮아진 만큼, 이미 존재하는 사내 Dashboard, Tool, API, Script를 충분히 확인하지 않은 채 유사한 자산을 반복적으로 다시 만드는 비용도 함께 낮아지고 있습니다. 그 결과 조직 내에는 비슷한 기능의 코드와 프로그램이 무질서하게 늘어나고 있으며, 이는 개인과 회사 차원의 토큰 낭비, 개발 리소스 낭비, 유지보수 부담, 자산 관리 비용 증가로 이어질 수 있습니다. 따라서 코딩을 시작하기 전에 사내에 활용 가능한 기존 자산이 있는지 검색하고 검증한 뒤, 사용자의 요구사항에 따라 재사용, 결합 및 확장, 신규 개발, 추가 검토 중 어떤 방식이 가장 효율적인지 판단해주는 서비스가 필요합니다.

**Rebuild or Reuse Advisor**는 새로운 S/W를 만들기 전에 사용자의 **Task Context와 접근 권한**을 기반으로 기존 사내 자산을 탐색하고, 여러 Source의 Evidence를 종합해 다음 행동을 추천하는 AI 기반 의사결정 도구입니다.

- **REUSE** — 기존 자산을 그대로 활용
- **EXTEND EXISTING** — 기존 자산을 기반으로 수정·확장
- **DEVELOP** — 적절한 기존 자산이 없어 신규 개발
- **NEEDS REVIEW** — 근거가 부족하거나 자동 판단이 어려워 추가 검토 필요

## Why this matters

AI Coding은 **“어떻게 더 빨리 만들 것인가?”**를 크게 개선했습니다. 하지만 개발을 시작하기 전에는 또 다른 질문이 필요합니다.

> **AI가 이것을 만들 수 있는가? 보다 먼저, 이것을 정말 새로 만들어야 하는가?**

기존 자산 탐색이 개인의 경험과 수동 검색에 의존하면 중복 개발이 발생하고, GitHub·Confluence·Jira 등 여러 Source에 흩어진 근거를 함께 판단하기 어렵습니다.

일반적인 Enterprise Search가 **“무엇이 존재하는가?”**에 답한다면, Rebuild or Reuse Advisor는 한 단계 더 나아가 **“현재 Task에서 기존 자산을 실제로 어떻게 활용해야 하는가?”**에 답합니다.

**Search → Decision**이 이 프로젝트의 핵심 차별점입니다.

## How it works

```text
Natural-language Task
        │
        ▼
1. Intent Structuring
   Role / Goal / Functions / Data / Output
        │
        ▼
2. Multi-Source Asset Search
        │
        ▼
3. Permission Filter
   unauthorized assets are removed
        │
        ▼
4. Top-N Candidate Selection
        │
        ▼
5. LLM Re-verification
        │
        ▼
6. Deterministic Decision Classification
        │
        ▼
7. Evidence Chain
        │
        ▼
REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW
```

### Permission before LLM

접근 권한이 없는 Asset은 UI에서만 숨기는 것이 아니라 **LLM 재검증 전에 후보에서 제거**됩니다. 공개 API 응답에도 내부 권한 정보나 제외된 Asset 정보가 포함되지 않도록 계약을 분리했습니다.

### Evidence Chain

하나의 재사용 대상인 **Asset**과 판단 근거인 **Evidence**를 분리했습니다.

```text
GitHub ───────┐
Confluence ───┤
Jira ─────────┤
IMS ──────────┼─> Evidence ─> Asset ─> Recommendation
BizForce ─────┤
EDM ──────────┘
```

현재 MVP는 6개 Mock Source Adapter를 사용하지만, 공통 `SourceAdapter` + Registry 구조로 실제 Enterprise Source 연결을 격리했습니다.

## Demo

기본 실행은 **Demo Mode**입니다. 실제 AWS 호출 없이 결정적 Fixture를 사용하므로 심사와 Demo Media에서 동일한 결과를 안정적으로 재현할 수 있습니다.

### Hero Scenario

**Role: Sales**

> 고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요.

Advisor는 요청을 구조화하고 → 기존 자산을 탐색하고 → 권한을 검사하고 → 후보를 재검증한 뒤 **Overall Decision: REUSE**와 함께 후보 랭킹 및 Evidence Chain을 제공합니다.

그 외에도 `NEEDS REVIEW`, `DEVELOP`, 정보 부족 시 `Clarification` 시나리오를 재현할 수 있습니다.

## Product UI

React 기반 단일 화면에서 전체 판단 흐름을 확인할 수 있습니다.

```text
┌─────────────────────┬────────────────────────┬─────────────────────┐
│ Request & Intent    │ Ranking & Decision     │ Evidence Chain      │
│ Natural language   │ Overall Decision       │ Why this decision?  │
│ Structured Intent  │ Ranked Candidates      │ Source Evidence     │
└─────────────────────┴────────────────────────┴─────────────────────┘
```

사용자는 자연어 요청을 입력한 뒤 구조화된 Intent를 확인하고, 후보 랭킹·재사용성 판단·근거를 한 화면에서 검토할 수 있습니다.

## Architecture

```text
[React Web UI]
      │
      ▼
[Advisor Orchestrator]
      │
      ├─ Intent Structuring
      ├─ Asset Search ── SourceAdapter Registry ── 6 Mock Sources
      ├─ Permission Filter
      ├─ Candidate Selection
      ├─ LLM Re-verification
      ├─ Decision Classifier (deterministic / pure)
      └─ Evidence Builder
      │
      ▼
[Advice Result + Feedback]
```

### Key design decisions

- **LLM과 Decision Logic 분리** — LLM은 후보를 재검증하고, 최종 State 판정은 deterministic classifier가 수행합니다.
- **Permission-before-LLM** — 미인가 Asset이 LLM Context와 공개 결과에 들어가지 않습니다.
- **Source Adapter 확장 구조** — Mock Source를 실제 Enterprise API로 교체해도 Advisor 핵심 파이프라인을 유지합니다.
- **Asset / Evidence 분리** — 하나의 Asset을 여러 Source의 근거로 판단할 수 있습니다.

## AWS / LLM Integration

두 가지 실행 모드를 지원합니다.

### Demo Mode — default

```text
DEMO_MODE=true
```

- 결정적 Fixture 사용
- AWS Credential 불필요
- Hero / Unhappy Path 재현 가능

### LLM Mode

```text
DEMO_MODE=false
```

- Amazon Bedrock의 Claude 모델 사용
- Intent Structuring / Re-verification 수행
- Demo Fixture fallback 없이 실제 LLM 결과 사용

판단 전체를 LLM에 맡기지 않고 **LLM reasoning + deterministic decision rules**로 구성했습니다.

## Built with AWS AI-DLC

이 프로젝트는 AWS AI-DLC를 실제 개발 Lifecycle로 사용했습니다. 사전에 준비한 업무 Evidence를 [`docs/aidlc/discovery-input.md`](docs/aidlc/discovery-input.md)에 입력하고, Requirements와 Architecture를 미리 확정하지 않은 상태에서 Inception → Construction → Build & Test를 진행했습니다.

```text
Discovery Input
   ↓
Requirements / Personas / User Stories
   ↓
Application Design / Units Generation
   ↓
Functional & NFR Design
   ↓
Code Generation
   ↓
Build & Test
```

| AI-DLC Stage / Evidence | Repository |
|---|---|
| Discovery Input | [`docs/aidlc/discovery-input.md`](docs/aidlc/discovery-input.md) |
| Requirements | [`aidlc-docs/inception/requirements/`](aidlc-docs/inception/requirements/) |
| Personas / Stories | [`aidlc-docs/inception/user-stories/`](aidlc-docs/inception/user-stories/) |
| Application Design | [`aidlc-docs/inception/application-design/`](aidlc-docs/inception/application-design/) |
| Construction Design | [`aidlc-docs/construction/u1-advisor-backend/`](aidlc-docs/construction/u1-advisor-backend/) |
| Build & Test | [`aidlc-docs/construction/build-and-test/`](aidlc-docs/construction/build-and-test/) |
| Lifecycle State | [`aidlc-docs/aidlc-state.md`](aidlc-docs/aidlc-state.md) |
| Decision / Interaction Audit | [`aidlc-docs/audit.md`](aidlc-docs/audit.md) |

Repository에서 **Evidence → Requirement → Story → Architecture → Implementation → Test**의 흐름을 추적할 수 있습니다.

## Validation

현재 `main` 기준:

- **Backend:** 44 / 44 tests passed, **92% coverage**
- **Property-Based Testing:** Decision Classifier 핵심 불변식 검증
- **Frontend:** TypeScript `strict` 오류 0, Vite production build 성공
- **Integration:** U1 pipeline 자동화 시나리오 4 / 4 통과
- **Security-related behavior:** permission filtering 및 unauthorized-data non-disclosure 검증

상세 결과: [`aidlc-docs/construction/build-and-test/build-and-test-summary.md`](aidlc-docs/construction/build-and-test/build-and-test-summary.md)

## Quick Start

### Requirements

- Python 3.11+
- Node.js 18+
- npm

### 1. Backend

```bash
cd advisor-backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

기본 Demo Mode에서는 AWS Credential이 필요하지 않습니다. OpenAPI는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. Vite 개발 서버가 `/intent`, `/advise`, `/feedback` 요청을 Backend로 proxy합니다.

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic, boto3, Amazon Bedrock
- **Frontend:** React 18, TypeScript, Vite
- **Test:** pytest, Hypothesis
- **Development Lifecycle:** AWS AI-DLC

## Repository Structure

```text
.
├── advisor-backend/        # U1 — FastAPI Advisor backend + tests
├── frontend/               # U2 — React single-screen Web UI
├── docs/                   # Discovery input + integration contracts
├── aidlc-docs/             # AI-DLC Inception / Construction / audit trail
└── mock/                   # Representative enterprise mock data
```

## Hackathon Scope

MVP에서는 실제 사내 시스템과 SSO 대신 representative Mock Enterprise Data와 Permission Context를 사용합니다. 실제 환경에서는 **Source Adapter, Identity Context, Bedrock 실행 환경**을 연결하는 방식으로 확장하도록 설계했습니다.

---

> **AI가 이것을 만들 수 있는가? 보다 먼저, 이것을 정말 새로 만들어야 하는가?**
