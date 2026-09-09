"""구조화 로깅 + 내부 감사 로거 (NFR Design §3.4 / NFR-M1).

- `configure_logging`: 앱 전역 구조화 로거 설정(JSON-lines 유사 key=value).
- `get_audit_logger`: 미인가 제외 판정 등 **서버 내부 전용 감사** 로거.
  감사 로그는 공개 응답에 절대 포함되지 않는다(§3.2/§3.4).
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any

AUDIT_LOGGER_NAME = "advisor.audit"


class _StructuredFormatter(logging.Formatter):
    """레코드를 단일 JSON 라인으로 직렬화(구조화 로깅)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # extra로 전달된 구조화 필드 병합(표준 LogRecord 속성 제외)
        extra = getattr(record, "structured", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    # 중복 핸들러 방지(재초기화 대비)
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_StructuredFormatter())
    root.addHandler(handler)


def get_audit_logger() -> logging.Logger:
    """서버 내부 감사 로거. 미인가 제외/실패 사유 등 비공개 정보 기록 전용."""
    return logging.getLogger(AUDIT_LOGGER_NAME)


def audit(event: str, **fields: Any) -> None:
    """감사 이벤트 기록 헬퍼. fields는 구조화 필드로 저장(공개 응답 아님)."""
    get_audit_logger().info(event, extra={"structured": {"event": event, **fields}})
