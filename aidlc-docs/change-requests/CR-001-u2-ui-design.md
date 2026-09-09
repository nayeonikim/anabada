# CR-001 — U2 Action Handoff UI Design (US-6.2)

**Status**: APPROVED (2026-09-09) — Q-TARGET/Q-NULL/Q-LABEL/Q-TEST 확정(§7). U2 Code Generation(증분) Part 2 진행 중.
**Stage**: CONSTRUCTION → **U2 UI Design (증분)** — U2 Code Generation *앞*의 별도 설계 게이트.
**Authoritative for**: U2 Action Handoff 표시·Copy의 상세 UI(화면 배치·정보 계층·상태·접근성).
**Supersedes(부분)**: `CR-001-u2-action-handoff-design-delta.md` 의 **D1(하단 별도 패널 배치)** — 본 문서의 탭 기반 배치로 대체. 그 외 델타 내용(계약 소비·null 처리·a11y 재사용)은 재사용.
**Base**: `integration/action-handoff-on-main` @ 최신 origin/main(`e4111ef`, Anabada 검색형 라이트 UI) 위 CR-001 백엔드 통합(`dc6c6ea`).

---

## 0. 이 단계가 왜 필요한가 (승인 범위 구분)

- CR-001 **Application Design(증분)** 에서 승인된 것은 **(D1) `/advise` 응답의 `actionHandoff` 계약**과 **"표시 책임이 U2에 있다"** 는 것뿐이다.
- **화면 어디에·어떤 정보 계층으로·각 상태를 어떻게 그릴지(UI 상세 설계)는 승인된 적이 없다.**
- 따라서 백엔드 계약 승인·표시 책임 승인을 **UI 상세 설계 승인으로 간주하지 않는다.** 본 문서가 그 UI 상세 설계이며, **별도 승인 게이트**를 거친 뒤에만 U2 Code Generation(Part 1/2)으로 진행한다.

---

## 1. 승인된 US-6.2 Acceptance Criteria (원문, `stories.md:168-175`)

- 결과 화면을 열면 Action Prompt를 표시하고 **어떤 Overall Decision에 대한 것인지** 자기설명적으로 드러낸다. (NFR-1/NFR-6)
- Copy 실행 → 전체 Prompt를 클립보드에 복사하고 **성공을 알린다("복사됨")**.
- Copy 실패 → **실패를 알리고** 수동 선택·복사 대안을 제공한다.
- Action Prompt가 없으면(생성 실패 등) → 기존 판단 결과(랭킹·Decision·Evidence)는 그대로 표시하고 **부재만 안내**한다.
- U1→U2 계약은 Advisor 결과의 Action Prompt를 소비. 구체 필드는 Application Design에서 확정(본 문서는 확정된 계약을 소비).

---

## 2. 소비할 백엔드 계약 (기 구현, 무변경)

`advisor-backend/app/api/schemas.py:77-91` — `AdviceResponse.actionHandoff: Optional[ActionPromptDTO]`

| 필드 | 타입 | 의미 | 표시 |
|---|---|---|---|
| `decisionState` | `str` | = `overallDecision` (REUSE / EXTEND_EXISTING / NEEDS_REVIEW / DEVELOP) | Decision 배지(자기설명) |
| `promptText` | `str` | Copy 대상 자연어 Prompt 전문(다행, `\n` 포함) | pre-wrap 박스 |
| `targetAssetNames` | `string[]` | REUSE/EXTEND의 접근 가능 대상 Asset명; DEVELOP/NEEDS_REVIEW → `[]` | (선택) "대상 자산" 줄 |

- **null 조건**: 생성 실패(정합 가드 위반·LLM 오류/타임아웃)에만 `actionHandoff = null`(비차단). 4개 Decision 정상 시 값 존재.
- **비노출(NFR-8)**: 페이로드는 이미 공개 투영(후보 id·미인가 자산·내부 사유 필드 구조적 부재) → U2는 받은 3필드를 **그대로 표시만** 하면 계약 충족.
- **demoMode 픽스처(무변경)**: `demo_fixtures.json` `actionHandoff` 3 시나리오(각 `promptText`만 보유, `decisionState`/`targetAssetNames`는 런타임에 overall decision으로 산출):
  - `customer overview dashboard` → REUSE, 702자 → `targetAssetNames=["Customer 360 Dashboard"]`
  - `legacy common utilities` → NEEDS_REVIEW, 516자 → `targetAssetNames=[]`
  - `release version checklist automation script` → DEVELOP, 514자 → `targetAssetNames=[]`

