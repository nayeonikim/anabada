# Build and Test Summary — 제품 전체 (U1 Advisor Backend + U2 Web UI)

> 범위: **U1**(`advisor-backend/`, Python) + **U2**(`frontend/`, React+Vite+TS).
> 실행 환경: U1 = Python 3.12(로컬 venv), `DEMO_MODE=true`(결정적 fixture). U2 = Node 18+ / npm.

## Build Status

### U1 — Advisor Backend
- **Build Tool**: venv + pip (Python 패키지형, 컴파일 산출물 없음)
- **Build Status**: ✅ Success
  - `python -m compileall app tests` → 오류 없음
  - `create_app()` 조립 import + mock 로드(12 assets · 6 adapters) 정상
  - 라우트 노출: `/intent`, `/advise`, `/feedback` 확인
- **Build Artifacts**: 소스 트리 + `requirements.txt`(fastapi, uvicorn, pydantic v2, boto3, hypothesis, pytest, httpx)

### U2 — Web UI
- **Build Tool**: Vite 5 + TypeScript 5(strict) + `@vitejs/plugin-react`
- **Build Status**: ✅ Success
  - `npm run build` (= `tsc --noEmit && vite build`) → **strict 타입 오류 0**
  - **38 modules transformed**, `dist/` 산출(js ~154.66KB / gzip ~50.26KB, css ~5.99KB), built in ~626ms
- **Build Artifacts**: `frontend/dist/`(index.html + hashed assets, 정적 호스팅 가능)

## Test Execution Summary

### Unit / Component Tests
- **U1**: 44 tests, **44 passed / 0 failed**, coverage **92%** (`pytest-cov`)
  | 파일 | 개수 |
  |---|---|
  | `tests/pbt/test_decision_classifier.py` (Hypothesis P1~P11) | 10 |
  | `tests/unit/test_decision_classifier_examples.py` (경계) | 10 |
  | `tests/unit/test_components.py` (C1~C5,C7,C8) | 11 |
  | `tests/unit/test_orchestrator.py` (S1 e2e) | 5 |
  | `tests/unit/test_api.py` (API·DTO·오류) | 8 |
- **U2**: 정적 컴포넌트 게이트 = `tsc --noEmit`(strict) **오류 0**. 별도 단위 테스트 프레임워크는 MVP 범위 밖(presentational 분리 + 타입 계약으로 정확성 보장).
- **Status**: ✅ Pass

### Integration Tests
- **Part A (U1 파이프라인)**: 4 시나리오(Hero REUSE / 재검증 전체 실패 502 / DEVELOP / demoMode 미매칭 422) — `test_api.py` + `test_orchestrator.py`에 포함, **4 passed / 0 failed**. (인프로세스 TestClient)
- **Part B (U1↔U2 계약)**: dev proxy 경유 4 데모 프리셋(B-1~B-4) 계약 시나리오 지침화 — DTO 형태 일치 + §3.2 비노출 + 오류 모델 파싱 + 피드백 왕복. **실 왕복 시각 검증은 데모/e2e 단계에서 수행**(지침 제공).
- **Status**: ✅ Pass (A 자동 통과) / 🔶 Part B 실 렌더링은 데모 단계

### Performance Tests
- **Status**: ⏸️ N/A (본 실행에서 미수행 — 지침만 제공)
- MVP는 mock + demoMode 기반. 실사용 성능은 LLM 지연 지배 → 별도 용량 계획 필요.
- 지침: `performance-test-instructions.md` (demoMode ON p95 < 200ms 목표).

### E2E Tests (UI)
- **Status**: 🔶 지침 완비 / 실 브라우저 시각 확인은 데모 단계
- `e2e-test-instructions.md`: 4 워크플로(REUSE/NEEDS_REVIEW/DEVELOP/Clarify) + 피드백 + 오류 경로 수동 절차, 선택적 Playwright 가이드.

### Additional Tests
- **Contract Tests**: U1↔U2 계약은 U2 `types.ts`(U1 공개 DTO 1:1 미러) + integration Part B로 커버. 별도 소비자주도 계약 프레임워크는 미도입.
- **Security Tests**: N/A (Security Baseline 확장 비활성). 단, 권한 필터·미인가 비노출은 U1 기능 테스트(`test_api.py` 내부 필드 부재) + U2 타입 구조(§3.2)로 이중 검증됨.

### 커버리지 하이라이트 (U1)
- 100%: `domain/models.py`, `domain/errors.py`, `api/schemas.py`, `decision_classifier.py`, `candidate_selection.py`, `evidence_builder.py`, `feedback.py`, `structure.py`, `registry.py`
- 부분: `llm_client.py` 56%(BedrockClaudeClient 실호출 경로는 demoMode OFF·실제 AWS 필요로 미실행), `config.py` 77%(env 파싱 분기 일부)

## Overall Status
- **Build**: ✅ Success (U1 import/compile + U2 tsc/vite build 모두 통과)
- **All Tests**: ✅ Pass (U1 44/44·coverage 92%, U2 strict 0, 통합 A 4/4)
- **Ready for Operations**: ✅ Yes (제품 전체 U1+U2). 단, 실 브라우저 4 시나리오 시각 확인 및 성능/실 LLM 경로는 데모/Operations에서 수행.

## 검증된 핵심 계약
- **evaluationStatus(§7.1)**: COMPLETED만 Score 판정 / UNAVAILABLE⇒NEEDS_REVIEW·score=null (PBT P1·P11). U2는 '평가 미완료'로 표기.
- **기술 실패↛DEVELOP(BR-OVERALL/P5·P10)**, 랭킹 2계층 결정성(P8).
- **Type-Enforced Non-Disclosure(§3.2)**: U1 공개 응답 + U2 `types.ts` 모두에 `technicalFailureReason`·`excluded*`·`allowedRoles/Users` 부재.
- **오류 매핑(§1.6)**: 400 EMPTY_INTENT / 422 DEMO_FIXTURE_NOT_FOUND / 502 REVERIFICATION_UNAVAILABLE. U2 `client.ts`가 `{error:{code,message,requestId}}` 파싱.
- **demoMode 폴백 없음(§1.2)**: 미매칭 입력 → 명시적 422. U2 데모 프리셋 rawText는 U1 fixture와 정확히 일치.

## Next Steps
- (전부 통과) **Operations 단계(배포 계획)로 진행 가능** — 제품 전체(U1+U2).
- 데모 시연 시: `integration-test-instructions.md` Part B + `e2e-test-instructions.md`의 4 시나리오를 브라우저에서 순차 확인.
- 실 LLM/성능 검증은 `DEMO_MODE=false` + 용량 계획으로 Operations에서 다룸.
