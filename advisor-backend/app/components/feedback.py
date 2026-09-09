"""C8 Feedback — 피드백 수집 (US-4.3 / BR-FEEDBACK) [MVP: 수집만].

(resultId, candidateId, verdict) → FeedbackStore append + 확인 id.
선별/랭킹 반영은 [Later] US-5.1 (범위 밖).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.domain.models import Feedback, FeedbackVerdict
from app.infra.feedback_store import FeedbackStore


class FeedbackComponent:
    def __init__(self, store: FeedbackStore):
        self._store = store

    def record(
        self, result_id: str, candidate_id: str, verdict: FeedbackVerdict
    ) -> str:
        feedback = Feedback(
            result_id=result_id,
            candidate_id=candidate_id,
            verdict=verdict,
            timestamp=datetime.now(timezone.utc),
        )
        self._store.append(feedback)
        return uuid.uuid4().hex