---

## 3. 확정된 배치 결정 (사용자 승인 2026-09-09)

- **위치: 최종 판정(`VerdictBanner`) 안, `AI 요약 답변` 박스 다음.** (결과 화면 하단 별도 패널 아님 — 초안 D1 대체)
- **표현: 배너 내 탭 스트립의 단일 탭 `✨ 추천 프롬프트`.** 기존 후보 상세 탭(`판단 근거·적합도 분석·참고 자료`)과 **동일한 탭 시각언어**(`.tabs`/`.tab`/`.tab--active`/`.tab-panel`)를 재사용. 이미지의 "배너 안 탭(버튼)" 방향과 일치.
- **범위 한정**: 배너에 `판단 근거·적합도 분석·참고 자료` 3탭을 새로 올리지 **않는다**(그건 전체 수준 재구성 → CR-001 범위 밖). CR-001에서는 `✨ 추천 프롬프트` **탭 하나만** 추가.
- **향후 확장(미포함)**: 후보별(candidate-level) 프롬프트는 백엔드 계약 확장이 필요 → **후속 이터레이션으로 연기**. 단일 탭 스트립은 향후 전체 수준 탭이 늘어날 때 자연 확장되는 구조.

정보 계층(결과 화면):

```
[← 새 질문하기]
내 질문: "고객의 Project, Forecast, Risk..."          2026. 9. 9. 13:50

┌─ 최종 판정 (verdict--{variant}) ─────────────────────────────┐
│ ✓ 최종 판정                                                   │
│ (원형 아이콘)  DECISION  [Decision 태그 badge]                │
│               summary 문장                                    │
│               sub 문장(REUSE/EXTEND & 점수 있을 때)           │
│ ┌ AI 요약 답변 ────────────────────────────────────────────┐ │
│ │ overallRationale ...                                      │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌ tabs ─────────────────────────────────────────────────────┐ │  ← 신규
│ │ [ ✨ 추천 프롬프트 ]  (활성)                                 │ │
│ ├───────────────────────────────────────────────────────────┤ │
│ │ [Decision badge]  대상 자산: ...(있으면)                    │ │
│ │ ┌ 실행 프롬프트 (pre-wrap) ───────────────────────────────┐ │ │
│ │ │ promptText 전문 (다행) ...                              │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │ [ 📋 복사 ]   ✓ 복사됨 / (실패 시) 오류 안내                 │ │
│ └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘

┌─ 추천 후보 Top N (block) ────────────────────────────────────┐
│ ① … [state badge] 92% ▾   (펼치면 판단근거·적합도·참고자료 3탭)│
│ ② … / ③ …                                                     │
└───────────────────────────────────────────────────────────────┘
```

계층 순서: **판정 → 요약(왜) → ✨ 다음 행동(실행 프롬프트) → 후보 근거 검토**. Action Handoff는 판정 배너의 **마지막 요소**(= "판단을 봤으니, 이게 다음 실행 단계") 이며 후보 리스트 위에 온다.

---

## 4. 화면 시안 (검토용 · ASCII 목업)

> 목업은 데스크톱 폭 기준. 실제 색/여백은 기존 토큰(`styles.css`)을 그대로 따른다.

### M1. REUSE (hero 프리셋) — 기본 상태 (Copy 이전)

```
┌───────────────────────────────────────────────────────────────┐
│ ● 최종 판정                                                     │
│                                                                 │
│  ⬤    REUSE   [ 기존 자산 재사용 추천 ]   ← badge--reuse(초록)   │
│  ✓    기존 Customer 360 Dashboard을(를) 재사용하는 것이 가장     │
│       적합합니다.                                                │
│       요구사항과의 높은 유사성(92%)으로 추가 개발 없이 기존       │
│       자산을 활용할 수 있습니다.                                 │
│                                                                 │
│  ┌ AI 요약 답변 ───────────────────────────────────────────┐   │
│  │ 고객의 Project, Forecast, Risk 요청사항을 통합 조회하는    │   │
│  │ 요구사항은 기존 Customer 360 Dashboard와 대부분 일치...    │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ [ ✨ 추천 프롬프트 ]‾‾‾‾‾  ← .tab--active (accent 밑줄)      │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ [ REUSE ]   대상 자산: Customer 360 Dashboard               │ │
│  │ ┌ 실행 프롬프트 ─────────────────────────────────────────┐ │ │
│  │ │ 【목표】                                                 │ │ │
│  │ │ 기존 사내 자산 'Customer 360 Dashboard'를 활용·재사용... │ │ │
│  │ │ 【다음 작업】                                            │ │ │
│  │ │ 1) ... 2) ... 3) ...                                    │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │ [ 📋 복사 ]                                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### M2. Copy 성공 / 실패

```
성공(클릭 후):
   [ 📋 복사 ]   ✓ 복사됨          ← .confirmation role="status" (초록)

