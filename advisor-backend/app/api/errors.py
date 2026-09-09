"""공통 오류 모델 + HTTP↔code 매핑 (§1.6).

공개 오류 응답: `{ error: { code, message, requestId } }` — 내부 예외 문자열 미포함.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domain.errors import AdvisorError, ErrorCode

# §1.6 HTTP 상태 매핑
_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.EMPTY_INTENT: 400,
    ErrorCode.INTENT_STRUCTURING_FAILED: 502,
    ErrorCode.LLM_TIMEOUT: 504,
    ErrorCode.REVERIFICATION_UNAVAILABLE: 502,
    ErrorCode.DEMO_FIXTURE_NOT_FOUND: 422,
}
_FALLBACK_STATUS = 500


class ErrorDetail(BaseModel):
    code: str
    message: str
    requestId: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


def http_status_for(error: AdvisorError) -> int:
    return _HTTP_STATUS.get(error.code, _FALLBACK_STATUS)


def to_error_response(error: AdvisorError, request_id: str) -> ErrorResponse:
    """공개 message만 사용(내부 detail 비노출)."""
    return ErrorResponse(
        error=ErrorDetail(
            code=error.code.value,
            message=error.public_message,
            requestId=request_id,
        )
    )


def generic_error_response(request_id: str, message: Optional[str] = None) -> ErrorResponse:
    """비도메인 예외용 일반 오류(내부 문자열 미노출)."""
    return ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message=message or "요청을 처리할 수 없습니다.",
            requestId=request_id,
        )
    )
