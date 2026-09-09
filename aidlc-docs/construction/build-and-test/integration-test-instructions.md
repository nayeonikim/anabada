# Integration Test Instructions — U1 Advisor Backend + U2 Web UI

## Purpose
두 층위의 통합을 검증한다:
- **Part A — U1 내부 파이프라인 통합**: API → S1 → C1~C8 → 공개 DTO (인프로세스 TestClient).
- **Part B — 유닛 간(U1↔U2) 계약 통합**: U2 Web UI가 U1의 `/intent`·`/advise`·`/feedback` HTTP 계약과 공개 DTO에 정확히 정합하는지(dev proxy 경유).

> U2는 U1 확정 3개 API에만 의존하므로, 계약 통합의 핵심은 **DTO 형태 일치 + demoMode 결정성**이다.

---

## Part A — U1 파이프라인 통합

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

---

## Part B — 유닛 간 계약 통합 (U2 Web UI ↔ U1)

### 환경 기동
```bash
# 터미널 1 — U1 백엔드 (demoMode ON = 결정적 fixture)
cd advisor-backend
# venv 활성화 후
export DEMO_MODE=true        # Windows(cmd): set DEMO_MODE=true / PowerShell: $env:DEMO_MODE="true"
uvicorn app.main:app --port 8000

# 터미널 2 — U2 프론트엔드 (dev proxy → :8000)
cd frontend
npm install                  # 최초 1회
npm run dev                  # http://localhost:5173
```
- Vite dev proxy가 `/intent`·`/advise`·`/feedback`를 `:8000`으로 전달 → **별도 백엔드 CORS 설정 불필요**.
- 백엔드 포트가 다르면 `VITE_BACKEND_URL=http://host:port npm run dev`.

### 계약 통합 시나리오 (dev proxy 경유, 4 데모 프리셋)
U2 `demo/presets.ts`의 rawText는 U1 `demo_fixtures.json` 키와 정확히 일치 → demoMode ON에서 결정적.

| # | 프리셋 | 흐름 | 기대 결과(계약) |
|---|---|---|---|
| B-1 | Hero (REUSE) | 프리셋 선택 → 구조화(`/intent`) → 자문(`/advise`) | Overall 배너=REUSE, rank1=asset-001, 재사용성 0.92, EvidencePanel에 다중 Source chain 렌더 |
| B-2 | NEEDS_REVIEW | 구조화 → 자문 | Overall=NEEDS_REVIEW; UNAVAILABLE 후보는 점수 대신 '평가 미완료' 표기(null) |
| B-3 | DEVELOP | Sales 권한 컨텍스트 → 자문 | Overall=DEVELOP, 후보 카드 0개(접근 가능 0) — 미인가 자산 UI 비노출 |
| B-4 | Clarify | 정보 부족 rawText → 구조화 | 명료화 질문/누락 필드 렌더 → 보완 재제출 |

### 계약 검증 포인트(핵심)
- **DTO 형태 일치**: `/intent`·`/advise` 응답 JSON이 U2 `types.ts` 미러와 정합(타입체크 + 실 응답 파싱 무오류).
- **Type-Enforced Non-Disclosure(§3.2)**: 공개 응답에 `technicalFailureReason`·`excluded*`·`allowedRoles/Users` 부재 → UI에도 미노출.
- **오류 모델 파싱**: 미매칭 입력 → `422 DEMO_FIXTURE_NOT_FOUND`가 `{error:{code,message,requestId}}`로 반환되고, `client.ts`의 `ApiError`가 파싱하여 사용자 메시지로 표시.
- **피드백 왕복**: 후보 선택 → `POST /feedback` → 확인 id 표시.

> 실제 브라우저 시각 검증(스크린샷/렌더 확인)은 `e2e-test-instructions.md` 참조.
