# Build and Test Summary — U1 Advisor Backend (CR-001 Action Handoff)

> 실행 일자: 2026-09-09 · 환경: Windows 11 / Python 3.12.10 / git-bash · 모드: `DEMO_MODE=true`
> 범위: **U1 Advisor Backend** (`advisor-backend/`). 목적: `main` 브랜치 UI(`frontend/`)가 소비할 백엔드 계약(CR-001 `actionHandoff` 포함) 검증 및 sync.
> U2 Web UI 신규 빌드는 본 브랜치 범위 밖(U2는 `main`에 존재).

## Build Status
- **Build Tool**: Python venv + pip (순수 Python, 컴파일 없음).
- **Build Status**: ✅ Success — `pip install -r requirements.txt` 완료, `import app.main` 성공(FastAPI app "Reuse Advisor Backend (U1)").
- **Build Artifacts**: 없음(인터프리터 실행). 실행 진입점 `uvicorn app.main:app`.
- **Install 확인 버전(요지)**: fastapi 0.141.1, pydantic 2.13.5, boto3 1.43.90, hypothesis 6.168.0, pytest 8.4.2, httpx 0.28.1.

## Test Execution Summary

### Unit + PBT Tests
- **Total Tests**: 52 (PBT 13 + Unit 39)
- **Passed**: 52
- **Failed**: 0
- **Coverage**: 정량 측정 안 함(해커톤 MVP). 커버 범위: C1~C8 + C11, 결정 분류 P1~P11, orchestrator E2E(Hero+3 Unhappy), 공개 API 계약·비노출, CR-001 INV-HANDOFF-1~5.
- **Status**: ✅ Pass

### Integration / Contract Tests
- **Scenarios**: 3 (orchestrator E2E / 공개 API 계약·비노출 / CR-001 `actionHandoff` 계약)
- **Status**: ✅ Pass
- **actionHandoff 계약 확정**: `AdviceResponse.actionHandoff: ActionPromptDTO | null`, `ActionPromptDTO = { decisionState, promptText, targetAssetNames[] }` (camelCase). 실측 스냅샷(Hero REUSE): `decisionState="REUSE"`, `targetAssetNames=["Customer 360 Dashboard"]`.

### Performance Tests
- **Status**: N/A — Hard SLA 없음(tech-stack-decisions D6, best-effort). 부하/스트레스 테스트 비수행(MVP).

### Additional Tests
- **Contract Tests**: ✅ (integration-test-instructions.md Scenario 3 — main UI sync 계약)
- **Security Tests**: N/A (Security Baseline Disabled; 단 미인가/내부 필드 비노출은 `test_api.py`·INV-HANDOFF-3로 검증됨)
- **E2E Tests**: ✅ (demoMode `/advise` 실호출 → actionHandoff 정상)

## 발견·조치 사항 (본 실행)
- **회귀 발견 및 수정**: CR-001이 `LLMClient` ABC에 추상 메서드 `generate_action_prompt` 추가 → 기존 테스트 더블(`tests/unit/test_components.py`의 `_AllFailLLM`/`_PartialFailLLM`) 인스턴스화 불가(TypeError). 두 더블에 최소 구현 추가로 수정(코드 로직 무변경). Code Gen Step 11 "기존 테스트 불변" 주장이 pytest 미실행(이전 세션 fastapi 미설치)으로 미검증됐던 부분 — 본 실행에서 실제 검증·해소.
- **환경 메모**: git-bash 콘솔에서 한글 출력이 깨져 보이나(stdout 인코딩), 저장/서빙 데이터는 UTF-8 정상(내용 검증 단위 테스트 통과로 확인).

## Overall Status
- **Build**: ✅ Success
- **All Tests**: ✅ Pass (52/52)
- **Ready for Operations**: Operations는 PLACEHOLDER. **main UI sync 관점**: `actionHandoff` 계약 확정·검증 완료 → main UI(`frontend/`)에서 US-6.2(표시·Copy·부재 안내) 반영 가능.

## Next Steps
- main 브랜치 UI가 `actionHandoff` 계약(위 형태)에 맞춰 표시/Copy 구현(US-6.2).
- (선택) 본 브랜치를 `main`/`origin/codex/action-handoff`에 반영 시, 백엔드 계약 변경은 append-only(비회귀)이므로 기존 UI 소비 로직에 영향 없음.
