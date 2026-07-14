"""Risk profiling questionnaire scorer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from financial_engine.models import RiskProfile


class RiskProfiler:
    """Scores a configurable risk questionnaire and maps to investment personality."""

    def __init__(self, questionnaire_path: str | Path):
        with open(questionnaire_path, encoding="utf-8") as f:
            self.config = json.load(f)

    def get_questionnaire(self) -> dict[str, Any]:
        return self.config

    def score(self, answers: dict[str, str]) -> dict[str, Any]:
        """
        answers: {question_id: option_id}
        """
        questions = self.config.get("questions", [])
        total = 0
        detail = []
        for q in questions:
            qid = q["id"]
            selected = answers.get(qid)
            option = next((o for o in q["options"] if o["id"] == selected), None)
            points = int(option["score"]) if option else 0
            total += points
            detail.append(
                {
                    "question_id": qid,
                    "question": q["text"],
                    "selected_option": selected,
                    "score": points,
                }
            )

        band = None
        for b in self.config.get("score_bands", []):
            if b["min"] <= total <= b["max"]:
                band = b
                break
        if band is None:
            band = {"profile": "moderate", "personality": "Balanced Grower", "description": ""}

        profile = RiskProfile(band["profile"])
        return {
            "total_score": total,
            "max_score": len(questions) * 4,
            "profile": profile.value,
            "personality": band["personality"],
            "description": band["description"],
            "answers_detail": detail,
        }
