---
name: run
description: Launch and drive the anabada Rebuild-or-Reuse Advisor — U1 FastAPI backend (:8000) and U2 React+Vite web UI — and verify the demo end-to-end via a browser. Use when asked to run/start the app, screenshot it, or confirm a change works in the real app.
---

# Run the anabada Advisor (backend + web UI)

Two apps in this repo:

- `advisor-backend/` — FastAPI (U1). Routes with NO prefix: `POST /intent`, `POST /advise`, `POST /feedback`. OpenAPI at `/docs`.
- `frontend/` — React + Vite + TS (U2). Vite dev server proxies `/intent`·`/advise`·`/feedback` → `http://localhost:8000` (see `frontend/vite.config.ts`), so run the backend first.

This is Windows + Git Bash. Use `.venv/Scripts/python.exe` (not `bin/`). Background launches inherit the session cwd, so pass absolute paths and do NOT re-`cd` into a dir you're already in.

## 1. Backend (:8000)

The venv already exists with deps installed. Verify then launch in the background:

```bash
cd C:/Users/kimna/anabada/advisor-backend
.venv/Scripts/python.exe -c "import fastapi, uvicorn; print('deps OK')"
# launch (run_in_background=true); cwd is already advisor-backend, so no cd:
.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000 --log-level info
```

Smoke: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/docs` → `200`.

If deps are missing: `.venv/Scripts/python.exe -m pip install -r requirements.txt`.
If no venv: `python -m venv .venv && .venv/Scripts/python.exe -m pip install -r requirements.txt`.

### Demo data & request shapes

`data/demo_fixtures.json` is UTF-8; the Windows console is cp949, so read/print it via
`.venv/Scripts/python.exe` with `encoding='utf-8'` and `ensure_ascii=False` — never the system `python`
(it raises `UnicodeDecodeError` / prints mojibake). Fixtures are keyed by the raw Korean `rawText`;
demo mode is turned on with `"demoMode": true` in the request body.

- `POST /intent` body: `{"rawText": "<demo key>", "demoMode": true}` → `{status, intent, clarification}`
- `POST /advise` body: `{"intent": <intent>, "context": {"userId":"u-sales-1","role":"Sales"}, "demoMode": true}`
  → `{resultId, ranking[], overallDecision, overallRationale, isRecommendation, evidenceChains[]}`
  - ranking items: `candidateId, assetName, candidateState (REUSE|EXTEND_EXISTING|...), reusabilityScore, evaluationStatus, sources[], rank`
- `POST /feedback` body: `{"resultId","candidateId","verdict":"useful"|"notFit"}` → `{confirmationId}`
  - Hardening: blank/whitespace `resultId`/`candidateId` → 422; verdict outside the enum → 422.

Hero scenario (first `structure` fixture key) expects `overallDecision: REUSE`, asset-001 at rank 1 (~0.92).

## 2. Frontend (:5173, may fall back)

```bash
cd C:/Users/kimna/anabada/frontend
node_modules/.bin/vite --port 5173
```

Ports 5173/5174 are often already taken by other sessions — Vite auto-falls-back (e.g. **5175**).
Read the launch log for the actual `Local: http://localhost:<port>/`; the proxy config is port-independent.

## 3. Drive it in a browser (Playwright)

`playwright` is in `frontend/node_modules`, but the chromium binary is NOT installed by default:

```bash
cd C:/Users/kimna/anabada/frontend && npx playwright install chromium
```

Then drive the full Hero flow (adjust the port to the one Vite reported). The UI is Korean; buttons:
**구조화하기** (structure intent → `/intent`), **검색 · 자문 실행** (run advise → `/advise`),
**👍 유용함** / **👎 맞지 않음** (feedback → `/feedback`). Scenario cards fill the request; the top one is Hero.

```bash
cd C:/Users/kimna/anabada/frontend && node -e "
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const reqs=[]; p.on('response', r=>{ const u=r.url(); if(/\/(intent|advise|feedback)/.test(u)) reqs.push(r.status()+' '+u.split('localhost')[1]); });
  await p.goto('http://localhost:5175/', {waitUntil:'networkidle'});
  await p.getByText('Hero - 재사용', {exact:false}).click(); await p.waitForTimeout(300);
  await p.getByRole('button', {name:'구조화하기'}).click(); await p.waitForTimeout(1000);
  await p.getByRole('button', {name:'검색 · 자문 실행'}).click(); await p.waitForTimeout(1500);
  await p.getByRole('button', {name:/유용함/}).click(); await p.waitForTimeout(800);
  await p.screenshot({path:'_run_advice.png', fullPage:true});
  console.log('network:', reqs);   // expect 200 /intent, 200 /advise, 200 /feedback
  await b.close();
})().catch(e=>{console.error('FAIL',e.message);process.exit(1)});
"
```

Then **Read `frontend/_run_advice.png`** — a real run shows the 3-candidate ranking (REUSE/EXTEND), 종합 권고,
Evidence Chain, and "기록됨 · <id>" after feedback. A blank frame = launch failed.

## 4. Cleanup

- Stop servers: find PIDs on the ports and kill them —
  `netstat -ano | grep -E ':8000|:5175' | awk '{print $5}' | sort -u` then `taskkill //PID <pid> //F`.
- `POST /feedback` appends to `advisor-backend/data/feedback.jsonl` (NOT gitignored). Delete it after a smoke run
  to keep the tree clean: `rm -f advisor-backend/data/feedback.jsonl`.
- Delete any `frontend/_run_*.png` screenshots you created.