실패(clipboard 거부·미지원):
   [ 📋 복사 ]   ⚠ 복사에 실패했습니다. 아래 프롬프트를 직접
                 선택해 복사해 주세요.   ← .error-text role="alert" (빨강)
   (프롬프트 박스는 텍스트 선택 가능 → 수동 복사 대안)
```

### M3. NEEDS REVIEW — 앰버, 대상 자산 없음, "다음 검토" 성격

```
┌───────────────────────────────────────────────────────────────┐
│  ⬤(!)  NEED REVIEW  [ 추가 검토 필요 ]  ← badge--review(앰버)   │
│        (참고용 · 확정 권고 아님)   ← isRecommendation=false      │
│        판단을 확정하기 전에 추가 검토가 필요합니다. 후보를 살펴보세요.│
│  ┌ AI 요약 답변 ─────────────────────────────────────────────┐ │
│  │ ...                                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ [ ✨ 추천 프롬프트 ]                                         │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ [ NEEDS REVIEW ]      ← 대상 자산 줄 없음(targetAssetNames=[])│ │
│  │ ┌ 실행 프롬프트 ─────────────────────────────────────────┐ │ │
│  │ │ '...'를 재사용 가능한 판단으로 확정하기 전에, 다음 추가   │ │ │
│  │ │ 근거를 확인하세요: ...                                   │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  │ [ 📋 복사 ]                                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

- NEEDS REVIEW·DEVELOP는 **앰버/보라 배지 + 대상 자산 줄 생략**으로 REUSE/EXTEND(초록/파랑 + 대상 자산 명시)와 시각적으로 구분된다.
- 배지 색은 `VerdictBanner`·후보 배지와 **동일 팔레트**(review=앰버, develop=보라) → 화면 전체에서 일관.
- NEEDS REVIEW의 프롬프트는 "실행"이라기보다 "다음 검토 단계"를 안내(백엔드 promptText가 그 성격으로 생성됨). 배지 + `(참고용 · 확정 권고 아님)` 컨텍스트가 이를 프레이밍. (라벨을 "다음 단계"로 바꿀지는 §7 Q-LABEL.)

### M4. DEVELOP — 보라, 대상 자산 없음

```
│  ⬤(+)  DEVELOP  [ 신규 개발 권장 ]   ← badge--develop(보라)     │
│  ┌ ✨ 추천 프롬프트 ─────────────────────────────────────────┐ │
│  │ [ DEVELOP ]      (대상 자산 줄 없음)                        │ │
│  │ ┌ 실행 프롬프트 ─── 신규 개발 착수 가이드 ...──────────────┐ │ │
│  │ [ 📋 복사 ]                                                 │ │
```

### M5. Prompt 부재 (actionHandoff = null) — AC5

```
┌─ 최종 판정 ───────────────────────────────────────────────────┐
│  ⬤   REUSE  [ 기존 자산 재사용 추천 ]                           │
│  ┌ AI 요약 답변 ─────────────────────────────────────────────┐ │
│  │ ...(정상 렌더)                                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ⓘ 실행 프롬프트를 생성하지 못했습니다. 위 판단 결과(판정·요약)   │  ← 흐린 텍스트,
│    와 아래 후보·근거는 그대로 유효합니다.                        │    탭/패널 없음
└───────────────────────────────────────────────────────────────┘
[추천 후보 Top N ... 정상 렌더]
```

- **[Q-NULL 확정 override]** `actionHandoff == null` → **탭 스트립은 그대로 유지**하고, `✨ 추천 프롬프트` **패널 안**에 부재 안내(`.handoff-note`)만 표시한다. 판정·요약·후보·근거는 App/VerdictBanner가 독립 렌더하므로 그대로 유지(비차단). (위 M5 ASCII는 초안이며, 실제 구현은 §5.3 의사설계 + §7 확정을 따른다.)

### M6. 반응형 (≤ 720px)

