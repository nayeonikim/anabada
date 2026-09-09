# Build Instructions — U1 Advisor Backend (CR-001 포함)

> CONSTRUCTION - Build and Test. 유닛: **U1 Advisor Backend** (`advisor-backend/`). U2 Web UI는 본 브랜치 범위 밖(`main` 브랜치 `frontend/`에 존재).
> 실제 실행 환경: Windows 11 / Python 3.12.10 / git-bash. 결과는 `build-and-test-summary.md` 참조.

## Prerequisites
- **Build Tool**: Python `venv` + `pip` (별도 컴파일 없음 — 순수 Python).
- **Runtime**: Python 3.11+ (검증: 3.12.10).
- **Dependencies**: `advisor-backend/requirements.txt` — fastapi, uvicorn[standard], pydantic, boto3, hypothesis, pytest, httpx.
- **Environment Variables**:
  - `DEMO_MODE=true` — 결정적 fixture 경로(LLM/Bedrock 미호출). 빌드·테스트·데모에 권장.
  - (실 호출 시) 표준 AWS 자격증명 체인 + `LLM_TIMEOUT_SECONDS` 등 — 테스트에는 불필요.
- **System Requirements**: 인터넷(최초 pip install 시), 디스크 ~수백 MB(venv).

## Build Steps

### 1. Install Dependencies
```bash
cd advisor-backend
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r requirements.txt
# (macOS/Linux는 ./.venv/bin/python)
```

### 2. Configure Environment
```bash
export DEMO_MODE=true   # 결정적 데모 경로 (LLM 미호출)
```

### 3. Build / Import 검증 (컴파일 대체)
```bash
./.venv/Scripts/python.exe -c "import app.main; print(app.main.app.title)"
# 기대 출력: Reuse Advisor Backend (U1)
```

### 4. Verify Build Success
- **Expected Output**: `app.main` import 성공, FastAPI app 제목 출력.
- **Build Artifacts**: 없음(인터프리터 실행형). 실행은 `uvicorn app.main:app`.
- **Common Warnings**: starlette TestClient의 httpx deprecation 경고 — 무해(테스트 전용).

## Troubleshooting
### Build Fails with Dependency Errors
- **Cause**: 네트워크/프록시, Python 버전(<3.11).
- **Solution**: Python 3.11+ 확인, `pip install -r requirements.txt` 재시도.

### Import Fails (`ModuleNotFoundError: app`)
- **Cause**: 작업 디렉토리 오류.
- **Solution**: `advisor-backend/`에서 실행(패키지 루트). venv의 python 사용.
