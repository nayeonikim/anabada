# Mock Enterprise Data Design

## 목적

해커톤 환경에서는 실제 사내 시스템에 직접 연결하기 어려울 수 있으므로, Rebuild or Reuse Advisor가 실제 사내 환경에서 동작하는 상황을 대표하는 Mock 데이터를 준비한다.

Mock은 단순 샘플 데이터가 아니라, 이후 실제 사내 시스템 Adapter로 교체할 수 있도록 다음을 표현하는 것을 목표로 한다.

- 여러 사내 Source에 분산된 Asset / Evidence
- 사용자별 접근 권한 차이
- 완성형 S/W뿐 아니라 API, Script, Agent, Skill 등 부분 Capability
- Active / Deprecated / Unknown 등 자산 상태 차이
- 검색 유사도와 실제 Reusability가 다를 수 있는 상황

## 대표 Enterprise Sources

| Source | 대표 정보 |
|---|---|
| `github` | Repository, Code, Script, Library, Agent 구현 |
| `confluence` | Architecture, Design, API Guide, Usage Guide, 운영 문서 |
| `jira` | Requirement, Feature, Issue, 개발 이력, Known Limitation |
| `ims` | Incident, 장애 이력, 운영 Risk, Known Problem |
| `bizforce` | Customer, Project, Forecast, Opportunity, 영업 Context |
| `edm` | 사내 문서, 보고서, 제안서, 시장/제품 분석 자료 |

> Wiki / Confluence 계열 사내 문서 Source는 Mock에서 `confluence`로 통합한다.

## Identity / Permission Context

실제 환경에서는 SSO로 사용자를 인증하고, 각 Source의 기존 권한 범위 안에서만 검색해야 한다.

Mock에서는 SSO 자체를 구현하기보다 representative user와 permission context를 제공한다.

예시:

```json
[
  {
    "user_id": "mock-dev-user",
    "role": "Developer",
    "accessible_sources": ["github", "confluence", "jira", "ims"]
  },
  {
    "user_id": "mock-sales-user",
    "role": "Sales",
    "accessible_sources": ["confluence", "bizforce", "edm", "jira"]
  }
]
```

`role`은 Task Context로 활용할 수 있지만 실제 접근 제어는 Role만으로 결정하지 않는다. 같은 직군이라도 Source 또는 개별 자산/페이지 권한이 다를 수 있으므로, 향후에는 실제 사용자 권한 정보를 기준으로 filtering하는 구조를 고려한다.

## Asset과 Evidence 분리

### Asset

재사용 여부를 판단하려는 대상.

예:
- Dashboard
- Tool
- API
- Repository
- Library
- Script
- Agent
- Skill
- Workflow / Capability

### Evidence

Asset의 존재, 기능, 상태, 제약, 운영 이력 등을 설명하는 Source별 근거.

한 Asset은 여러 Source에 걸친 Evidence를 가질 수 있다.

```text
Customer 360 Dashboard
├─ BizForce: 고객/Forecast 데이터 연계 정보
├─ Confluence: 기능 및 사용 가이드
└─ Jira: Feature 추가 및 Known Limitation 이력
```

## Representative Mock Assets

| ID | Asset | Type | 대표 Use Case | Evidence Sources |
|---|---|---|---|---|
| asset-001 | Customer 360 Dashboard | Dashboard | SALES-01 | bizforce, confluence, jira |
| asset-002 | Forecast Insight Dashboard | Dashboard | SALES-01 | bizforce, github, confluence |
| asset-003 | Customer Risk API | API | SALES-01 | github, confluence, ims |
| asset-004 | Customer Request Tracker | Tool | SALES-01 | bizforce, jira, confluence |
| asset-005 | Similar Code Finder | Tool | DEV-01 | github, confluence, jira |
| asset-006 | Issue & PR Knowledge Agent | Agent | DEV-01 | github, jira, confluence |
| asset-007 | Legacy Feature Helper | Library | DEV-01 | github, confluence, ims |
| asset-008 | Dev Workflow Automation Skill | Skill | DEV-02 | github, confluence, jira |
| asset-009 | Release Task Script | Script | DEV-02 | github, confluence, ims |
| asset-010 | News Monitoring Agent | Agent | SALES-06 | github, confluence, edm |
| asset-011 | IR Document Analyzer | Skill | SALES-06 | github, edm, confluence |
| asset-012 | Market Consensus Analyzer | Tool | SALES-06 | edm, bizforce, confluence |

## Mock Data가 표현해야 할 판단 차이

Mock Asset에는 `decision`, `reuse_score`, `similarity_score` 같은 최종 판단값을 넣지 않는다. 이는 Advisor가 Task Context와 Evidence를 비교하여 도출해야 하는 결과다.

대신 다음과 같은 사실을 데이터에 포함해 판단 차이가 발생하도록 한다.

- 기능 Coverage
- Lifecycle status: active / experimental / deprecated / unknown
- Owner 존재 여부
- Last updated
- Interface / Integration 방식
- Known constraints
- Jira의 Known Limitation
- IMS의 장애/운영 Risk
- BizForce/EDM 등 Source별 Context
- 사용자 접근 권한

예를 들어 `Legacy Feature Helper`는 기능적으로는 유사하지만 deprecated 상태이고 Owner가 불명확하며 IMS에 호환성 문제가 존재하도록 구성하여, 단순 유사 검색과 실제 재사용 판단의 차이를 보여줄 수 있다.

## Mock 구조 초안

```text
mock/
├── users.json          # Mock SSO user / permission context
├── assets.json         # Normalized Asset 정보
└── evidence/
    ├── github.json
    ├── confluence.json
    ├── jira.json
    ├── ims.json
    ├── bizforce.json
    └── edm.json
```

해커톤 구현 시 실제 디렉터리/파일 구조는 AI-DLC Design 단계에서 조정할 수 있다. 이 문서는 실제 Enterprise Source와 권한 제약을 표현하기 위한 사전 Integration Context와 representative Mock 설계 초안이다.
