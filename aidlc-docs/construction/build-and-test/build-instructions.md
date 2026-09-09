# Build Instructions — U1 Advisor Backend + U2 Web UI

> 범위: **U1**(`advisor-backend/`, Python) + **U2**(`frontend/`, React+Vite+TS).
> U1은 Python 패키지형이라 컴파일 산출물 없이 "환경 구성 + import/컴파일 검증"이 build에 해당.
> U2는 `tsc --noEmit`(strict 타입체크) + `vite build`(프로덕션 번들)이 build에 해당.

## Prerequisites
- **Runtime**: Python 3.11+
- **Build/Env Tool**: `venv` + `pip`
- **Dependencies**: `advisor-backend/requirements.txt`
  - fastapi, uvicorn[standard], pydantic(v2), boto3, hypothesis, pytest, httpx
- **Environment Variables**: 없음(필수). 기본값으로 동작(`DEMO_MODE=true`). `.env.example` 참조.
  - Bedrock 실사용 시(`DEMO_MODE=false`)에만 AWS 자격증명 + `LLM_*` 필요.
- **System Requirements**: OS 무관(Windows/macOS/Linux), 메모리 ~512MB, 디스크 ~200MB(가상환경 포함)

## Build Steps

### 1. Install Dependencies
```bash
cd advisor-backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# 기본(demoMode=ON, Bedrock 불필요) — 별도 설정 없이 동작
cp .env.example .env    # 선택: 값 조정 시에만
# (선택) 실제 LLM 사용:
# export DEMO_MODE=false AWS_REGION=us-east-1  # + AWS 자격증명
```

### 3. Build (컴파일/Import 검증)
```bash
# 3-1) 전체 소스 바이트컴파일(구문 검증)
python -m compileall app tests

# 3-2) 앱 조립 import 검증(DI 그래프 로드 + mock 데이터 로드)
python -c "from app.main import create_app; app = create_app(); print('app routes:', [r.path for r in app.routes])"
```

### 4. Verify Build Success
- **Expected Output**:
  - `compileall`: 오류 없이 종료(exit 0), `Listing ...`만 출력.
  - import 검증: `app routes: [..., '/intent', '/advise', '/feedback', ...]` 출력.
- **Build Artifacts**: `__pycache__/*.pyc`(부수적). 배포 산출물은 소스 트리 자체 + `requirements.txt`.
- **Common Warnings**: 없음. (pydantic v2 deprecation 경고가 보이면 버전 확인)

## Troubleshooting

### Build Fails with Dependency Errors
- **Cause**: Python < 3.11, 또는 pip 캐시/네트워크 문제.
- **Solution**: `python --version`으로 3.11+ 확인 → `pip install --upgrade pip` → `pip install -r requirements.txt` 재실행.

### Import Fails: `ModuleNotFoundError: app...`
- **Cause**: `advisor-backend/`가 아닌 상위 디렉터리에서 실행.
- **Solution**: `cd advisor-backend` 후 실행(패키지 루트 기준). 테스트/실행 모두 이 디렉터리에서.

### Import Fails: fixture/데이터 경로 오류
- **Cause**: `data/*.json` 누락 또는 `ASSETS_PATH` 등 env 오설정.
- **Solution**: `data/assets.json`·`evidence.json`·`demo_fixtures.json` 존재 확인. 경로는 기본적으로 `advisor-backend/` 기준 상대 해석됨.

---

# U2 Web UI (`frontend/`)

## Prerequisites
- **Runtime**: Node.js 18+ (LTS 권장), npm 9+
- **Build Tool**: Vite 5 + TypeScript 5(strict) + `@vitejs/plugin-react`
- **Dependencies**: `frontend/package.json` (react, react-dom / dev: vite, typescript, @types/*)
- **Environment Variables**: 없음(필수). dev proxy는 `/intent`·`/advise`·`/feedback`를 `http://localhost:8000`으로 전달. 백엔드 주소가 다르면 `VITE_BACKEND_URL`로 override.
- **System Requirements**: OS 무관, 메모리 ~512MB, 디스크 ~150MB(node_modules 포함)

## Build Steps

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Build (타입체크 + 프로덕션 번들)
```bash
# package.json의 build = "tsc --noEmit && vite build"
npm run build
```
(타입체크만 별도 실행: `npm run typecheck`)

### 3. Verify Build Success
- **Expected Output**: `tsc --noEmit` 오류 0 → `vite build`가 `✓ NN modules transformed` + `dist/` 산출.
  - 참조 실행값: **38 modules transformed**, strict 오류 0, `dist/assets/index-*.js` ~154KB(gzip ~50KB), `index-*.css` ~6KB.
- **Build Artifacts**: `frontend/dist/`(index.html + hashed assets). 정적 호스팅 가능.
- **Common Warnings**: 없음(경고 0 상태로 통과 확인됨).

## Troubleshooting

### `tsc` strict 오류
- **Cause**: 타입 불일치(예: U1 DTO 미러 `src/api/types.ts` 변경 후 컴포넌트 미갱신).
- **Solution**: `npm run typecheck`로 오류 위치 확인 → 타입/props 정렬 후 재빌드.

### dev 실행 시 API 404 / CORS
- **Cause**: 백엔드 미기동 또는 포트 불일치.
- **Solution**: U1(`uvicorn app.main:app --port 8000`, `DEMO_MODE=true`) 먼저 기동. 포트 다르면 `VITE_BACKEND_URL` 지정.
