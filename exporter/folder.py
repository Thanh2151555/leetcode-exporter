import logging
from pathlib import Path

from models.submission import LeetCodeProblem, SubmissionCode
from utils.exceptions import ExportException


logger = logging.getLogger(__name__)


class ExportFolderService:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized export service with base path: %s", self.base_path)

    def create_problem_folder(self, problem: LeetCodeProblem) -> Path:
        """Create a problem folder with the pattern: 0001-Two-Sum"""
        directory_name = f"{problem.problem_id.zfill(4)}-{problem.slug}"
        folder_path = self.base_path / directory_name
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug("Created/verified folder: %s", folder_path)
            return folder_path
        except Exception as exc:
            logger.error("Failed to create folder for problem %s: %s", problem.problem_id, str(exc))
            raise ExportException(f"Failed to create folder for problem {problem.problem_id}") from exc

    def save_solution(self, problem: LeetCodeProblem, submission: SubmissionCode) -> Path:
        """Save solution code to file."""
        try:
            folder = self.create_problem_folder(problem)
            extension = "java" if submission.language == "java" else "py"
            filename = f"Solution.{extension}"
            file_path = folder / filename
            file_path.write_text(submission.code, encoding="utf-8")
            logger.info("Saved solution for problem %s: %s (%d bytes)", 
                       problem.problem_id, file_path, len(submission.code))
            return file_path
        except Exception as exc:
            logger.error("Failed to save solution for problem %s: %s", problem.problem_id, str(exc))
            raise ExportException(f"Failed to save solution for problem {problem.problem_id}") from exc
