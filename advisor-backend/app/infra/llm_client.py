"""LLMClient 추상화 + Bedrock/Fixture 구현 (NFR Design §1.1/§1.2, §4.2, §5.2).

- `LLMClient`: C1(structure) / C5(reverify) LLM 경계 인터페이스.
- `BedrockClaudeClient`: Amazon Bedrock Claude 호출(boto3). **재시도 없음**, 타임아웃 config.
- `FixtureLLMClient`: demoMode 결정적 fixture. **미매칭 입력 → 명시적 오류**(폴백 금지, §1.2).

실패 규약:
- 타임아웃 → LLMTimeoutError
- 그 외 LLM 오류 → 도메인 예외(IntentStructuringError는 C1에서, C5는 후보 UNAVAILABLE 강등)
- FixtureLLMClient 미매칭 → DemoFixtureNotFoundError
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.domain.errors import (
    DemoFixtureNotFoundError,
    IntentStructuringError,
    LLMTimeoutError,
)
from app.domain.models import Candidate, StructuredIntent


@dataclass
class ReverifyOutcome:
    """C5 LLM 성공 산출(정상 완료). 실패는 예외로 신호."""
    reusability_score: float
    reasoning: str
    role_task_context_note: str
    evidence_sufficient: bool
    insufficiency_reason: Optional[str] = None


class LLMClient(ABC):
    @abstractmethod
    def structure_intent(self, raw_text: str) -> StructuredIntent:
        ...

    @abstractmethod
    def reverify(self, intent: StructuredIntent, candidate: Candidate) -> ReverifyOutcome:
        ...


# ── Fixture (demoMode) ──────────────────────────────────────────────

class FixtureLLMClient(LLMClient):
    """결정적 fixture 응답. 미매칭 입력은 DemoFixtureNotFoundError(§1.2)."""

    def __init__(self, fixtures: dict):
        self._structure = fixtures.get("structure", {})
        self._reverify = fixtures.get("reverify", {})

    @staticmethod
    def load(path: Path) -> "FixtureLLMClient":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return FixtureLLMClient(data)

    @staticmethod
    def _key(raw_text: str) -> str:
        return raw_text.strip()

    def structure_intent(self, raw_text: str) -> StructuredIntent:
        entry = self._structure.get(self._key(raw_text))
        if entry is None:
            raise DemoFixtureNotFoundError(
                f"structure fixture 미존재: {self._key(raw_text)!r}"
            )
        return StructuredIntent(
            role=entry.get("role") or "",
            goal=entry.get("goal") or "",
            function=entry.get("function") or "",
            data=entry.get("data") or "",
            output=entry.get("output") or "",
        )

    def reverify(self, intent: StructuredIntent, candidate: Candidate) -> ReverifyOutcome:
        # fixture 키: intent.function 우선, 없으면 goal — 결정적 시나리오 식별자
        scenario = (intent.function or intent.goal or "").strip()
        by_candidate = self._reverify.get(scenario)
        if by_candidate is None:
            raise DemoFixtureNotFoundError(
                f"reverify fixture 시나리오 미존재: {scenario!r}"
            )
        entry = by_candidate.get(candidate.id)
        if entry is None:
            raise DemoFixtureNotFoundError(
                f"reverify fixture 후보 미존재: {scenario!r}/{candidate.id}"
            )
        return ReverifyOutcome(
            reusability_score=float(entry["score"]),
            reasoning=entry.get("reasoning", ""),
            role_task_context_note=entry.get("roleTaskContextNote", ""),
            evidence_sufficient=bool(entry.get("evidenceSufficient", True)),
            insufficiency_reason=entry.get("insufficiencyReason"),
        )


# ── Bedrock (실제 호출) ─────────────────────────────────────────────

class BedrockClaudeClient(LLMClient):
    """Amazon Bedrock Claude 호출. 재시도 없음, 타임아웃 config(§1.1).

    boto3는 지연 import(테스트/데모에서 미설치여도 무방).
    """

    def __init__(self, model_id: str, region: str, timeout_seconds: float):
        self._model_id = model_id
        self._region = region
        self._timeout = timeout_seconds
        self._client = None

    def _bedrock(self):
        if self._client is None:
            import boto3  # 지연 import
            from botocore.config import Config as BotoConfig

            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self._region,
                config=BotoConfig(
                    read_timeout=self._timeout,
                    connect_timeout=self._timeout,
                    retries={"max_attempts": 0},  # 재시도 없음(§1.1)
                ),
            )
        return self._client

    def _invoke(self, prompt: str) -> str:
        import botocore.exceptions as be

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            resp = self._bedrock().invoke_model(
                modelId=self._model_id, body=json.dumps(body)
            )
        except be.ReadTimeoutError as e:
            raise LLMTimeoutError(str(e)) from e
        except be.ConnectTimeoutError as e:
            raise LLMTimeoutError(str(e)) from e
        except Exception as e:  # noqa: BLE001 - 경계에서 도메인 예외로 변환
            raise IntentStructuringError(str(e)) from e
        payload = json.loads(resp["body"].read())
        return payload["content"][0]["text"]

    def structure_intent(self, raw_text: str) -> StructuredIntent:
        prompt = (
            "다음 요청에서 role, goal, function, data, output 5개 필드를 JSON으로만 추출하라. "
            "알 수 없으면 빈 문자열. 추가 텍스트 금지.\n\n요청:\n" + raw_text
        )
        text = self._invoke(prompt)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise IntentStructuringError(f"구조화 응답 파싱 실패: {e}") from e
        # LLM이 명시적 null을 반환해도 빈 문자열로 강제(누락 검출/‘.strip()’ 안전)
        return StructuredIntent(
            role=data.get("role") or "",
            goal=data.get("goal") or "",
            function=data.get("function") or "",
            data=data.get("data") or "",
            output=data.get("output") or "",
        )

    def reverify(self, intent: StructuredIntent, candidate: Candidate) -> ReverifyOutcome:
        prompt = _build_reverify_prompt(intent, candidate)
        text = self._invoke(prompt)
        data = json.loads(text)  # 파싱 실패는 상위(C5)에서 UNAVAILABLE 처리
        return ReverifyOutcome(
            reusability_score=float(data["score"]),
            reasoning=data.get("reasoning", ""),
            role_task_context_note=data.get("roleTaskContextNote", ""),
            evidence_sufficient=bool(data.get("evidenceSufficient", True)),
            insufficiency_reason=data.get("insufficiencyReason"),
        )


def _build_reverify_prompt(intent: StructuredIntent, candidate: Candidate) -> str:
    """C5 재검증 프롬프트(간결화, §2.4). 필요한 근거만 포함."""
    evidence_lines = "\n".join(
        f"- [{ev.source.value}/{ev.evidence_type}] {ev.title}: {ev.summary}"
        for ev in candidate.evidence
    )
    return (
        "재사용성 평가. 아래 자산이 요청 목표에 재사용 가능한지 0.0~1.0 점수로 평가하고 "
        "JSON으로만 응답하라. 필드: score(float), reasoning(string, Role/Task 맥락 반영), "
        "roleTaskContextNote(string), evidenceSufficient(bool), insufficiencyReason(string|null).\n\n"
        f"요청 role={intent.role} goal={intent.goal} function={intent.function} "
        f"data={intent.data} output={intent.output}\n\n"
        f"자산 name={candidate.asset_name} type={candidate.type.value} "
        f"lifecycle={candidate.lifecycle_status.value}\n"
        f"capabilities={candidate.capabilities}\nconstraints={candidate.constraints}\n"
        f"evidence:\n{evidence_lines}\n"
    )
