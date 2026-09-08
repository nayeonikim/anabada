# Unit of Work Dependency — Rebuild or Reuse Advisor

> 유닛 간 의존성 매트릭스 + 통합 방식 + 개발 순서.

---

## 의존성 매트릭스

| Depends → | U1 Advisor Backend | U2 Web UI |
|---|---|---|
| **U1 Advisor Backend** | — | (없음) |
| **U2 Web UI** | ✅ HTTP API (`/intent`, `/advise`, `/feedback`) | — |

- **방향**: U2 → U1 (단방향). U1은 U2에 의존하지 않음.
- **결합 지점**: U1이 노출하는 3개 로컬 HTTP 엔드포인트만 (Q2-A, Q6-A). 내부 파이프라인 컴포넌트(C1~C10)는 U2에 은닉.
- **공유 자원**: mock 데이터/Adapter(C9/C10)는 U1 내부에 캡슐화(Q5-A) — 유닛 간 공유 모듈 없음.

---

## 통합 계약 (개념 수준 — 상세는 Functional Design)

| Endpoint | 방향 | 요청(개념) | 응답(개념) | 스토리 |
|---|---|---|---|---|
| `POST /intent` | U2→U1 | rawText | StructuredIntent \| ClarificationRequest | US-1.1/1.2/1.3 |
| `POST /advise` | U2→U1 | approvedIntent + PermissionContext | AdviceResult(ranking, overallDecision, evidenceChains, excluded) | US-2.1~US-4.2 |
| `POST /feedback` | U2→U1 | resultId, candidateId, feedback | 기록 확인 | US-4.3 |

---

## 개발 순서 & 크리티컬 패스 (Q3-A)

```
U1 (backend) 완성  ──►  U2 (frontend) 진행
 └ per-unit 루프:                └ per-unit 루프:
   Functional → NFR-Req →           Functional → NFR-Req →
   NFR-Design → Code Gen            NFR-Design → Code Gen
```

- **크리티컬 패스**: U1이 U2를 블록. U1의 API 계약(`/intent`, `/advise`, `/feedback`)이 U2 개발의 선행 조건.
- **테스트 체크포인트**: U1 완료 시 백엔드 단위/PBT + 3 Unhappy 시나리오 검증 → U2 완료 후 통합(E2E) 검증(Build and Test 단계).
- **롤백**: Greenfield, 유닛 단위 독립성 높아 롤백 부담 낮음.
