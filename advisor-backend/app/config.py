"""Config 모듈 — 환경변수 override (NFR Design §4.3 Externalized Configuration).

임계값/Top-N/데모모드/LLM/경로/로그레벨을 env로 외부화한다(NFR-S4/M3).
임계값 제약 `0 < extend <= reuse <= 1` 위반 시 기본값 폴백 + 경고 로깅(BR-STATE / PBT P9).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("advisor.config")

# 기본값 (domain-entities §2.14 ClassificationConfig / U1 Open Decisions)
DEFAULT_REUSE_THRESHOLD = 0.75
DEFAULT_EXTEND_THRESHOLD = 0.50
DEFAULT_TOP_N = 3

_BACKEND_ROOT = Path(__file__).resolve().parent.parent  # advisor-backend/


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("config: %s=%r 파싱 실패 → 기본값 %s 사용", name, raw, default)
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("config: %s=%r 파싱 실패 → 기본값 %s 사용", name, raw, default)
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else (_BACKEND_ROOT / p)


@dataclass(frozen=True)
class Config:
    # Classification
    reuse_threshold: float
    extend_threshold: float
    top_n: int
    # Demo / LLM
    demo_mode: bool
    llm_model_id: str
    llm_region: str
    llm_timeout_seconds: float
    # Paths
    assets_path: Path
    evidence_path: Path
    demo_fixtures_path: Path
    feedback_path: Path
    # Logging
    log_level: str

    @staticmethod
    def load() -> "Config":
        reuse = _env_float("REUSE_THRESHOLD", DEFAULT_REUSE_THRESHOLD)
        extend = _env_float("EXTEND_THRESHOLD", DEFAULT_EXTEND_THRESHOLD)
        reuse, extend = _validate_thresholds(reuse, extend)

        top_n = _env_int("TOP_N", DEFAULT_TOP_N)
        if top_n < 1:
            logger.warning("config: TOP_N=%s < 1 → 기본값 %s 사용", top_n, DEFAULT_TOP_N)
            top_n = DEFAULT_TOP_N

        return Config(
            reuse_threshold=reuse,
            extend_threshold=extend,
            top_n=top_n,
            demo_mode=_env_bool("DEMO_MODE", True),
            llm_model_id=os.getenv(
                "LLM_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
            ),
            llm_region=os.getenv("LLM_REGION", "us-east-1"),
            llm_timeout_seconds=_env_float("LLM_TIMEOUT_SECONDS", 30.0),
            assets_path=_resolve_path(os.getenv("ASSETS_PATH", "data/assets.json")),
            evidence_path=_resolve_path(os.getenv("EVIDENCE_PATH", "data/evidence.json")),
            demo_fixtures_path=_resolve_path(
                os.getenv("DEMO_FIXTURES_PATH", "data/demo_fixtures.json")
            ),
            feedback_path=_resolve_path(os.getenv("FEEDBACK_PATH", "data/feedback.jsonl")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )


def _validate_thresholds(reuse: float, extend: float) -> tuple[float, float]:
    """제약 `0 < extend <= reuse <= 1` 검증. 위반 시 기본값 폴백 + 경고(P9)."""
    valid = 0 < extend <= reuse <= 1
    if not valid:
        logger.warning(
            "config: 임계값 제약(0 < extend <= reuse <= 1) 위반 "
            "(reuse=%s, extend=%s) → 기본값(%s/%s) 폴백",
            reuse,
            extend,
            DEFAULT_REUSE_THRESHOLD,
            DEFAULT_EXTEND_THRESHOLD,
        )
        return DEFAULT_REUSE_THRESHOLD, DEFAULT_EXTEND_THRESHOLD
    return reuse, extend
