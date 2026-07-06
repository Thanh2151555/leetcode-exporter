import logging
from pathlib import Path

from git import Repo, GitCommandError, InvalidGitRepositoryError

from utils.exceptions import GitException


logger = logging.getLogger(__name__)


class GitManager:
    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
            logger.info("Opened existing Git repository: %s", repo_path)
        except InvalidGitRepositoryError:
            logger.info("Initializing new Git repository at: %s", repo_path)
            self.repo = Repo.init(repo_path)

    def stage_all(self) -> None:
        """Stage all changes for commit."""
        try:
            self.repo.git.add(".")
            logger.info("Staged all changes")
        except GitCommandError as exc:
            logger.error("Failed to stage changes: %s", str(exc))
            raise GitException("Failed to stage changes") from exc

    def commit(self, message: str) -> None:
        """Commit staged changes."""
        try:
            if self.repo.is_dirty(untracked_files=True):
                self.repo.index.commit(message)
                logger.info("Created commit: %s", message)
            else:
                logger.info("No changes to commit")
        except GitCommandError as exc:
            logger.error("Failed to commit changes: %s", str(exc))
            raise GitException("Failed to commit changes") from exc

    def push(self, remote_name: str = "origin", branch: str = None) -> None:
        """Push changes to remote repository."""
        try:
            remote = self.repo.remote(remote_name)
            if branch is None:
                branch = self.repo.active_branch.name
            remote.push(branch)
            logger.info("Pushed changes to %s/%s", remote_name, branch)
        except TypeError:
            logger.error("Failed to determine active branch (detached HEAD?)")
            raise GitException("Failed to determine active branch for push")
        except GitCommandError as exc:
            logger.error("Failed to push changes: %s", str(exc))
            raise GitException("Failed to push changes to remote") from exc
        except ValueError as exc:
            logger.error("Remote '%s' not configured: %s", remote_name, str(exc))
            raise GitException(f"Remote '{remote_name}' not configured") from exc
