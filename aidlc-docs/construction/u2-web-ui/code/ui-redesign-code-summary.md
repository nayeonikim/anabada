# Code Summary — Anabada UI 재디자인 (U2 Web UI)

**작성일**: 2026-09-09 · **범위**: `frontend/` 프론트엔드 재스킨 · **결과**: tsc strict 0 오류 · vite build 40 modules · 홈/결과 화면 시각 검증 완료(Playwright, 백엔드 mock)

## 변경 파일

### 신규
- `src/components/Header.tsx` — 상단바(브랜드 Anabada + 계정 칩 "DevRel", 장식/홈 복귀)
- `src/components/SearchHome.tsx` — 화면1 검색 홈(제목/서브카피/pill 검색바/예시칩3/그라데이션/푸터)
- `src/components/ProgressSteps.tsx` — AI 진행 스텝바(4단계 + %, role=status/aria-live)
- `src/components/VerdictBanner.tsx` — 대형 판정 배너(원형 체크 + 판정 + 태그 + 요약 + AI 요약 답변)
- `src/components/CandidateList.tsx` — 추천 후보 Top N + 카드(펼침) + 3탭(판단 근거/적합도 분석/참고 자료) + 피드백
- `src/demo/examples.ts` — 예시 질문 칩 매핑(DEMO_PRESETS 재사용, fixture 정합)

### 수정
- `src/App.tsx` — 전면 재작성. view(home/result) 상태 전환 + `/intent`→`/advise` 자동 오케스트레이션(runSearch), phase 기반 진행률, 피드백 핸들러. 권한 컨텍스트 단일 지점(SSO 확장 주석).
- `src/styles.css` — 라이트 테마 디자인 시스템 전면 재작성(판정 색상 팔레트 유지, :focus-visible 이관).
- `index.html` — title → "Anabada — AI Knowledge Assistant".

### 삭제(구 3컬럼 대시보드)
- `src/components/IntentPanel.tsx`, `RankingPanel.tsx`, `EvidencePanel.tsx`, `FeedbackBar.tsx`, `panel-props.ts`

### 재사용(불변)
- `src/api/client.ts`, `src/api/types.ts`(DTO), `src/components/badges.ts`, `src/demo/presets.ts`

## 설계 결정 반영 (requirements D1~D9)
- D1 완전 교체 / D2 자동 intent→advise(clarification만 노출) / D3 스텝바 90%→100% / D4 role 기본값 고정·비노출 + 계정 "DevRel" / D5 상태 기반 전환(router 미추가) / D6 3탭 매핑 / D7 Anabada 리브랜딩(코드 식별자 유지) / D8 확장 설정 유지 / D9 데스크톱 전용.

## 검증
- `npm run build`(tsc --noEmit strict + vite build) 성공, 신규 의존성 0(런타임).
- Playwright로 홈/결과 화면 렌더 캡처 확인(임시 스크립트, 커밋 제외). 목표 목업과 시각적으로 일치.
- API 계약(`/intent`·`/advise`·`/feedback`)·DTO 불변 → U1 백엔드 회귀 없음.

## 참고 / 데모 주의
- demoMode에서 결정적 응답을 위해 예시 칩은 `DEMO_PRESETS.rawText`(fixture 키 정확 일치)를 사용. 자유 입력 질문은 실백엔드/LLM 경로.
- 계정 표시 "DevRel"은 로그인 persona(장식); `/advise` 기능 role 기본값은 유효 role(`Sales`), 예시 칩은 preset.role로 override.
