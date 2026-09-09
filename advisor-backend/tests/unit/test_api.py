"""API 라우트 · 공개 DTO 직렬화 · 오류 매핑 테스트 (§1.6/§3.2).

핵심 검증: 미인가/내부 필드가 공개 응답 JSON에 **부재**함(Type-Enforced Non-Disclosure).
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.main import create_app

_DATA = Path(__file__).resolve().parent.parent.parent / "data"

_HERO = "고객의 Project, Forecast, Risk, 요청사항을 한 화면에서 조회하는 대시보드를 만들고 싶어요"
_CLARIFY = "대시보드 하나 만들어줘"


@pytest.fixture
def client(tmp_path) -> TestClient:
    config = dataclasses.replace(Config.load(), feedback_path=tmp_path / "fb.jsonl")
    return TestClient(create_app(config))


def _structured_intent(role: str) -> dict:
    return {
        "role": role,
        "goal": "고객 현황 통합 조회 대시보드 구성",
        "function": "customer overview dashboard",
        "data": "customer project forecast risk request",
        "output": "dashboard",
    }


# ── /intent ───────────────────────────────────────────────────────
def test_intent_structured(client):
    resp = client.post("/intent", json={"rawText": _HERO})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "structured"
    assert body["intent"]["role"] == "Sales"
    assert body["clarification"] is None


def test_intent_clarification(client):
    resp = client.post("/intent", json={"rawText": _CLARIFY})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "clarification"
    assert set(body["clarification"]["missingFields"]) == {"role", "data"}


def test_intent_empty_returns_400(client):
    resp = client.post("/intent", json={"rawText": "   "})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "EMPTY_INTENT"
    assert "requestId" in resp.json()["error"]


def test_intent_demo_unmatched_returns_422(client):
    resp = client.post("/intent", json={"rawText": "데모에 없는 임의 요청"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "DEMO_FIXTURE_NOT_FOUND"


# ── /advise ───────────────────────────────────────────────────────
def test_advise_hero_reuse(client):
    resp = client.post(
        "/advise",
        json={
            "intent": _structured_intent("Sales"),
            "context": {"userId": "mock-sales-user", "role": "Sales"},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["overallDecision"] == "REUSE"
    assert body["isRecommendation"] is True
    top = body["ranking"][0]
    assert top["candidateId"] == "asset-001"
    assert top["evaluationStatus"] == "COMPLETED"
    assert top["reusabilityScore"] == pytest.approx(0.92)


def test_advise_response_hides_internal_fields(client):
    resp = client.post(
        "/advise",
        json={
            "intent": _structured_intent("Sales"),
            "context": {"userId": "mock-sales-user", "role": "Sales"},
        },
    )
    raw = resp.text
    # §3.2/§1.4: 내부/제외 정보는 공개 응답에 절대 부재
    for forbidden in (
        "technicalFailureReason",
        "excluded",
        "excludedCount",
        "ExcludedCandidate",
        "allowedRoles",
        "allowedUsers",
    ):
        assert forbidden not in raw


def test_advise_develop_empty_ranking(client):
    # Sales는 관련 자산(Developer 전용)에 접근 불가 → DEVELOP
    resp = client.post(
        "/advise",
        json={
            "intent": {
                "role": "Sales",
                "goal": "릴리스 자동화 스크립트 구성",
                "function": "release version checklist automation script",
                "data": "build artifact version",
                "output": "script",
            },
            "context": {"userId": "mock-sales-user", "role": "Sales"},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["overallDecision"] == "DEVELOP"
    assert body["ranking"] == []


# ── /feedback ─────────────────────────────────────────────────────
def test_feedback_confirmation(client):
    resp = client.post(
        "/feedback",
        json={"resultId": "res-1", "candidateId": "asset-001", "verdict": "useful"},
    )
    assert resp.status_code == 200
    assert resp.json()["confirmationId"]
