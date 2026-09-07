# Enterprise Asset Adapter Contract — Draft

## 목적

Rebuild or Reuse Advisor가 해커톤에서는 Mock 데이터를 사용하고, 이후에는 GitHub / Wiki / Jira / IMS / BizForce / EDM 등 실제 사내 Source로 교체할 수 있도록 공통 Integration 경계를 정의한다.

이 문서는 확정 Architecture가 아니라 AI-DLC Design 단계에 제공할 사전 Integration Constraint / Contract 초안이다.

## 핵심 원칙

1. **Authentication과 Authorization을 분리한다.**
   - 사용자는 사내 SSO로 인증된다고 가정한다.
   - Advisor는 기존 Source의 권한을 확장하지 않는다.
   - 검색과 Evidence 조회는 현재 사용자가 접근 가능한 범위에서만 수행한다.

2. **Source와 Asset을 분리한다.**
   - Source는 GitHub, Wiki, Jira, IMS, BizForce, EDM 같은 정보 시스템이다.
   - Asset은 Dashboard, API, Repository, Tool, Script, Agent, Skill 등 재사용 판단 대상이다.

3. **Retrieval과 Reuse Decision을 분리한다.**
   - Adapter는 후보 Asset / Evidence를 반환한다.
   - REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW 판단은 Advisor가 수행한다.
   - Adapter 결과에 `decision`, `reuse_score` 같은 최종 판단값을 포함하지 않는다.

4. **Source별 데이터를 공통 Evidence 모델로 Normalize한다.**
   - Source마다 원본 Schema는 달라도 Advisor에는 동일한 형태의 Evidence로 제공한다.

---

## 1. Identity Context

```text
IdentityContext
- user_id: string
- role: string
- department: string | null
- permissions: SourcePermission[]
```

### SourcePermission

```text
SourcePermission
- source_type: github | wiki | jira | ims | bizforce | edm
- access: allowed | denied
- scopes: string[]
```

`scopes`는 Source 전체 권한이 아니라 repository, project, space, page group 등 사용자가 실제 접근할 수 있는 범위를 표현하기 위한 값이다.

해커톤에서는 Mock permission을 사용하며, 실제 환경에서는 SSO 및 각 Source의 권한 정보로 대체한다.

---

## 2. Asset Model

```text
Asset
- id: string
- name: string
- type: dashboard | api | repository | tool | library | script | agent | skill | workflow | capability
- description: string
- capabilities: string[]
- lifecycle_status: active | experimental | deprecated | unknown
- owner: string | null
- last_updated: date | null
- interfaces: string[]
- constraints: string[]
- evidence_refs: string[]
```

Asset에는 판단 결과를 저장하지 않는다.

---

## 3. Evidence Model

```text
Evidence
- id: string
- asset_id: string
- source_type: github | wiki | jira | ims | bizforce | edm
- source_ref: string
- evidence_type: string
- title: string
- summary: string
- last_updated: date | null
- access_scope: string | null
- metadata: object
```

### Source별 대표 evidence_type

| Source | 대표 Evidence Type |
|---|---|
| github | repository, implementation, script, package, release |
| wiki | architecture, design, api_guide, usage_guide, operation_guide |
| jira | requirement, feature_history, known_limitation, issue |
| ims | incident, known_problem, operation_risk |
| bizforce | customer_context, project, forecast, opportunity, data_source |
| edm | report, proposal, market_analysis, product_document, reference_document |

---

## 4. Search Query

```text
AssetSearchQuery
- user_context: IdentityContext
- task: string
- role: string | null
- desired_capabilities: string[]
- preferred_asset_types: string[]
- constraints: string[]
```

`role`은 검색 및 판단 Context이며 권한 자체를 의미하지 않는다. 실제 Source 접근 여부는 `IdentityContext.permissions`로 결정한다.

---

## 5. Adapter Interface

개념적으로 Source Adapter는 다음 동작을 제공한다.

```text
SourceAdapter
- search(query, identity_context) -> Evidence[]
- get_evidence(evidence_id, identity_context) -> Evidence
- health() -> SourceStatus
```

그리고 Evidence를 Asset 단위로 결합하는 계층을 별도로 둔다.

```text
Evidence[]
   ↓
Asset Aggregation
   ↓
Asset[] + Evidence[]
   ↓
Rebuild or Reuse Advisor
   ↓
REUSE / EXTEND EXISTING / DEVELOP / NEEDS REVIEW
```

해커톤에서는 `MockSourceAdapter`가 JSON 데이터를 반환하도록 구현할 수 있고, 실제 환경에서는 Source별 Adapter로 교체한다.

---

## 6. Representative Source Mapping

```text
MockGitHubAdapter   -> Future GitHub Adapter
MockWikiAdapter     -> Future Wiki/Confluence Adapter
MockJiraAdapter     -> Future Jira Adapter
MockIMSAdapter      -> Future IMS Adapter
MockBizForceAdapter -> Future BizForce Adapter
MockEDMAdapter      -> Future EDM Adapter
```

구체적인 REST Endpoint, 인증 프로토콜, class hierarchy, scoring algorithm은 이 문서에서 확정하지 않고 AI-DLC Design 단계에서 결정한다.
