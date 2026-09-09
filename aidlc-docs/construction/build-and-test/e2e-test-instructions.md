# End-to-End Test Instructions — U2 Web UI ↔ U1 (브라우저 시각 검증)

## Purpose
사용자가 실제로 마주하는 단일 화면(NFR-6)에서, U1 백엔드와 연동한 4개 핵심 워크플로가 **시각적으로 올바르게 렌더링**되는지 확인한다. (계약/DTO 정합은 `integration-test-instructions.md` Part B에서 검증 — 본 문서는 실 렌더링·UX 확인.)

> 상태: 타입체크·빌드는 통과 완료. **브라우저 4 시나리오 시각 확인은 데모 단계에서 수행**(자동화 e2e 프레임워크는 MVP 범위 밖 — 아래 수동 절차 + 선택적 Playwright 가이드).

## 사전 요건 (환경 기동)
```bash
# 터미널 1 — U1 백엔드 (결정적 fixture)
cd advisor-backend
# venv 활성화 후
export DEMO_MODE=true        # Windows(cmd): set DEMO_MODE=true / PowerShell: $env:DEMO_MODE="true"
uvicorn app.main:app --port 8000

# 터미널 2 — U2 프론트엔드
cd frontend
npm install                  # 최초 1회
npm run dev                  # http://localhost:5173
```
브라우저에서 `http://localhost:5173` 접속.

## 수동 E2E 시나리오

### E2E-1: Hero → REUSE (US-1.1/1.2, US-4.1/4.2)
1. 좌측 패널에서 **Hero(REUSE)** 데모 프리셋 선택.
2. `구조화하기`(`POST /intent`) → 5필드(역할/목표/기능/데이터/산출물) 렌더 확인.
3. `검색 · 자문 실행`(`POST /advise`).
- **기대**: 중앙에 Overall Decision 배너=**REUSE**, 후보 카드 목록 상단 asset-001(순위 1, State/재사용성 0.92/lifecycle/Source). 카드 선택 시 우측 EvidencePanel에 **다중 Source의 evidence chain + stateRationale** 표시.

### E2E-2: NEEDS_REVIEW (evaluationStatus 계약)
1. **NEEDS REVIEW** 프리셋 선택 → 구조화 → 자문.
- **기대**: Overall 배너=**NEEDS_REVIEW**. `UNAVAILABLE` 후보는 점수 대신 **'평가 미완료'** 배지, 재사용성 점수 미표기(null). deprecated lifecycle 표기 노출.

### E2E-3: DEVELOP + 미인가 비노출 (US-4.1, §3.2)
1. 권한 컨텍스트를 **Sales**로 두고 **DEVELOP** 프리셋 선택 → 자문.
- **기대**: Overall 배너=**DEVELOP**, 후보 카드 **0개**(접근 가능 자산 없음). 미인가 자산의 이름·존재가 화면 어디에도 노출되지 않음.

### E2E-4: Clarify → 보완 재제출 (US-1.3)
1. **Clarify** 프리셋(정보 부족) 선택 → `구조화하기`.
- **기대**: 명료화 질문 + 누락 필드 안내 렌더. 필드 보완 후 재제출 시 정상 구조화로 진행.

### E2E-5: 피드백 왕복 (US-4.3)
1. 임의 후보 선택 → FeedbackBar에서 `유용함`/`부적합` 클릭(`POST /feedback`).
- **기대**: 확인 id 표시, 오류 없음.

## 오류 경로 시각 확인
- 데모에 없는 자연어 입력 → `구조화하기`: 백엔드 `422 DEMO_FIXTURE_NOT_FOUND` → UI가 `ApiError` 메시지를 사용자 친화 안내로 표시(앱 크래시 없음).

## 검증 체크리스트
- [ ] 4 시나리오(REUSE/NEEDS_REVIEW/DEVELOP/Clarify) 시각 렌더 정상
- [ ] UNAVAILABLE '평가 미완료' 표기 확인
- [ ] 미인가 자산 화면 비노출 확인(§3.2)
- [ ] 명료화 → 보완 재제출 흐름 동작
- [ ] 피드백 왕복 확인 id 표시
- [ ] 오류 입력 시 우아한 오류 메시지(크래시 없음)

## (선택) 자동화 e2e
회귀 필요 시 Playwright 도입 권장:
```bash
cd frontend
npm i -D @playwright/test
npx playwright install chromium
# tests/e2e/*.spec.ts 작성 → npx playwright test
```
- 백엔드 `DEMO_MODE=true` 기동 상태를 전제로, 위 E2E-1~5를 셀렉터 기반으로 스크립트화.
- 현 MVP 산출물에는 미포함(수동 절차로 충분).
