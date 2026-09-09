# Build Instructions — U1 Advisor Backend

> 범위: U1(`advisor-backend/`). Python 패키지형이므로 컴파일 산출물은 없고 "환경 구성 + import/컴파일 검증"이 build에 해당.
> U2(Web UI)는 코드 생성 미수행 → 본 문서 범위 밖(pending).

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
