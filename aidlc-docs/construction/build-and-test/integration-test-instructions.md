# Integration / Contract Test Instructions — U1 ↔ (main UI) 계약

> 본 브랜치는 단일 유닛(U1 Advisor Backend)만 포함. 통합의 핵심은 **U1이 제공하는 HTTP API 계약**을 소비자(`main` 브랜치 `frontend/` = U2 Web UI)가 sync 맞추는 것.
> CR-001 초점: `/advise` 응답에 **append-only**로 추가된 `actionHandoff` 계약.

## Purpose
U1 파이프라인 내부 컴포넌트 간 협업(오케스트레이터 E2E)과, U1↔main UI 공개 계약(특히 CR-001 `actionHandoff`)의 정합을 검증.

## Test Scenarios

### Scenario 1: 오케스트레이터 E2E (파이프라인 통합) — `tests/unit/test_orchestrator.py`
- **검증**: Hero(REUSE) + 3 Unhappy(NEEDS REVIEW / DEVELOP / CLARIFY) 시나리오가 C1→C7(+C11) 전 구간을 통과.
- **결과**: PASS (demoMode fixture 결정적 경로).

### Scenario 2: 공개 API 계약 — `tests/unit/test_api.py`
- **검증**: `/intent`, `/advise`, `/feedback` 응답 스키마 + 내부/미인가 필드 비노출(`technicalFailureReason`/`excluded`/`allowedRoles` 등 부재).
- **결과**: PASS.

### Scenario 3: CR-001 `actionHandoff` 계약 (main UI sync 대상)
- **계약 형태** (`AdviceResponse.actionHandoff: ActionPromptDTO | null`):
  ```json
  {
    "decisionState": "REUSE | EXTEND_EXISTING | DEVELOP | NEEDS_REVIEW",
    "promptText": "<외부 AI 도구용 실행 Prompt 전문 (목표·근거·다음작업·확인사항)>",
    "targetAssetNames": ["<대상 자산명>", "..."]
  }
  ```
  - `REUSE`/`EXTEND_EXISTING` → `targetAssetNames`에 최상위 접근가능 자산 1개.
  - `DEVELOP`/`NEEDS_REVIEW` → `targetAssetNames = []`.
  - 생성 실패 시 → `actionHandoff = null` (비차단, 기존 Decision/Evidence/랭킹 유지).
- **실측 스냅샷** (demoMode, Hero REUSE): `decisionState="REUSE"`, `targetAssetNames=["Customer 360 Dashboard"]`, `promptText`=4요소 한국어 본문(UTF-8).
- **main UI 반영 필요**: US-6.2 — `actionHandoff` 존재 시 표시 + Copy(성공/실패), `null`이면 기존 결과만 표시.

## Run
```bash
cd advisor-backend
export DEMO_MODE=true
./.venv/Scripts/python.exe -m pytest tests/unit/test_orchestrator.py tests/unit/test_api.py tests/unit/test_action_handoff.py -q
```

### 수동 계약 스냅샷 (선택)
```bash
uvicorn app.main:app --port 8000    # 별도 터미널
# POST /advise (demoMode) → 응답 JSON의 actionHandoff 필드 확인
```

## Notes
- 콘솔에서 한글 `promptText`가 깨져 보일 수 있으나(git-bash stdout 인코딩), API가 서빙하는 JSON은 UTF-8 정상 — 4요소 내용 검증 단위 테스트 통과로 확인됨.
