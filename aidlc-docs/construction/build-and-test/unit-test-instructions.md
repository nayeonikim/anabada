# Unit Test Execution — U1 Advisor Backend

> pytest 예제 기반 단위 테스트 + Hypothesis PBT(순수 판단 로직). CR-001 Action Handoff 테스트 포함.

## Run Unit Tests

### 1. Execute All Tests
```bash
cd advisor-backend
export DEMO_MODE=true
./.venv/Scripts/python.exe -m pytest tests/ -q
```

### 2. Category별 실행 (선택)
```bash
./.venv/Scripts/python.exe -m pytest tests/pbt   -q   # PBT (순수 로직)
./.venv/Scripts/python.exe -m pytest tests/unit  -q   # 예제 기반 단위/통합
```

### 3. Review Test Results (실제 결과, 2026-09-09)
- **Total**: 52 (PBT 13 + Unit 39) — **52 passed, 0 failed**.
- **PBT (`tests/pbt/`)**: `test_decision_classifier.py`(P1~P11 순수 로직), `test_action_handoff.py`(INV-HANDOFF-1 decisionState==overall / -2 targetAssetNames 규칙 / -5 §3.1 게이팅).
- **Unit (`tests/unit/`)**: components(C1~C5·C7·C8), decision_classifier 예제, orchestrator(Hero + 3 Unhappy), api(/intent·/advise·/feedback + 내부필드 비노출), `test_action_handoff.py`(INV-HANDOFF-3 비노출·-4 실패→null 비차단·최소 유용성 4요소·demoMode 재현·e2e).
- **Warnings**: 2 (starlette TestClient httpx deprecation) — 무해.

### 4. Fix Failing Tests (본 실행에서 발견·수정된 회귀)
- **회귀**: CR-001이 `LLMClient` ABC에 추상 메서드 `generate_action_prompt`를 추가 → `tests/unit/test_components.py`의 기존 테스트 더블 `_AllFailLLM`/`_PartialFailLLM`(ABC 직접 상속)이 미구현으로 인스턴스화 불가(`TypeError`).
- **수정**: 두 테스트 더블에 `generate_action_prompt` 최소 구현 추가(`RuntimeError("n/a")` — 해당 C5 테스트에서 미호출). 코드 로직 변경 없음, 테스트 더블만 갱신.
- **재실행 결과**: 전체 52 passed.
