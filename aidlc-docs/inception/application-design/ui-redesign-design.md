# Application Design (Minimal) — Anabada UI 재디자인

**작성일**: 2026-09-09 · **대상**: U2 Web UI(`frontend/src`)
**원칙**: presentational 컴포넌트 + App 상태 소유(기존 패턴 유지), router 미추가, 신규 의존성 0.

## 1. 화면 흐름 (상태 기반)

```
App state: view ∈ {home, result}
home  --(검색 제출)-->  result (자동 /intent -> /advise 오케스트레이션)
result --("← 새 질문하기")-->  home (입력·결과 리셋)
```

## 2. 컴포넌트 구조

| 컴포넌트 | 역할 | 상태 |
|----------|------|------|
| `App.tsx` | 상태 소유 + 오케스트레이션(runSearch), view 전환 | 신규 재작성 |
| `components/Header.tsx` | 상단바: "Anabada" 브랜드 + 계정 칩 "DevRel ▾"(장식) | 신규 |
| `components/SearchHome.tsx` | 화면1: 제목/서브카피/pill 검색바/예시칩3/그라데이션/푸터 | 신규 |
| `components/ProgressSteps.tsx` | AI 진행 스텝바(4단계 + %) | 신규 |
| `components/VerdictBanner.tsx` | 대형 판정 배너(원형 체크+판정+태그+요약)+AI 요약 박스 | 신규 |
| `components/CandidateList.tsx` | "추천 후보 Top N" + 카드(펼침) + 3탭 상세 + 피드백 | 신규 |
| `components/badges.ts` | 판정/lifecycle/점수 매핑 | **재사용** |
| `api/*`, `api/types.ts` | 백엔드 클라이언트/DTO | **재사용(불변)** |
| `demo/presets.ts` | 예시 칩 매핑용 프리셋 | **재사용** |
| ~~IntentPanel/RankingPanel/EvidencePanel/panel-props~~ | 구 3컬럼 대시보드 | **삭제** |
| `components/FeedbackBar` | 피드백 | CandidateList에 통합 흡수(파일 삭제) |

## 3. App 상태 & 오케스트레이션 (D2/D3)

```
view: 'home'|'result'
question: string           // 표시용 '내 질문'
phase: 'idle'|'understanding'|'searching'|'analyzing'|'done'|'clarify'|'error'
context: {userId:'demo-user', role:'Sales'(기본, 칩이 override)}
intent, clarification, advice, selectedCandidateId, error
feedback: confirmationId/submitting/error

runSearch(rawText, ctx):
  view=result; question=rawText; reset; phase='understanding'
  intentRes = await /intent(rawText)
    clarification -> phase='clarify' (추가질문 UI), 중단
    structured    -> phase='searching' -> (짧은 지연) phase='analyzing'(90%)
                     advice = await /advise({intent, context}); phase='done'(100%)
                     선택 후보 = rank===1
  오류 -> phase='error'
```

- **진행률(D3)**: phase→percent 목표(understanding 25 / searching 55 / analyzing 90 / done 100), CSS width transition으로 부드럽게. `/advise` 대기 중 90% 유지.
- **clarification(D2)**: `/intent`가 clarification이면 그때만 추가 질문 UI 노출(누락필드+질문). 사용자가 질문 보완 후 재검색.

## 4. 권한 컨텍스트 (D4)

- Header 계정 표시 = **"DevRel"**(로그인 persona/이름 표시, 장식). 목업 "김지훈님"의 대체.
- `/advise` context.role 기능 기본값 = 유효 role(`Sales`), 예시 칩은 preset.role로 override(fixture 정합).
- **확장 지점**: `context`는 App 단일 지점에서 생성 → 향후 SSO 로그인 시 이 지점에서 실제 사용자 role 주입(주석 명시).

## 5. 후보 상세 탭 매핑 (D6)

| 탭 | 데이터 소스 |
|----|-------------|
| 판단 근거 | `evidenceChains[cid].stateRationale` (+ 판정 배지) |
| 적합도 분석 | `reusabilityScore`(%)·`evaluationStatus`·`candidateState`·`lifecycleStatus`·`capabilityMatch` |
| 참고 자료 | `evidenceChains[cid].evidenceItems[]` (source/type/title/sourceRef) |

- 데이터 없음 시 "표시할 정보가 없습니다" 안내(비파괴적).
- 피드백(👍유용함/👎맞지 않음)은 펼친 후보 하단에 배치 → `/feedback({resultId, candidateId, verdict})`.

## 6. 디자인 토큰 (라이트 테마, NFR-1)

- `--bg:#f5f7fb` 계열 밝은 배경, `--surface:#ffffff`, `--text:#1b2536`, `--text-dim:#5a6b85`, `--border:#e6ebf3`, 파스텔 그라데이션 장식, 부드러운 그림자(`0 8px 30px rgba(20,40,80,.08)`), 큰 radius(pill/카드).
- **판정 색상 불변**: reuse #2ecc8f / extend/accent #4f8cff / review #f5a623 / develop #b06cff (라이트 배경용 배경 알파만 재조정).

## 7. 접근성 이관 (NFR-2)

`:focus-visible` 아웃라인, 카드/탭/칩 키보드 조작(role/tabIndex/Enter·Space), 진행/피드백 상태 `role="status"`·`aria-live`, 이모지 `aria-hidden`, 색상+텍스트 병행.
