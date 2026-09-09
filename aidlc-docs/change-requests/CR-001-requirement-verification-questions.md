# CR-001 Action Handoff — Requirement Verification Questions (Minimal delta)

> AI-DLC Requirements Analysis (Minimal depth) 게이트.
> **RESOLVED (2026-09-09)**: 사용자 응답 **"전부 권장"** → Q1=A, Q2=A, Q3=A, Q4=A, Q5=A, Q6=A.
> (근거: `inception/requirements-analysis.md` Step 6, `common/question-format-guide.md`)
>
> **참고 — 이미 확정되어 질문하지 않은 항목**: 흐름 위치(Evidence 직후 append-only), Decision 4종별 목적, MVP 범위(생성+표시+Copy), 범위 밖(자동 실행/수정/commit·PR 없음).
> **설계로 미룬 항목**: Prompt 생성 방식(LLM vs 템플릿), 엔드포인트 형태(`/advise` 확장 vs 신규) 등은 Application/Functional/NFR Design에서 결정.

---

## Q1. Action Prompt 생성 **단위**
- **A) Overall Decision 기준 단일 Prompt 1개** (Recommended) — 요청 전체의 Overall Decision + 근거 Evidence로 한 개 생성. 단순·단일 화면 적합.
- **B) 후보별 Prompt** — 랭킹의 각(상위) 후보마다.
- **C) Overall 1개 + 사용자가 선택한 후보 on-demand 추가.**
- **X) Other**

[Answer]: A

---

## Q2. Prompt이 겨냥하는 **다음 workflow / 형식**
- **A) 도구 비종속(tool-agnostic) 일반 텍스트 Prompt** (Recommended) — 어떤 AI-assisted dev 도구에도 붙여넣기 가능한 자연어 Prompt.
- **B) AI-DLC 재진입 형식** (Role/Goal/Function/Data/Output 구조 포함).
- **C) 특정 Coding Agent 형식.**
- **X) Other**

[Answer]: A

---

## Q3. Prompt **언어**
- **A) 사용자 Intent 입력 언어를 따름** (Recommended) — 기본 한국어, 기술용어 영문 혼용.
- **B) 항상 한국어.**
- **C) 항상 영어.**
- **X) Other**

[Answer]: A

---

## Q4. **NEEDS REVIEW** Review Prompt의 적용 레벨
- **A) Overall Decision = NEEDS REVIEW일 때 Review Prompt 산출** (Recommended, Q1=A와 일관).
- **B) 후보별 NEEDS REVIEW에도 각각.**
- **X) Other**

[Answer]: A

---

## Q5. Extension 설정 **유지 여부** (delta 적용)
기존 확정: **Security = No, Resiliency = No, Property-Based Testing = Partial**(순수 로직 한정).
- **A) 그대로 유지** (Recommended) — Action Prompt의 Decision→목적 매핑/선택 로직이 순수 함수면 PBT Partial 대상.
- **B) 변경.**
- **X) Other**

[Answer]: A

---

## Q6. evidence-grounding **비노출 규칙** 확정
Action Prompt는 **결과에 실제 존재하는 Decision·Evidence·접근 가능 Candidate만** 근거로 하며, 미인가·제외 후보·평가 미완료(UNAVAILABLE)·내부 기술사유는 근거·노출하지 않는다(§3.2 Non-Disclosure 확장, 근거 밖 생성 금지).
- **A) 확정** (Recommended).
- **X) Other**

[Answer]: A
