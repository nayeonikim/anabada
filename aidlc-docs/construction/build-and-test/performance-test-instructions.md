# Performance Test Instructions — U1 Advisor Backend

## Purpose
MVP는 mock 데이터 + demoMode(결정적 fixture) 기반이므로 성능은 **1차 검증(smoke/latency sanity)** 수준으로 다룬다.
실사용(`DEMO_MODE=false`, 실제 Bedrock) 성능은 LLM 지연이 지배적이며 별도 용량 계획이 필요하다.

## Performance Requirements (MVP 목표, 데모 기준)
- **Response Time (demoMode ON)**: `/intent`·`/advise`·`/feedback` p95 < 200ms (LLM fixture, 로컬).
- **Response Time (demoMode OFF)**: `/advise`는 Top-N(≤3) × LLM 재검증 지연에 지배됨 → 재시도 없음 + 타임아웃(config 기본 30s)로 상한.
- **Throughput**: 데모 목적상 단일 인스턴스 기준 수십 req/s(demoMode ON) 정도면 충분.
- **Concurrent Users**: 데모 시연 수준(≤ 20).
- **Error Rate**: demoMode ON, 대표 시나리오에서 0%.

## Setup Performance Test Environment
### 1. Prepare
```bash
cd advisor-backend
source .venv/bin/activate
pip install locust        # 또는 k6/hey/wrk 중 택1
export DEMO_MODE=true      # LLM 변동성 제거(재현성)
uvicorn app.main:app --port 8000 --workers 1
```

### 2. Test Parameters
- **Test Duration**: 2~5분
- **Ramp-up**: 30초
- **Virtual Users**: 10~20

## Run Performance Tests

### 1. Load Test (예: hey)
```bash
# /intent
hey -z 60s -c 10 -m POST -H 'Content-Type: application/json' \
  -d '{"rawText":"고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"}' \
  http://localhost:8000/intent

# /advise (structured intent 페이로드)
hey -z 60s -c 10 -m POST -H 'Content-Type: application/json' \
  -d '{"intent":{"role":"Sales","goal":"고객 현황 통합 조회 대시보드 구성","function":"customer overview dashboard","data":"customer project forecast risk request","output":"dashboard"},"context":{"userId":"mock-sales-user","role":"Sales"}}' \
  http://localhost:8000/advise
```

### 2. Stress Test
```bash
# 동시성을 단계적으로 증가시키며 오류율/지연 관찰(-c 10 → 50 → 100)
hey -n 5000 -c 100 -m POST -H 'Content-Type: application/json' \
  -d '{"rawText":"대시보드 하나 만들어줘"}' http://localhost:8000/intent
```

### 3. Analyze Results
- **Response Time**: p50/p95/p99 기록(목표: demoMode ON p95 < 200ms).
- **Throughput**: req/s 기록.
- **Error Rate**: non-2xx 비율(대표 시나리오 0% 기대; clarify/oversized 입력 제외).
- **Bottlenecks**: in-memory 조회는 O(후보수). 병목은 실사용 시 LLM 호출(demoMode OFF).
- **Results Location**: 도구 표준 출력 캡처.

## Performance Optimization
요구 미달 시:
1. demoMode ON 병목이면 프로파일링(`cProfile`) — 토큰화/정렬 핫스팟 확인.
2. demoMode OFF는 LLM 동시성/타임아웃/모델 선택 조정, 필요 시 Top-N 축소.
3. 재사용 조회가 커지면 AssetRepository 인덱싱(키워드 역색인) 도입 검토([Later]).

> 참고: 재시도 없음(§1.1) 정책상 성능 최적화가 "재시도 추가"로 흐르지 않도록 유의(오류 계약 유지).
