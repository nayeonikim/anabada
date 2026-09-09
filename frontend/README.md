# U2 — Rebuild or Reuse Advisor Web UI

단일 화면(NFR-6) React + Vite + TypeScript 프론트엔드. U1 백엔드(`advisor-backend/`)의 3개 HTTP API에만 의존한다.

## 스택
- React 18 + Vite 5 + TypeScript (strict)
- 상태 관리: React `useState` (경량, 외부 라이브러리 없음)
- API 통신: `fetch` + Vite dev server proxy (CORS 우회)

## 사전 요건
U1 백엔드가 먼저 실행 중이어야 한다 (기본 `http://localhost:8000`). 데모는 `DEMO_MODE=ON` 권장.

```bash
# 터미널 1 — 백엔드 (advisor-backend/README.md 참고)
cd advisor-backend
# venv 활성화 후
set DEMO_MODE=true            # Windows(cmd) / PowerShell: $env:DEMO_MODE="true"
uvicorn app.main:app --reload --port 8000
```

## 실행

```bash
# 터미널 2 — 프론트엔드
cd frontend
npm install
npm run dev
# 브라우저: http://localhost:5173
```

Vite dev proxy가 `/intent`·`/advise`·`/feedback` 요청을 `http://localhost:8000`으로 전달한다.
백엔드 주소가 다르면 `VITE_BACKEND_URL` 환경변수로 override:

```bash
VITE_BACKEND_URL=http://localhost:9000 npm run dev
```

## 사용 흐름 (단일 화면)
1. **요청 & 의도**(좌): 데모 프리셋 선택 또는 자연어 입력 → `구조화하기`(`POST /intent`).
   - 정보 부족 시 명료화 질문 표시 → 보완 후 재제출.
   - 구조화되면 5필드(역할/목표/기능/데이터/산출물) 편집 가능 → `검색 · 자문 실행`(`POST /advise`).
2. **후보 랭킹 & 종합 권고**(중): Overall Decision 배너 + 후보 카드(순위/State/재사용성 점수/lifecycle/Source). 카드 선택 시 근거 표시. 피드백 버튼(`POST /feedback`).
3. **근거 Evidence Chain**(우): 선택 후보의 결정 근거 + 출처 목록.

## 데모 프리셋
`src/demo/presets.ts`는 U1 `data/demo_fixtures.json`의 정확한 rawText에서 자동 추출됨.
`DEMO_MODE=ON`일 때 결정적 fixture 응답(Hero REUSE / NEEDS REVIEW / DEVELOP / Clarify)을 재현한다.

## 스크립트
- `npm run dev` — 개발 서버
- `npm run typecheck` — `tsc --noEmit`
- `npm run build` — 타입체크 + 프로덕션 번들
- `npm run preview` — 빌드 결과 미리보기

## 설계 메모
- 미인가/제외된 자산 정보는 백엔드 응답 DTO에 구조적으로 부재(§3.2)하며, UI에서도 노출하지 않는다.
- `evaluationStatus=UNAVAILABLE` 후보는 점수 대신 "평가 미완료"로 표시(재사용성 점수 null).
