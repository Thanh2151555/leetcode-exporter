from dataclasses import dataclass
from pathlib import Path


@dataclass
class LeetCodeProblem:
    problem_id: str
    title: str
    slug: str
    difficulty: str = ""


@dataclass
class SubmissionCode:
    language: str
    code: str
    url: str
