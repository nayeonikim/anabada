"""C1 IntentStructuring — 5필드 추출 + 누락 검출 + ClarificationRequest (US-1.1/1.2/1.3).

LLM(structure) 실패는 IntentStructuringError/LLMTimeoutError로 종료(§1.3, 폴백 없음).
demoMode 미매칭은 LLMClient에서 DemoFixtureNotFoundError 발생(§1.2).
"""
from __future__ import annotations

from app.domain.errors import EmptyIntentError
from app.domain.models import (
    ClarificationRequest,
    REQUIRED_INTENT_FIELDS,
    StructuredIntent,
)
from app.infra.llm_client import LLMClient

_FIELD_QUESTIONS = {
    "role": "어떤 역할(직무)에서 사용하실 예정인가요?",
    "goal": "달성하려는 목표가 무엇인가요?",
    "function": "어떤 기능을 만들고 싶으신가요?",
    "data": "어떤 데이터를 사용하실 예정인가요?",
    "output": "결과물은 어떤 형태(대시보드/API/스크립트 등)여야 하나요?",
}


class IntentStructuringComponent:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    def structure(self, raw_text: str) -> StructuredIntent:
        if raw_text is None or raw_text.strip() == "":
            raise EmptyIntentError("rawText 비어 있음")
        # LLM 실패/타임아웃/데모 미매칭은 예외로 전파(§1.3/§1.6)
        return self._llm.structure_intent(raw_text)

    @staticmethod
    def detect_missing_fields(intent: StructuredIntent) -> list[str]:
        missing = []
        for field in REQUIRED_INTENT_FIELDS:
            # None(누락/명시적 null)도 빈 값으로 취급 — '.strip()' 안전
            if not (getattr(intent, field, "") or "").strip():
                missing.append(field)
        return missing

    @staticmethod
    def build_clarification(missing_fields: list[str]) -> ClarificationRequest:
        return ClarificationRequest(
            missing_fields=list(missing_fields),
            questions=[_FIELD_QUESTIONS[f] for f in missing_fields],
        )
