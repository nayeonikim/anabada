# Reuse Advisor Backend (U1)

사내 자산(Asset) 재사용 권고 백엔드. 사용자의 자연어 의도를 구조화하고, Multi-Source
Evidence 기반으로 후보 자산을 검색·권한 필터링·재검증(LLM)하여 **REUSE / EXTEND_EXISTING /
NEEDS_REVIEW / DEVELOP** 권고와 근거(Evidence Chain)를 제공한다.

- 아키텍처/설계 근거: `aidlc-docs/construction/u1-advisor-backend/`
- 생성 요약: `aidlc-docs/construction/u1-advisor-backend/code/code-summary.md`

## 요구 사항
- Python 3.11+

## 설치
```bash
cd advisor-backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 실행
```bash
# 기본 demoMode=ON (결정적 fixture, Bedrock 불필요)
uvicorn app.main:app --reload --port 8000
```
- OpenAPI 문서: http://localhost:8000/docs

### 논리 엔드포인트
| Method | Path | 설명 |
|---|---|---|
| POST | `/intent` | rawText → StructuredIntent 또는 ClarificationRequest |
| POST | `/advise` | 승인된 intent + PermissionContext → AdviceResult(랭킹·권고·Evidence) |
| POST | `/feedback` | (resultId, candidateId, verdict) 기록 → 확인 id |

## 환경 변수 (`.env.example` 참조)
| 변수 | 기본값 | 설명 |
|---|---|---|
| `REUSE_THRESHOLD` | 0.75 | REUSE 임계값 |
| `EXTEND_THRESHOLD` | 0.50 | EXTEND 임계값 (`0 < extend ≤ reuse ≤ 1`, 위반 시 기본값 폴백) |
| `TOP_N` | 3 | 재검증 대상 Top-N |
| `DEMO_MODE` | true | ON=결정적 fixture / OFF=Amazon Bedrock Claude (폴백 없음) |
| `LLM_MODEL_ID` | claude-3-5-sonnet | Bedrock 모델 ID (DEMO_MODE=off 시) |
| `LLM_REGION` | us-east-1 | Bedrock 리전 |
| `LLM_TIMEOUT_SECONDS` | 30 | LLM 타임아웃(재시도 없음) |
| `ASSETS_PATH` / `EVIDENCE_PATH` / `DEMO_FIXTURES_PATH` / `FEEDBACK_PATH` | `data/*` | 데이터 경로 |
| `LOG_LEVEL` | INFO | 로그 레벨 |

### demoMode
- **ON**: `data/demo_fixtures.json`의 결정적 응답만 사용. 대표 시나리오(Hero + 3 Unhappy)
  재현. 미매칭 입력은 폴백하지 않고 `422 DEMO_FIXTURE_NOT_FOUND` 오류.
- **OFF**: 실제 Amazon Bedrock Claude 호출(AWS 자격증명 필요). fixture 폴백 없음.

대표 데모 입력(demoMode ON):
- Hero(REUSE): "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요" (role=Sales)
- NEEDS_REVIEW: "예전 프로젝트에서 쓰던 공통 기능 라이브러리를 재사용하고 싶어요" (role=Developer)
- DEVELOP: "릴리스 버전 체크와 아티팩트 검증을 자동화하는 스크립트가 필요해요" (role=Sales)
- Clarify: "대시보드 하나 만들어줘"

## 테스트
```bash
pytest                      # 전체
pytest tests/pbt            # Property-Based Test (Hypothesis, C6 P1~P11)
pytest tests/unit           # 예제 기반 단위 + API + orchestrator
```

## 구조 요점
- `app/domain` — 기술 중립 도메인 모델/오류(공개 DTO와 분리, §3.2).
- `app/components` — C1~C8 (C6 DecisionClassifier는 순수·PBT 대상).
- `app/services/orchestrator.py` — S1 동기 순차 오케스트레이션.
- `app/infra` — LLMClient(Bedrock/Fixture), AssetRepository(in-memory), FeedbackStore(JSONL).
- `app/adapters` — SourceAdapter + Registry (mock 6 Source).
- `app/api` — 공개 요청/응답 DTO + 오류 매핑(내부 필드 비노출).
