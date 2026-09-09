# Integration Test Instructions — U1 Advisor Backend

## Purpose
U1 내부 컴포넌트 간 상호작용(파이프라인 전 구간)과 HTTP 계약을 통합 검증한다.
현재 구성된 유닛은 U1 하나이므로 "유닛 간(U1↔U2)" 통합은 U2 코드 생성 이후로 이연(pending).
대신 **엔드투엔드 파이프라인 통합**(API → S1 → C1~C8 → 공개 DTO)을 대상으로 한다.

> 유닛 간 통합(예정): U2 Web UI ↔ U1 `/intent`·`/advise`·`/feedback` HTTP 계약 검증(U2 생성 후 추가).

## Test Scenarios

### Scenario 1: API → Orchestrator → Components (Hero, REUSE)
- **Description**: `/intent`(구조화) → `/advise`(권고) 전 구간이 협력하여 REUSE 권고를 산출.
- **Setup**: `DEMO_MODE=true`(기본). 앱 기동 또는 `TestClient`.
- **Test Steps**:
  1. `POST /intent {rawText: "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"}`
  2. 응답 `status=structured`, `intent.role=Sales` 확인.
  3. `POST /advise {intent, context:{userId:"mock-sales-user", role:"Sales"}}`
- **Expected Results**: `overallDecision=REUSE`, `ranking[0].candidateId=asset-001`, `reusabilityScore=0.92`, `evidenceChains` 다중 Source 포함, 내부 필드 부재.
- **Cleanup**: 없음(in-memory/읽기 전용). feedback 테스트만 임시 파일 사용.

### Scenario 2: 부분 재검증 실패 → 강등 포함 정상 응답 (§1.4/§7.1)
- **Description**: 일부 후보 재검증 기술 실패 시 UNAVAILABLE로 강등되어 200 응답에 포함, 전체 실패 시에만 502.
- **Setup**: LLMClient에 "일부 실패" 스텁 주입(단위 레벨 `ReVerificationComponent`로 검증됨). API 레벨은 전체 실패(502) 계약 확인.
- **Test Steps**: 재검증이 전부 실패하도록 구성 → `/advise` 호출.
- **Expected Results**: `502 REVERIFICATION_UNAVAILABLE`, 응답 body `{error:{code,message,requestId}}`(내부 문자열 미포함).

### Scenario 3: 권한 필터 → DEVELOP (접근 가능 0)
- **Description**: 접근 불가로 후보 0 → DEVELOP 경로가 파이프라인 끝까지 일관.
- **Test Steps**: Sales role로 Developer 전용 자산만 매칭되는 요청(`release version checklist automation script`) `/advise`.
- **Expected Results**: `overallDecision=DEVELOP`, `ranking=[]`, HTTP 200.

### Scenario 4: demoMode 계약 (미매칭 → 명시적 오류)
- **Description**: demoMode ON에서 fixture 없는 입력은 폴백 없이 오류.
- **Test Steps**: `POST /intent {rawText:"데모에 없는 임의 요청"}`.
- **Expected Results**: `422 DEMO_FIXTURE_NOT_FOUND`.

## Setup Integration Test Environment

### 1. Start (옵션 A: 인프로세스 TestClient — 권장)
```bash
cd advisor-backend
pytest tests/unit/test_api.py -q      # TestClient 기반 통합(외부 서비스 불필요)
```

### 2. Start (옵션 B: 실제 서버)
```bash
cd advisor-backend
uvicorn app.main:app --port 8000
export API_URL=http://localhost:8000
```

## Run Integration Tests
```bash
# 인프로세스(권장): API 계약 + 파이프라인 통합
pytest tests/unit/test_api.py tests/unit/test_orchestrator.py -q

# 실제 서버(옵션 B) 수동 검증 예:
curl -s -X POST "$API_URL/intent" -H 'Content-Type: application/json' \
  -d '{"rawText":"대시보드 하나 만들어줘"}'
```

### Verify Service Interactions
- **Test Scenarios**: 위 Scenario 1~4.
- **Expected Results**: 각 시나리오 Expected 일치, 공개 응답에 내부/제외 정보 부재.
- **Logs Location**: stdout(구조화 JSON 라인). 감사 이벤트(`permission_excluded`, `reverify_*`, `advise_completed`)는 서버 로그에만.

### Cleanup
```bash
# 임시 feedback 파일 사용 시 삭제(테스트는 tmp_path 사용 → 자동 정리)
rm -f data/feedback.jsonl   # 실제 서버로 수동 테스트한 경우에만
```