```
┌─ 최종 판정 ─────────────────┐
│ ⬤  REUSE                    │  ← .verdict-body flex-direction:column
│ [ 기존 자산 재사용 추천 ]     │    (기존 @media 규칙 재사용)
│ summary ...                  │
│ ┌ AI 요약 답변 ───────────┐ │
│ └──────────────────────────┘ │
│ ┌ ✨ 추천 프롬프트 ───────┐ │
│ │ [REUSE]                  │ │
│ │ 대상 자산: Customer 360  │ │  ← 긴 이름/버튼·상태는
│ │ Dashboard                │ │    flex-wrap 으로 줄바꿈
│ │ ┌ 실행 프롬프트 ───────┐ │ │
│ │ │ pre-wrap 자동 줄바꿈  │ │ │
│ │ └────────────────────────┘ │ │
│ │ [ 📋 복사 ]              │ │
│ │ ✓ 복사됨                 │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

---

## 5. 컴포넌트 설계 (구현 대상 — 코드 생성 계획 정합화용)

### 5.1 데이터 흐름
```
App (App.tsx:187)
  advice.actionHandoff  ─prop→  <VerdictBanner handoff={advice.actionHandoff ?? null} .../>
                                     └─ AI 요약 답변 다음 ─→ <ActionHandoffTab handoff={handoff}/>
```

### 5.2 신규/변경
| 파일 | 변경 | 내용 |
|---|---|---|
| `frontend/src/api/types.ts` | 추가 | `ActionPromptDTO`(3필드) + `AdviceResponse.actionHandoff?: ActionPromptDTO \| null`. 백엔드 camelCase 1:1 미러. |
| `frontend/src/components/ActionHandoffTab.tsx` | **신규** | 배너 내부에 렌더되는 작은 프레젠테이셔널 컴포넌트. Props `{ handoff: ActionPromptDTO \| null }`. Copy 상태 **로컬** `useState<'idle'\|'copied'\|'failed'>`(서버 왕복 없음 → App 전역 상태 미오염). Decision→variant 로컬 맵(`CandidateList.tsx:246-259`와 동일 4줄, 관심사 분리 위해 소규모 중복 허용). |
| `frontend/src/components/VerdictBanner.tsx` | 편집 | props에 `handoff` 추가. `.ai-answer` 블록 **다음**에 `<ActionHandoffTab handoff={handoff}/>` 1줄 렌더. 그 외 로직 무변경. |
| `frontend/src/App.tsx` | 편집 | `<VerdictBanner ... handoff={advice.actionHandoff ?? null} />` 로 prop 1개 전달(신규 import 없음 — ActionHandoffTab은 VerdictBanner가 import). |
| `frontend/src/styles.css` | 최소 | 기존 클래스 재사용. 필요 시 소형 규칙 **최대 1개**(예: `.handoff-actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:14px;}`). 신규 토큰/색상 금지. |

### 5.3 `ActionHandoffTab` 렌더 규칙 (의사설계)
```
// 탭 스트립은 null/비-null 공통으로 항상 렌더 (Q-NULL 확정: 탭 내부 안내). 루트 = <div class="handoff">.
<div class="handoff">
  <div class="tabs" role="tablist">
    <button class="tab tab--active" role="tab" aria-selected="true"
            aria-controls="handoff-panel" id="handoff-tab">✨ 추천 프롬프트</button>
  </div>
  <div class="tab-panel" role="tabpanel" id="handoff-panel" aria-labelledby="handoff-tab">

    handoff == null  →  <p class="handoff-note">실행 프롬프트를 생성하지 못했습니다.
                          위 판단 결과(판정·후보·근거)는 그대로 유효합니다.</p>   // 부재 안내(패널 내부)

    handoff != null  →  <div class="handoff-meta">
                          <span class="badge badge--{variant(decisionState)}">{decisionState}</span>
                          {targetAssetNames.length>0 &&                              // Q-TARGET: []이면 숨김
                             <span class="handoff-target">대상 자산: {join(' · ')}</span>}
                        </div>
                        // Q-LABEL: NEEDS_REVIEW 는 검토용임을 명시, 개발 실행 유도 문구 금지
                        <p class="handoff-note">
                           decisionState==='NEEDS_REVIEW'
                             ? '판단 확정을 위한 검토용 프롬프트입니다. 후보와 근거를 먼저 검토하세요.'
                             : '복사해 외부 AI 도구에 붙여넣어 사용할 수 있습니다.'</p>
                        <div class="ai-answer"><p class="ai-answer-label">추천 프롬프트</p>   // '실행'→'추천'
                             <p class="ai-answer-text">{promptText}</p></div>          // pre-wrap, 선택 가능
                        <div class="handoff-actions">
                           <button class="btn btn--sm" onClick={copy}>📋 복사</button>
                           copied  → <span class="confirmation" role="status">복사됨</span>
                           failed  → <span class="error-text" role="alert">복사 실패 안내 + 수동 대안</span>
                        </div>
  </div>
