# Workflow Plan — UI 재디자인 (Anabada 검색형 라이트 UI)

**작성일**: 2026-09-09 · **범위**: U2 Web UI(`frontend/`) 단일 유닛 · **복잡도**: Moderate

## 실행 단계 결정

| 단계 | 실행? | 근거 |
|------|-------|------|
| Workspace Detection | ✅ 완료 | 기존 상태 재개, brownfield 변경 |
| Reverse Engineering | ⏭️ SKIP | 자체 작성 코드 + 완전한 설계 아티팩트 보유 |
| Requirements Analysis | ✅ 완료·승인 | `ui-redesign-requirements.md` |
| User Stories | ⏭️ SKIP | 기존 사용자 기능의 재스킨. 요구사항·목업·색상/데이터 계약이 명확하여 스토리가 추가 가치 없음. 기존 US-1.x/US-4.x 스토리를 화면에 재배치할 뿐 신규 유저 여정 없음 |
| Workflow Planning | ✅ 이 문서 | ALWAYS |
| Application Design | ✅ Minimal | 신규 UI 컴포넌트/상태 흐름 정의 필요 (도메인/비즈니스 규칙 변경 없음) |
| Units Generation | ⏭️ SKIP | 단일 유닛(U2)만 대상 |
| **Construction** | | |
| Functional Design | ⏭️ SKIP | 신규 도메인/데이터 모델/비즈니스 로직 없음. U1 API 계약·DTO 재사용 |
| NFR Requirements | ⏭️ SKIP | 신규 NFR 없음. 기존 tech-stack·성능·접근성 기준 재사용 |
| NFR Design | ⏭️ SKIP | 상동 |
| Infrastructure Design | ⏭️ SKIP | mock/정적 프론트, 인프라 변경 없음 |
| Code Generation | ✅ 실행 | 실제 재디자인 구현(핵심 작업) |
| Build and Test | ✅ 실행 | tsc strict + vite build + 통합 회귀 |
| Operations | ⏭️ placeholder | — |

## 실행 순서 (흐름)

```
Requirements(완료) -> Workflow Planning(이 문서) -> Application Design(Minimal)
  -> Code Generation(구현) -> Build and Test -> Commit & Push
```

## 위험/주의

- **데모 fixture 정합**: demoMode는 `rawText`가 fixture 키와 정확히 일치해야 결정적 응답. 예시 질문 칩은 목업의 시각 구조를 따르되, 동작 보장을 위해 칩 텍스트는 실제 `DEMO_PRESETS.rawText`를 사용(백엔드 out-of-scope).
- **판정 색상/접근성 회귀 금지**: `badges.ts` 로직·`:focus-visible`·`aria-*`를 신규 컴포넌트에 이관.
- **API 계약 불변**: `/intent`·`/advise`·`/feedback` 및 DTO 변경 없음.
