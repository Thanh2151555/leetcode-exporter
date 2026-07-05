"""Tests for crawler modules."""

import pytest
from models.submission import LeetCodeProblem, SubmissionCode


class TestLeetCodeProblem:
    """Test LeetCodeProblem dataclass."""

    def test_problem_creation(self):
        problem = LeetCodeProblem(
            problem_id="1",
            title="Two Sum",
            slug="two-sum"
        )
        assert problem.problem_id == "1"
        assert problem.title == "Two Sum"
        assert problem.slug == "two-sum"

    def test_problem_with_difficulty(self):
        problem = LeetCodeProblem(
            problem_id="1",
            title="Two Sum",
            slug="two-sum",
            difficulty="Easy"
        )
        assert problem.difficulty == "Easy"


class TestSubmissionCode:
    """Test SubmissionCode dataclass."""

    def test_submission_code_creation(self):
        code = SubmissionCode(
            language="python",
            code="print('hello')",
            url="https://leetcode.com/submissions/detail/123/"
        )
        assert code.language == "python"
        assert code.code == "print('hello')"
        assert code.url == "https://leetcode.com/submissions/detail/123/"
