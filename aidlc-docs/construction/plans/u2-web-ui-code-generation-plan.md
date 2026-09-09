# U2 Web UI — Code Generation Plan (fast-path)

> CONSTRUCTION - Code Generation (U2). 사용자 결정: U1 승인 후 U2 즉시 착수, 설계 단계 압축(fast-path), 가능 시 병렬 코드 생성.
> 근거: `inception/application-design/unit-of-work.md`(U2 정의), U1 확정 API 계약(`advisor-backend/app/api/schemas.py`, `main.py`), NFR-6(단일 화면).
> 스택 결정(사용자): **React + Vite + TypeScript**. Vite dev proxy로 `/intent`·`/advise`·`/feedback` → `http://localhost:8000`(CORS 우회).

## Fast-path 근거
U2는 U1의 확정된 3개 HTTP API와 공개 DTO에만 의존하는 단일 화면 thin presentational UI다.
새 도메인/비즈니스 로직·NFR 패턴·인프라 프로비저닝이 없으므로 Functional/NFR/Infra 설계 단계 산출물은
application-design + U1 API 계약을 재사용하고 Code Generation에 집중한다(사용자 승인 하 압축).

## API 계약 (U1, 고정)
- `POST /intent`  {rawText} → {status: "structured"|"clarification", intent?, clarification?}
- `POST /advise`  {intent(5필드), context{userId,role}} → {resultId, ranking[], overallDecision, overallRationale, isRecommendation, evidenceChains[]}
- `POST /feedback` {resultId, candidateId, verdict: "useful"|"notFit"} → {confirmationId}
- ⚠️ 미인가/제외 정보는 응답 DTO에 구조적으로 부재(§3.2) — UI도 노출 안 함.

## 병렬화 전략
1. **공유 파운데이션(직렬, 메인)**: 스캐폴드 + `api/types.ts`(DTO 미러) + `api/client.ts` + `styles.css`(디자인 토큰/클래스) + `components/panel-props.ts`(패널 props 계약) + `App.tsx`(상태 흐름/조립) + `demo/presets.ts`.
2. **팬아웃(병렬 에이전트)**: 서로 독립인 4개 presentational 패널을 계약(props + CSS 클래스명 + enum→배지 매핑)에 맞춰 병렬 생성.
   - IntentPanel / RankingPanel / EvidencePanel / FeedbackBar

## 실행 체크리스트
- [x] Step 0: 계획 문서 작성(본 파일)
- [x] Step 1: 프로젝트 스캐폴드(package.json, vite.config.ts, tsconfig*, index.html, main.tsx)
- [x] Step 2: `api/types.ts` — 공개 DTO/enum 미러
- [x] Step 3: `api/client.ts` — fetch 래퍼 + 오류 처리(공통 오류 모델 `{error:{code,message,requestId}}`)
- [x] Step 4: `styles.css` — 디자인 토큰 + 공유 클래스(.panel/.card/.badge/.btn/.field ...)
- [x] Step 5: `components/panel-props.ts` — 4개 패널 props 계약 + `components/badges.ts` 헬퍼
- [x] Step 6: `App.tsx` — 상태 흐름(intent→advise→feedback), context 바, 데모 프리셋, 패널 조립
- [x] Step 7: `demo/presets.ts` — U1 demo_fixtures 정확한 rawText 프리셋(4 시나리오, 자동 추출)
- [x] Step 8: IntentPanel.tsx  *(병렬 에이전트 sonnet 403 인증 거부로 실패 → 메인이 직접 작성)*
- [x] Step 9: RankingPanel.tsx  *(동상)*
- [x] Step 10: EvidencePanel.tsx  *(동상)*
- [x] Step 11: FeedbackBar.tsx  *(동상)*
- [x] Step 12: `npm install`(exit 0) + `npm run build`(tsc --noEmit + vite build) → **성공, 38 modules, 오류 0**
- [x] Step 13: code-summary.md(U2) 작성 + state/audit 갱신

## 병렬화 결과 메모
공유 파운데이션(직렬)은 계획대로 완성. 4개 패널 팬아웃은 subagent(sonnet)로 시도했으나
Bedrock IAM 정책이 sonnet inference-profile을 explicit deny(403)하여 4개 모두 실패 →
계약(props/CSS/badge)이 이미 확정돼 있어 메인 세션이 직접 순차 작성. 최종 빌드 검증 통과.

## 스토리 트레이스
US-1.1(입력), US-1.2(구조 표시/확인), US-1.3(명료화), US-4.1(랭킹), US-4.2(Evidence), US-4.3(피드백).