</div>
```
- Copy: `navigator.clipboard.writeText(handoff.promptText)` → then `copied`; catch → `failed`. 신규 의존성 0(브라우저 Clipboard API, secure context=localhost 데모 OK).

---

## 6. 접근성 & 반응형 (NFR-2 계승)

| 항목 | 처리 | 근거(기존 재사용) |
|---|---|---|
| Copy 버튼 키보드 | 네이티브 `<button>` → Tab 포커스 + Enter/Space 실행 | `.btn:focus-visible` 아웃라인 이미 정의(`styles.css:991`) |
| 탭 포커스 | `.tab` 네이티브 button + `.tab:focus-visible` | `styles.css:990` |
| 복사 성공 알림 | `role="status"`(polite live) "복사됨" | 피드백 `confirmation`과 동일(`CandidateList.tsx:231`) |
| 복사 실패 알림 | `role="alert"`(assertive) + 수동 선택 대안 | 피드백 오류와 동일(`CandidateList.tsx:236`) |
| 아이콘 | `✨`,`📋`,`✓` 는 `aria-hidden`, 의미는 텍스트 병행 | 기존 이모지 규칙 |
| 색상 의존 금지 | Decision은 배지 **텍스트(REUSE 등)** + 색 병행 | 기존 배지 규칙 |
| 반응형 | `.verdict-body` column(≤720), `.handoff-actions` flex-wrap, promptText pre-wrap 자동 줄바꿈, `.verdict-main{min-width:0}` 오버플로 방지 | `styles.css:999-1011` |
| 탭 시맨틱 | 단일 탭 `role=tablist/tab(aria-selected=true)/tabpanel(aria-labelledby)` — 유효. 향후 탭 확장 시 그대로 성장 | 후보 상세 탭 패턴 |

---

## 7. 열린 결정 — **확정 (2026-09-09, 사용자 승인)**

- **Q-TARGET = 표시**: `targetAssetNames`를 "대상 자산" 줄로 표시하되 **빈 배열이면 숨김**(DEVELOP/NEEDS_REVIEW는 자연히 미표시).
- **Q-NULL = 탭 내부 안내**: 부재(null)에도 `✨ 추천 프롬프트` **탭을 유지**하고 **패널 안에** 부재 안내를 표시. 기존 판정·후보·근거는 그대로 유효(비차단). → 초안 §4 M5의 "탭 없이 배너 하단 1줄" 은 **override**됨.
- **Q-LABEL**: 탭 제목은 **`✨ 추천 프롬프트`로 통일**. 내부 박스 라벨은 '실행 프롬프트' → **'추천 프롬프트'**로 조정. **NEEDS_REVIEW** 는 "판단 확정을 위한 검토용 프롬프트입니다. 후보와 근거를 먼저 검토하세요." 로 검토 성격을 명시. **개발 실행을 유도하는 문구(명령형 CTA)는 사용하지 않음.**
- **Q-TEST = 신규 하네스 생략**: 검증은 `tsc(strict) + vite build` + **스모크**(Decision 4종 REUSE·EXTEND_EXISTING·DEVELOP·NEEDS_REVIEW, Copy 성공/실패, null, 모바일(≤720px), 키보드 접근성). 신규 테스트 프레임워크 도입 없음(NFR-minimization).

> 배치(Q1)는 §3에서 이미 확정: 최종 판정 배너 내 `✨ 추천 프롬프트` 단일 탭.

---

## 8. 영향 범위 / 비회귀

- 변경: `types.ts`(+2), 신규 `ActionHandoffTab.tsx`, `VerdictBanner.tsx`(+prop, +1 렌더 줄), `App.tsx`(+prop 1), `styles.css`(0~1 규칙).
- API/DTO/기존 컴포넌트 계약·기존 흐름(home↔result, clarify, error, feedback, 후보 3탭) **무영향** → U1 회귀 없음.
- NFR-minimization: 신규 config/flag/의존성 0, 신규 테스트 프레임워크 0.
