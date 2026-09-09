"""도메인 오류 코드 + 파이프라인 예외 (NFR Design §1.6).

내부 예외 문자열은 공개 응답에 노출되지 않는다. api/errors.py가 이 예외들을
HTTP 상태 + 공통 오류 코드로 매핑한다.
"""
from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    EMPTY_INTENT = "EMPTY_INTENT"
    INTENT_STRUCTURING_FAILED = "INTENT_STRUCTURING_FAILED"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    REVERIFICATION_UNAVAILABLE = "REVERIFICATION_UNAVAILABLE"
    DEMO_FIXTURE_NOT_FOUND = "DEMO_FIXTURE_NOT_FOUND"


class AdvisorError(Exception):
    """공통 오류 신호. `internal_detail`은 서버 로그 전용(공개 message 아님)."""

    code: ErrorCode = ErrorCode.INTENT_STRUCTURING_FAILED
    public_message = "요청을 처리할 수 없습니다."

    def __init__(self, internal_detail: str = ""):
        super().__init__(internal_detail or self.public_message)
        self.internal_detail = internal_detail


class EmptyIntentError(AdvisorError):
    code = ErrorCode.EMPTY_INTENT
    public_message = "의도 텍스트가 비어 있습니다. 입력을 제공해 주세요."


class IntentStructuringError(AdvisorError):
    code = ErrorCode.INTENT_STRUCTURING_FAILED
    public_message = "의도를 구조화하지 못했습니다. 잠시 후 다시 시도해 주세요."


class LLMTimeoutError(AdvisorError):
    code = ErrorCode.LLM_TIMEOUT
    public_message = "처리 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."


class ReverificationUnavailableError(AdvisorError):
    code = ErrorCode.REVERIFICATION_UNAVAILABLE
    public_message = "재검증을 완료하지 못했습니다. 잠시 후 다시 시도해 주세요."


class DemoFixtureNotFoundError(AdvisorError):
    code = ErrorCode.DEMO_FIXTURE_NOT_FOUND
    public_message = "데모 모드에서 지원하지 않는 입력입니다."
