#!/usr/bin/env bash
# 아나바다 데모 원클릭 런처
# ------------------------------------------------------------------
# U1 FastAPI 백엔드(:8000)와 U2 React+Vite 웹 UI를 함께 띄우고,
# 기본 브라우저로 UI를 열어 사람이 직접 클릭하며 데모할 수 있게 한다.
# 실행: bash scripts/demo.sh   (종료: Ctrl+C — 두 서버 모두 정리됨)
#
# 기본은 Demo Mode(DEMO_MODE=true). AWS Credential 불필요, 결정적 Fixture 사용.
# macOS / Linux / Windows(Git Bash) 에서 동작.
set -euo pipefail

# --- 경로: 이 스크립트 위치 기준으로 repo 루트 계산 -----------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND="$ROOT/advisor-backend"
FRONTEND="$ROOT/frontend"
BACKEND_PORT=8000

IS_WINDOWS=0
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=1 ;; esac

log()  { printf '\033[36m▶ %s\033[0m\n' "$*"; }
ok()   { printf '\033[32m✓ %s\033[0m\n' "$*"; }
die()  { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# --- 백엔드 venv 파이썬 경로 확보 (없으면 생성 + 의존성 설치) --------
resolve_python() {
  if   [ -x "$BACKEND/.venv/Scripts/python.exe" ]; then echo "$BACKEND/.venv/Scripts/python.exe"
  elif [ -x "$BACKEND/.venv/bin/python" ];        then echo "$BACKEND/.venv/bin/python"
  else echo ""; fi
}

PY="$(resolve_python)"
if [ -z "$PY" ]; then
  log "백엔드 venv가 없어 생성합니다 (최초 1회, 수 분 소요)"
  BOOT_PY="$(command -v python3 || command -v python || true)"
  [ -n "$BOOT_PY" ] || die "python 을 찾을 수 없습니다. Python 3.11+ 를 설치하세요."
  ( cd "$BACKEND" && "$BOOT_PY" -m venv .venv )
  PY="$(resolve_python)"
  [ -n "$PY" ] || die "venv 생성에 실패했습니다."
  log "백엔드 의존성 설치 중..."
  "$PY" -m pip install -q -r "$BACKEND/requirements.txt" || die "pip install 실패"
  ok "백엔드 의존성 설치 완료"
fi

# --- 프론트엔드 의존성 --------------------------------------------
NPM="$(command -v npm || command -v npm.cmd || true)"
[ -n "$NPM" ] || die "npm 을 찾을 수 없습니다. Node.js 18+ 를 설치하세요."
if [ ! -d "$FRONTEND/node_modules" ]; then
  log "프론트엔드 의존성 설치 중 (최초 1회)..."
  ( cd "$FRONTEND" && "$NPM" install ) || die "npm install 실패"
  ok "프론트엔드 의존성 설치 완료"
fi

# --- 정리 훅 -------------------------------------------------------
BACK_PID=""; FRONT_PID=""
VITE_LOG="$(mktemp -t anabada-vite.XXXXXX.log)"
cleanup() {
  trap - INT TERM EXIT
  log "데모 종료 — 서버 정리 중..."
  for pid in "$FRONT_PID" "$BACK_PID"; do
    [ -n "$pid" ] || continue
    if [ "$IS_WINDOWS" -eq 1 ]; then
      taskkill //PID "$pid" //T //F >/dev/null 2>&1 || true
    else
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done
  rm -f "$VITE_LOG"
  ok "정리 완료"
}
trap cleanup INT TERM EXIT

# --- 백엔드 기동 (이미 :8000이 응답하면 재사용 — 포트 충돌 회피/멱등) ---
existing="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$BACKEND_PORT/docs" 2>/dev/null || echo 000)"
if [ "$existing" = "200" ]; then
  ok "이미 실행 중인 백엔드(:$BACKEND_PORT) 재사용"
else
  log "백엔드 기동 (:$BACKEND_PORT, DEMO_MODE=true)"
  ( cd "$BACKEND" && DEMO_MODE=true "$PY" -m uvicorn app.main:app --port "$BACKEND_PORT" --log-level warning ) &
  BACK_PID=$!

  code=000
  for i in $(seq 1 40); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$BACKEND_PORT/docs" 2>/dev/null || echo 000)"
    [ "$code" = "200" ] && break
    kill -0 "$BACK_PID" 2>/dev/null || die "백엔드가 기동 중 종료되었습니다. (:$BACKEND_PORT 가 이미 사용 중인가요?)"
    sleep 0.5
  done
  [ "$code" = "200" ] || die "백엔드가 20초 내 준비되지 않았습니다."
  ok "백엔드 준비됨 → http://localhost:$BACKEND_PORT/docs"
fi

# --- 프론트엔드 기동 (Vite; 포트는 자동 폴백될 수 있음) ------------
# NO_COLOR=1 : Vite 로그의 ANSI 색상 코드를 끔 → URL 라인을 안정적으로 파싱.
log "프론트엔드 기동 (Vite)"
( cd "$FRONTEND" && NO_COLOR=1 "$NPM" run dev ) >"$VITE_LOG" 2>&1 &
FRONT_PID=$!

URL=""
for i in $(seq 1 40); do
  URL="$(grep -oE 'http://localhost:[0-9]+/?' "$VITE_LOG" 2>/dev/null | head -n1 || true)"
  [ -n "$URL" ] && break
  kill -0 "$FRONT_PID" 2>/dev/null || die "프론트엔드가 기동 중 종료되었습니다. 로그: $VITE_LOG"
  sleep 0.5
done
[ -n "$URL" ] || die "프론트엔드 URL을 감지하지 못했습니다. 로그: $VITE_LOG"
ok "프론트엔드 준비됨 → $URL"

# --- 브라우저 열기 -------------------------------------------------
open_url() {
  local url="$1"
  case "$(uname -s)" in
    Darwin) open "$url" >/dev/null 2>&1 || true ;;
    MINGW*|MSYS*|CYGWIN*) cmd //c start "" "$url" >/dev/null 2>&1 || true ;;
    *) xdg-open "$url" >/dev/null 2>&1 || true ;;
  esac
}
if [ -n "${ANABADA_NO_OPEN:-}" ]; then
  log "브라우저 자동 열기 건너뜀 (ANABADA_NO_OPEN)"
else
  log "브라우저 열기: $URL"
  open_url "$URL"
fi

printf '\n'
ok "데모 실행 중"
printf '   UI  : %s\n' "$URL"
printf '   API : http://localhost:%s/docs\n' "$BACKEND_PORT"
printf '\n\033[33m종료하려면 이 터미널에서 Ctrl+C 를 누르세요.\033[0m\n\n'

# 포그라운드 유지 — Ctrl+C 시 cleanup 트랩이 두 서버를 정리한다.
wait
