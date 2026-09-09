# Unit of Work Story Map — Rebuild or Reuse Advisor

> 스토리 ↔ 유닛 매핑. 모든 스토리가 유닛에 할당되었는지 검증.

---

## 전체 매핑

| Story | 태그 | U1 Advisor Backend | U2 Web UI | 비고 |
|---|---|---|---|---|
| US-1.1 자연어 Intent 입력 | MVP·Hero | ✅ 접수/전달 | ✅ 입력 UI | 입력 UI(U2) + 접수(U1) |
| US-1.2 Intent 구조화 | MVP·Hero | ✅ C1 구조화 | ✅ 구조 표시/확인 | |
| US-1.3 모호 의도 추가질문·승인 | MVP | ✅ C1 명료화 로직 | ✅ 명료화 질문 UI | |
| US-2.1 Multi-Source 검색 | MVP·Hero | ✅ C2/C9/C10 | — | 백엔드 전용 |
| US-2.2 권한 필터 후 Top-N | MVP·Hero·Unhappy | ✅ C3/C4 | — | 백엔드 전용 |
| US-3.1 LLM 재검증 | MVP·Hero | ✅ C5 | — | 백엔드 전용 |
| US-3.2 Candidate State 분류 | MVP·Hero | ✅ C6 | — | 백엔드 전용 |
| US-3.3 근거 부족 → NEEDS REVIEW | MVP·Unhappy | ✅ C6 | — | 백엔드 전용 |
| US-3.4 적합 없음 → Overall DEVELOP | MVP·Unhappy | ✅ C6 | — | 백엔드 전용 |
| US-4.1 후보 랭킹 결과 화면 | MVP·Hero | ✅ AdviceResult 제공 | ✅ 랭킹/Overall 화면 | 화면 주도(U2) |
| US-4.2 후보별 Evidence Chain | MVP·Hero | ✅ C7 구성 | ✅ Evidence 표시 | |
| US-4.3 결과 피드백 수집 | MVP | ✅ C8 기록 | ✅ 피드백 UI | 선별 반영은 Later |
| US-6.1 Action Prompt 생성 *(CR-001)* | MVP·Hero | ✅ C11 + AdviceResult.actionPrompt | — | 백엔드 전용(생성·grounding·비차단) |
| US-6.2 Action Prompt 표시 & Copy *(CR-001)* | MVP·Hero | ✅ `/advise` 응답 actionHandoff 제공 | ✅ 표시 + Copy(성공/실패) + 부재 안내 | 화면 주도(U2) |
| US-5.1 가중치·전략 최적화 | Later | ✅ (Later 위치) | — | MVP 밖 |
| US-5.2 실제 Source & SSO 연동 | Later | ✅ (Later, Adapter 교체) | ✅ (SSO UI, Later) | MVP 밖 |

---

## 할당 검증

- **총 스토리**: 15 (US-1.1~US-4.3 MVP 11 + **US-6.1/US-6.2 MVP 2 [CR-001 증분]** + US-5.1/US-5.2 Later 2).
- **미할당 스토리**: 없음 ✅ — 모든 스토리가 U1 및/또는 U2에 매핑됨.
- **CR-001 증분(Action Handoff)**: US-6.1(U1 C11 단독) / US-6.2(U1 데이터 + U2 표시·Copy). 유닛 경계(2 units) 불변 — Units Generation SKIP. 상세: `change-requests/CR-001-application-design-delta.md`.
- **경계 원칙 준수**:
  - 순수 백엔드 판단 로직(US-2.1~US-3.4) → U1 단독.
  - 사용자 상호작용/표현(US-1.1 입력, US-4.1 화면, US-4.3 UI) → U1(데이터)+U2(표현) 협업.
  - Later 스토리는 삭제하지 않고 소속 유닛에 비전 위치로 표시(US-5.x).
- **MVP 완료 정의**: U1(US-1.1~US-4.3 백엔드) + U2(US-1.1/1.2/1.3/4.1/4.2/4.3 화면) → Hero + 3 Unhappy 시나리오 E2E 동작.
