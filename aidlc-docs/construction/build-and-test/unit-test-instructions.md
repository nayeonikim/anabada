# Unit / Component Test Execution — U1 Advisor Backend + U2 Web UI

> U1: 테스트는 Code Generation 단계에서 **생성 완료**. 본 단계에서 **실행/통과**를 확인. 실행 위치 `advisor-backend/`.
> U2: 별도 단위 테스트 프레임워크 없이 **정적 타입체크(`tsc --noEmit`, strict)** 가 컴포넌트 레벨 게이트. presentational 분리(상태는 App.tsx 소유) 설계로 타입 계약이 UI 정확성을 강하게 보장. 실 렌더링 검증은 e2e-test-instructions.md 참조.

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

---

# U2 Web UI — 정적 컴포넌트 게이트

## Run
```bash
cd frontend
npm install          # 최초 1회
npm run typecheck    # tsc --noEmit (strict)
```

## Review Results
- **Expected**: strict 타입 오류 0. (참조 실행값: `npm run build`의 `tsc --noEmit` 단계 오류 0, 38 modules 빌드 성공.)
- **핵심 검증 포인트**:
  - **API 계약 정합**: `src/api/types.ts`가 U1 공개 DTO/enum과 1:1. 제외/미인가 필드(`technicalFailureReason`·`excluded*`·`allowedRoles/Users`)가 **구조적으로 부재**(§3.2) → UI가 타입상 노출 불가.
  - **evaluationStatus 계약**: `UNAVAILABLE` 후보는 점수 대신 '평가 미완료' 표기(`badges.evaluationLabel`, 재사용성 null).
  - **props 계약**: `components/panel-props.ts`의 4개 패널 props가 App.tsx 파생값과 정합.
- **참고**: 향후 상호작용 회귀가 필요하면 Vitest + React Testing Library 도입 권장(현 MVP 범위 밖).

## Fix
1. `npm run typecheck` 출력의 파일:라인 확인.
2. U1 DTO 변경이 원인이면 `types.ts` → 컴포넌트/`panel-props.ts` 순으로 정렬.
3. 오류 0까지 반복 후 `npm run build`로 최종 확인.
