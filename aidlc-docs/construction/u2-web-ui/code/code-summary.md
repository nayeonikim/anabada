# Code Summary — U2 Web UI (Single-Screen Advisor)

> CONSTRUCTION - Code Generation (U2) 산출 요약. 실제 코드는 워크스페이스 루트 `frontend/`.
> 근거 계획: `aidlc-docs/construction/plans/u2-web-ui-code-generation-plan.md` (fast-path, Step 0~13).
> 스택(사용자 결정): React 18 + Vite 5 + TypeScript(strict). U1 확정 3개 HTTP API에만 의존.

---

## 1. 생성 파일 목록 (`frontend/`)

### 스캐폴드/설정
| 파일 | 책임 |
|---|---|
| `package.json` | React/Vite/TS 의존성 + scripts(dev/build/typecheck/preview) |
| `vite.config.ts` | React 플러그인 + dev proxy(`/intent`·`/advise`·`/feedback` → `:8000`), `VITE_BACKEND_URL` override |
| `tsconfig.json` / `tsconfig.node.json` | strict TS 설정 |
| `index.html` / `src/main.tsx` | 진입점 + React 마운트 |
| `README.md` | 실행/데모 안내(백엔드 DEMO_MODE 포함) |

### API 계층 (`src/api/`)
| 파일 | 책임 | 스토리 |
|---|---|---|
| `types.ts` | U1 공개 DTO/enum 1:1 미러. 미인가/제외 필드 **부재**(§3.2) | 계약 |
| `client.ts` | `fetch` 래퍼 3개 + `ApiError`(공개 오류 모델 `{error:{code,message,requestId}}` 파싱) | 계약 |

### 상태/조립 (`src/`)
| 파일 | 책임 | 스토리 |
|---|---|---|
| `App.tsx` | 단일 화면 상태 흐름(intent→advise→feedback), 파생값(선택 후보/체인), 3열 레이아웃 조립 | 전체 |
| `styles.css` | 디자인 시스템(토큰 + .panel/.card/.badge/.btn/.field/.evidence-*) — 다크 테마, 반응형 | NFR-6 |
| `demo/presets.ts` | U1 `demo_fixtures.json`에서 **정확한 rawText 자동 추출**(Hero/NEEDS_REVIEW/DEVELOP/Clarify) + ROLE_OPTIONS | 데모 |

### 컴포넌트 (`src/components/`)
| 파일 | 책임 | 스토리 |
|---|---|---|
| `panel-props.ts` | 4개 패널 props 계약(presentational, 상태 미소유) | 계약 |
| `badges.ts` | enum→배지(label+class) + `evaluationLabel`(UNAVAILABLE→'평가 미완료') | 계약 |
| `IntentPanel.tsx` | 데모 프리셋 + 권한 컨텍스트 + rawText 입력 + 구조화 5필드 편집 + 명료화 질문 | US-1.1/1.2/1.3 |
| `RankingPanel.tsx` | Overall Decision 배너 + 후보 카드(순위/State/점수/lifecycle/Source) + 선택 | US-4.1 |
| `EvidencePanel.tsx` | 선택 후보 Evidence chain(출처 목록 + stateRationale), UNAVAILABLE 처리 | US-4.2 |
| `FeedbackBar.tsx` | 선택 후보 useful/notFit 피드백 + 확인 id | US-4.3 |

## 2. 스토리 ↔ 코드 트레이스
| Story | 구현 |
|---|---|
| US-1.1 자연어 입력 | IntentPanel rawText + `POST /intent` |
| US-1.2 구조 표시/확인 | IntentPanel 편집 가능 5필드(StructuredIntentDTO) |
| US-1.3 명료화 | IntentPanel clarification(질문/누락 필드) → 보완 재제출 |
| US-4.1 랭킹/종합 권고 | RankingPanel(overallBadge + 후보 카드 + 선택) |
| US-4.2 Evidence | EvidencePanel(chain.evidenceItems + rationale) |
| US-4.3 피드백 | FeedbackBar + `POST /feedback` |

## 3. 핵심 설계 계약
- **API 의존 최소화**: U1의 3개 로컬 HTTP API에만 의존. dev proxy로 CORS 우회(별도 백엔드 CORS 설정 불필요).
- **Type-Enforced Non-Disclosure 유지(§3.2)**: `types.ts`에 제외/미인가 필드가 구조적으로 없으므로 UI가 노출할 수 없음.
- **evaluationStatus 계약**: UNAVAILABLE 후보는 점수 대신 '평가 미완료' 표기(재사용성 null) — `badges.evaluationLabel`.
- **presentational 분리**: 모든 상태는 `App.tsx`가 소유, 패널은 props+콜백만 → 테스트/교체 용이.
- **데모 결정성**: 프리셋 rawText가 U1 fixture 키와 정확히 일치 → `DEMO_MODE=ON`에서 결정적 재현.

## 4. 빌드/실행 검증
- `npm install` exit 0.
- `npm run build`(= `tsc --noEmit && vite build`) **성공** — 38 modules, TypeScript strict 오류 0, dist 번들 생성(js 154.66kB / gzip 50.26kB, css 5.99kB).
- 실행: `frontend/README.md`(백엔드 `:8000` + `npm run dev` → `:5173`).

## 5. 병렬 생성 메모
4개 패널을 subagent로 병렬 생성 시도 → Bedrock IAM 정책이 sonnet inference-profile을 explicit deny(403)하여 4개 모두 실패.
공유 파운데이션에서 props/CSS/badge 계약이 이미 확정돼 있어 메인 세션이 직접 순차 작성, 최종 빌드 검증 통과.

> **주의**: 본 단계는 코드/빌드 **생성·검증**까지. 백엔드 연동 실 렌더링(4 시나리오 시각 확인)은 Build & Test / 데모 단계에서 수행.
