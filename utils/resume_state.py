import json
from pathlib import Path
from typing import Set, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ResumeCheckpoint:
    processed_problems: Set[str]
    last_error: str = ""
    last_error_timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "processed_problems": list(self.processed_problems),
            "last_error": self.last_error,
            "last_error_timestamp": self.last_error_timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResumeCheckpoint":
        return cls(
            processed_problems=set(data.get("processed_problems", [])),
            last_error=data.get("last_error", ""),
            last_error_timestamp=data.get("last_error_timestamp", ""),
        )


class ResumeState:
    def __init__(self, checkpoint_file: Path = Path(".leetcode_resume")) -> None:
        self.checkpoint_file = checkpoint_file
        self.checkpoint = self._load()

    def _load(self) -> ResumeCheckpoint:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, encoding="utf-8") as handle:
                data = json.load(handle)
            return ResumeCheckpoint.from_dict(data)
        return ResumeCheckpoint(processed_problems=set())

    def save(self) -> None:
        with open(self.checkpoint_file, "w", encoding="utf-8") as handle:
            json.dump(self.checkpoint.to_dict(), handle, indent=2)

    def mark_problem_done(self, problem_id: str) -> None:
        self.checkpoint.processed_problems.add(problem_id)
        self.save()

    def is_problem_done(self, problem_id: str) -> bool:
        return problem_id in self.checkpoint.processed_problems

    def clear(self) -> None:
        self.checkpoint_file.unlink(missing_ok=True)
        self.checkpoint = ResumeCheckpoint(processed_problems=set())
