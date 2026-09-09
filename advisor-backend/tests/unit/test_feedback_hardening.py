"""F-05/F-06 하드닝 테스트 — 입력 검증(422) + append 동시성 락(무손실).

test_api.py 스타일을 미러링한다(DEMO_MODE 기본 ON + tmp_path fb 파일로 repo data/ 미오염).
"""
from __future__ import annotations

import dataclasses
import threading
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.domain.models import Feedback, FeedbackVerdict
from app.infra.feedback_store import FeedbackStore
from app.main import create_app


@pytest.fixture
def client(tmp_path) -> TestClient:
    # feedback_path를 tmp로 돌려 repo의 data/feedback.jsonl 오염 방지.
    config = dataclasses.replace(Config.load(), feedback_path=tmp_path / "fb.jsonl")
    return TestClient(create_app(config))


# ── F-05: 입력 검증 (HTTP 422) ────────────────────────────────────
def test_feedback_empty_result_id_returns_422(client):
    resp = client.post(
        "/feedback",
        json={"resultId": "", "candidateId": "asset-001", "verdict": "useful"},
    )
    assert resp.status_code == 422


def test_feedback_whitespace_candidate_id_returns_422(client):
    resp = client.post(
        "/feedback",
        json={"resultId": "res-1", "candidateId": "   ", "verdict": "useful"},
    )
    assert resp.status_code == 422


def test_feedback_valid_returns_200_with_confirmation(client):
    resp = client.post(
        "/feedback",
        json={"resultId": "res-1", "candidateId": "asset-001", "verdict": "useful"},
    )
    assert resp.status_code == 200
    assert resp.json()["confirmationId"]


# ── F-06: append 동시성 락 (무손실/무손상) ────────────────────────
def test_feedback_store_concurrent_append_no_loss(tmp_path):
    path = tmp_path / "fb.jsonl"
    store = FeedbackStore(path)

    n_threads = 20
    per_thread = 50
    expected_total = n_threads * per_thread
    # 최대 경합을 위해 모든 스레드를 동시에 출발시킨다.
    start = threading.Barrier(n_threads)

    def worker(tid: int) -> None:
        start.wait()
        for i in range(per_thread):
            store.append(
                Feedback(
                    result_id=f"res-{tid}-{i}",
                    candidate_id=f"cand-{tid}-{i}",
                    verdict=FeedbackVerdict.USEFUL,
                    timestamp=datetime.now(timezone.utc),
                )
            )

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # in-memory: 유실 없음
    assert len(store.all()) == expected_total

    # on-disk: 정확히 expected_total 개의 비어있지 않은 라인 (인터리브/손상 없음)
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == expected_total
