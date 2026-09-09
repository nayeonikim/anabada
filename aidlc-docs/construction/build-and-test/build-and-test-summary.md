# Build and Test Summary — U1 Advisor Backend

> 범위: U1(`advisor-backend/`). U2(Web UI)는 코드 생성 미수행 → **pending**(별도 유닛 루프에서 진행 예정).
> 실행 환경: Python 3.12(로컬 venv), `DEMO_MODE=true`(결정적 fixture).

## Build Status
- **Build Tool**: venv + pip (Python 패키지형, 컴파일 산출물 없음)
- **Build Status**: ✅ Success
  - `python -m compileall app tests` → 오류 없음
  - `create_app()` 조립 import + mock 로드(12 assets · 6 adapters) 정상
  - 라우트 노출: `/intent`, `/advise`, `/feedback` 확인
- **Build Artifacts**: 소스 트리 + `requirements.txt`(fastapi, uvicorn, pydantic v2, boto3, hypothesis, pytest, httpx)
- **Build Time**: 의존성 설치 ~수십 초, 검증 즉시

## Test Execution Summary

### Unit / Component Tests
- **Total Tests**: 44
- **Passed**: 44
- **Failed**: 0
- **Coverage**: 92% (TOTAL, `pytest-cov`)
- **Status**: ✅ Pass
- **분포**:
  | 파일 | 개수 |
  |---|---|
  | `tests/pbt/test_decision_classifier.py` (Hypothesis P1~P11) | 10 |
  | `tests/unit/test_decision_classifier_examples.py` (경계) | 10 |
  | `tests/unit/test_components.py` (C1~C5,C7,C8) | 11 |
  | `tests/unit/test_orchestrator.py` (S1 e2e) | 5 |
  | `tests/unit/test_api.py` (API·DTO·오류) | 8 |

### Integration Tests (파이프라인 통합, 인프로세스 TestClient)
- **Test Scenarios**: 4 (Hero REUSE / 재검증 전체 실패 502 / DEVELOP / demoMode 미매칭 422)
- **Passed**: 4 (해당 시나리오는 `test_api.py` + `test_orchestrator.py`에 포함되어 통과)
- **Failed**: 0
- **Status**: ✅ Pass
- **참고**: 유닛 간(U1↔U2) 통합은 U2 생성 후 추가 예정(pending).

### Performance Tests
- **Status**: ⏸️ N/A (본 실행에서 미수행 — 지침만 제공)
- MVP는 mock + demoMode 기반. 실사용 성능은 LLM 지연 지배 → 별도 용량 계획 필요.
- 지침: `performance-test-instructions.md` (demoMode ON p95 < 200ms 목표).

### Additional Tests
- **Contract Tests**: N/A (단일 유닛; U2 추가 시 API 계약 테스트 권장)
- **Security Tests**: N/A (Security Baseline 확장 비활성; 단, 권한 필터·미인가 비노출은 기능 테스트로 검증됨 — `test_api.py`의 내부 필드 부재 검증)
- **E2E Tests**: 파이프라인 e2e는 orchestrator/API 테스트로 커버(UI e2e는 U2 이후)

### 커버리지 하이라이트
- 100%: `domain/models.py`, `domain/errors.py`, `api/schemas.py`, `decision_classifier.py`, `candidate_selection.py`, `evidence_builder.py`, `feedback.py`, `structure.py`, `registry.py`
- 부분: `llm_client.py` 56%(BedrockClaudeClient 실호출 경로는 demoMode OFF·실제 AWS 필요로 미실행), `config.py` 77%(env 파싱 분기 일부)

## Overall Status
- **Build**: ✅ Success
- **All Tests**: ✅ Pass (44/44, coverage 92%)
- **Ready for Operations**: ⚠️ U1 한정 Yes. 전체 제품(U1+U2) 관점에서는 U2 Web UI 구성 필요.

## 검증된 핵심 계약
- **evaluationStatus(§7.1)**: COMPLETED만 Score 판정 / UNAVAILABLE⇒NEEDS_REVIEW·score=null (PBT P1·P11).
- **기술 실패↛DEVELOP(BR-OVERALL/P5·P10)**, 랭킹 2계층 결정성(P8).
- **Type-Enforced Non-Disclosure(§3.2)**: 공개 응답에 `technicalFailureReason`·`excluded*`·`allowedRoles/Users` 부재(API 테스트 통과).
- **오류 매핑(§1.6)**: 400 EMPTY_INTENT / 422 DEMO_FIXTURE_NOT_FOUND / 502 REVERIFICATION_UNAVAILABLE.
- **demoMode 폴백 없음(§1.2)**: 미매칭 입력 → 명시적 422.

## Next Steps
- (전부 통과) Operations 단계(배포 계획)로 진행 가능 — **단 U1 범위**.
- 전체 제품 완성을 원하면: U2(Web UI) 유닛의 per-unit 루프(Functional Design → … → Code Generation) 수행 후, 유닛 간 통합/계약 테스트 추가 → 재-Build&Test.
