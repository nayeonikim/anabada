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
from app.domain.models import Candidate, OverallDecision, StructuredIntent


@dataclass
class ReverifyOutcome:
    """C5 LLM 성공 산출(정상 완료). 실패는 예외로 신호."""
    reusability_score: float
    reasoning: str
    role_task_context_note: str
    evidence_sufficient: bool
    insufficiency_reason: Optional[str] = None


@dataclass
class ActionPromptRequest:
    """C11 Action Handoff grounding-only 페이로드(접근 가능 공개 투영만)."""
    decision_state: OverallDecision
    intent: StructuredIntent
    overall_rationale: str
    target_asset_names: list[str]
    evidence_lines: list[str]      # 공개 투영: "[Source/type] title"
    note_unavailable: bool         # §3.1 게이팅(INV-HANDOFF-5): '평가 미완료' 일반 문구 허용 여부


class LLMClient(ABC):
    @abstractmethod
    def structure_intent(self, raw_text: str) -> StructuredIntent:
        ...

    @abstractmethod
    def reverify(self, intent: StructuredIntent, candidate: Candidate) -> ReverifyOutcome:
        ...

    @abstractmethod
    def generate_action_prompt(self, req: ActionPromptRequest) -> str:
        ...


# ── Fixture (demoMode) ──────────────────────────────────────────────

class FixtureLLMClient(LLMClient):
    """결정적 fixture 응답. 미매칭 입력은 DemoFixtureNotFoundError(§1.2)."""

    def __init__(self, fixtures: dict):
        self._structure = fixtures.get("structure", {})
        self._reverify = fixtures.get("reverify", {})
        self._action_handoff = fixtures.get("actionHandoff", {})

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

    def generate_action_prompt(self, req: ActionPromptRequest) -> str:
        # fixture 키: intent.function 우선, 없으면 goal — reverify와 동일한 결정적 시나리오 식별자
        scenario = (req.intent.function or req.intent.goal or "").strip()
        entry = self._action_handoff.get(scenario)
        if entry is None:
            raise DemoFixtureNotFoundError(f"actionHandoff fixture 미존재: {scenario!r}")
        return entry["promptText"]


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

    def generate_action_prompt(self, req: ActionPromptRequest) -> str:
        # C11 Action Handoff 본문 생성. 실패/타임아웃은 _invoke가 도메인 예외로 전파
        # (orchestrator step 8 try/except가 잡아 actionPrompt=None 비차단 처리).
        prompt = _build_action_prompt(req)
        return self._invoke(prompt)


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


def _build_action_prompt(req: ActionPromptRequest) -> str:
    """C11 Action Handoff 프롬프트(grounding-only, 간결화 §2.4).

    아래 근거(req)만 사용해 외부 AI 개발 도구에 붙여 쓸 **도구 비종속 실행 Prompt 전문**을
    생성하도록 지시한다. 목표·근거·다음 작업·확인 사항 4요소 포함, 근거 밖 생성(환각) 금지.
    인용한 대상 자산/자료는 [근거 요약]에 주어진 참조(source_ref)를 본문에 함께 표기.
    """
    intent = req.intent
    targets = ", ".join(req.target_asset_names) if req.target_asset_names else "(없음 — 신규 개발)"
    evidence_block = "\n".join(f"- {line}" for line in req.evidence_lines) or "- (제공된 근거 없음)"

    # §3.1 게이팅: note_unavailable=True일 때만 후보 비식별·집계 일반 문구 허용
    unavailable_directive = (
        "- 일부 후보의 평가가 완료되지 않았으므로, 판단 확정을 위해 추가 검토가 필요하다는 취지의 "
        "**후보를 식별하지 않는 집계 수준의 일반 문구**를 1회 포함하라.\n"
        if req.note_unavailable
        else "- '평가 미완료' 취지의 문구는 포함하지 마라.\n"
    )

    return (
        "너는 재사용 권고 결과를 바탕으로, 사용자가 외부 AI 개발 도구(코딩 에이전트 등)에 그대로 "
        "붙여 넣어 쓸 수 있는 **도구 비종속 실행 Prompt 전문**을 작성한다. 사용자 입력 언어(기본 한국어, "
        "기술 용어는 영문 혼용 가능)로, 아래 4개 섹션을 모두 포함한 자연어 본문만 출력하라(머리말/메타 설명 금지):\n"
        "1) 목표(Goal): 이번 권고 목적에 맞는 다음 개발 목표\n"
        "2) 근거(Rationale): 제공된 근거 요약. 인용한 대상 자산/자료는 [근거 요약]에 주어진 "
        "참조(각 줄 '(참조: ...)' 값)를 'Source: ref' 형태로 함께 표기하라(아래 근거 밖 내용 생성 금지)\n"
        "3) 다음 작업(Next Actions): 도구 비종속 실행 단계\n"
        "4) 확인 사항(Checks): 진행 전 확인/검증 항목. **확인되지 않은 Gap·전제는 사실로 단정하지 말고 "
        "확인 질문 형태로** 표현하라.\n\n"
        "제약:\n"
        "- 아래 제공된 근거(결정/의도/근거요약/대상 자산)만 사용하고, 그 밖의 사실을 지어내지 마라.\n"
        "- 후보 id·권한 제외 자산·내부 기술 실패 사유·제외 개수 등은 언급하지 마라(제공되지 않음).\n"
        f"{unavailable_directive}\n"
        f"[권고 결정] {req.decision_state.value}\n"
        f"[대상 자산] {targets}\n"
        f"[요청 의도] role={intent.role} goal={intent.goal} function={intent.function} "
        f"data={intent.data} output={intent.output}\n"
        f"[권고 근거] {req.overall_rationale}\n"
        f"[근거 요약]\n{evidence_block}\n"
    )
