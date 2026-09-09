"""피드백 저장소 — JSONL append-only, 영속 (NFR-A4).

시작 시 기존 JSONL 로드, append로 신규 기록. 실제 DB로 교체 가능(경계).
"""
from __future__ import annotations

import json
from pathlib import Path

from app.domain.models import Feedback, FeedbackVerdict
from datetime import datetime


class FeedbackStore:
    def __init__(self, path: Path):
        self._path = Path(path)
        self._records: list[Feedback] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            self._records.append(
                Feedback(
                    result_id=d["resultId"],
                    candidate_id=d["candidateId"],
                    verdict=FeedbackVerdict(d["verdict"]),
                    timestamp=datetime.fromisoformat(d["timestamp"]),
                )
            )

    def append(self, feedback: Feedback) -> None:
        self._records.append(feedback)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "resultId": feedback.result_id,
            "candidateId": feedback.candidate_id,
            "verdict": feedback.verdict.value,
            "timestamp": feedback.timestamp.isoformat(),
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def all(self) -> list[Feedback]:
        return list(self._records)
