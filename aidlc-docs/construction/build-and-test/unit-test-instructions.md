# Unit Test Execution — U1 Advisor Backend

> 테스트는 Code Generation 단계에서 **생성 완료**. 본 단계에서 **실행/통과**를 확인.
> 실행 위치: `advisor-backend/` (가상환경 활성화 상태).

## 테스트 인벤토리
| 파일 | 유형 | 커버리지 |
|---|---|---|
| `tests/pbt/test_decision_classifier.py` | Property-Based(Hypothesis) | C6 불변식 P1~P11 (§7.4) |
| `tests/unit/test_decision_classifier_examples.py` | 예제 경계 | 임계값 0.75/0.50 경계, evidenceSufficient |
| `tests/unit/test_components.py` | 컴포넌트 | C1~C5,C7,C8 (LLM Fixture 주입) |
| `tests/unit/test_orchestrator.py` | 서비스 e2e | S1 Hero + 3 Unhappy |
| `tests/unit/test_api.py` | API | 라우트·공개 DTO 비노출·오류 매핑 |
| `tests/unit/conftest.py` | fixture | repository / registry |

## Run Unit Tests

### 1. Execute All Tests
```bash
cd advisor-backend
pytest -q
```

### 2. 카테고리별 실행
```bash
pytest tests/pbt -q       # Property-Based (C6 P1~P11)
pytest tests/unit -q      # 예제 + 컴포넌트 + orchestrator + API
```

### 3. (선택) 커버리지
```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing -q
```

## Review Test Results
- **Expected**: 전체 PASS, 0 failures. Hypothesis 예제 생성 케이스 포함 통과.
- **핵심 검증 포인트**:
  - **P1~P11**: UNAVAILABLE⇒NEEDS_REVIEW, 기술실패↛DEVELOP, score-status 정합, 랭킹 2계층 결정성.
  - **Hero(REUSE)**: asset-001 rank=1, score=0.92, Overall=REUSE.
  - **NEEDS_REVIEW**: asset-007(deprecated, 최고 Score COMPLETED, evidenceSufficient=false) → Overall=NEEDS_REVIEW.
  - **DEVELOP**: Sales가 Developer 전용 자산에 접근 불가 → accessible 0 → ranking=[], Overall=DEVELOP.
  - **Clarify**: role/data 누락 → ClarificationRequest.
  - **API 비노출(§3.2)**: 응답 JSON에 `technicalFailureReason`·`excluded*`·`allowedRoles/Users` 부재.
  - **오류 매핑(§1.6)**: 빈 rawText→400 EMPTY_INTENT, demo 미매칭→422 DEMO_FIXTURE_NOT_FOUND.
- **Test Report Location**: 콘솔 출력(기본). `--cov-report=html` 시 `htmlcov/`.

## Fix Failing Tests
테스트 실패 시:
1. `pytest -vv <실패 노드>` 로 상세 재현.
2. Hypothesis 실패는 최소 반례(falsifying example)를 출력 → C6 규칙(BR-STATE/BR-OVERALL/BR-RANK) 대조.
3. API/오케스트레이터 실패는 fixture 데이터(`data/*.json`)와 기대 시나리오 값 대조.
4. 코드 수정 후 재실행하여 전부 통과할 때까지 반복.
