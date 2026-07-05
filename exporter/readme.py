import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

from models.submission import LeetCodeProblem
from utils.exceptions import ExportException


logger = logging.getLogger(__name__)


class ReadmeService:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path

    def generate_readme(self, problems: Iterable[LeetCodeProblem]) -> Path:
        """Generate README.md with a table of exported problems."""
        try:
            readme_path = self.base_path / "README.md"
            problem_list = list(problems)
            
            lines = [
                "# LeetCode Exporter",
                "",
                "Exported solved LeetCode problems from a personal account.",
                "",
                f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                f"**Total Problems:** {len(problem_list)}",
                "",
                "| # | Title | Slug |",
                "|---|-------|------|",
            ]

            for problem in sorted(problem_list, key=lambda p: int(p.problem_id)):
                lines.append(
                    f"| {problem.problem_id} | [{problem.title}](./{problem.problem_id.zfill(4)}-{problem.slug}) | {problem.slug} |"
                )

            readme_path.write_text("\n".join(lines), encoding="utf-8")
            logger.info("Generated README.md with %d problems", len(problem_list))
            return readme_path
        except Exception as exc:
            logger.error("Failed to generate README: %s", str(exc))
            raise ExportException("Failed to generate README") from exc
