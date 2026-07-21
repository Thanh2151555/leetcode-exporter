import logging
import sys
from pathlib import Path

from tqdm import tqdm
from rich.console import Console

from utils.config import AppConfig
from utils.logger import setup_logger
from utils.resume_state import ResumeState
from utils.exceptions import LeetCodeExporterException

from crawler.chrome_session import ChromeSessionManager
from crawler.login import LoginService
from crawler.problemset import ProblemSetCrawler
from crawler.submissions import SubmissionCrawler
from crawler.detail import SubmissionDetailCrawler

from exporter.folder import ExportFolderService
from exporter.readme import ReadmeService

from git_service.git_manager import GitManager


console = Console()


def main() -> None:
    """Main orchestration for LeetCode Exporter."""
    try:
        # Load configuration
        config = AppConfig.load()
        logger = setup_logger(config.log_level)
        
        logger.info("=" * 80)
        logger.info("Starting LeetCode Exporter")
        logger.info("Output path: %s", config.output_path)
        logger.info("Repository path: %s", config.repo_path)
        logger.info("=" * 80)

        # Initialize services
        chrome_manager = ChromeSessionManager(
            headless=config.headless,
            browser=config.browser,
            user_data_dir=str(config.user_data_dir),
            profile_dir=config.profile_dir,
        )
        driver = chrome_manager.start()
        
        resume_state = ResumeState()
        git_manager = GitManager(config.repo_path)
        if config.repo_url:
            git_manager.set_remote(config.repo_url)
        export_service = ExportFolderService(config.output_path)
        readme_service = ReadmeService(config.output_path)

        logger.info("Initialized services successfully")

        try:
            # Step 1: Login
            login_service = LoginService(driver, config.username, config.password, config.session_cookie)
            login_service.ensure_login()

            # Step 2: Collect solved problems
            problemset_crawler = ProblemSetCrawler(driver)
            all_problems = problemset_crawler.collect_solved_problems()
            logger.info("Found %d solved problems", len(all_problems))

            # Step 3: Filter problems that need to be exported (resume support & filesystem check)
            problems_to_export = []
            for p in all_problems:
                if resume_state.is_problem_done(p.problem_id):
                    continue
                if export_service.is_problem_exported(p):
                    # Mark as done in state so we don't check disk again next time
                    resume_state.mark_problem_done(p.problem_id)
                    continue
                problems_to_export.append(p)

            logger.info("Problems to export: %d (skipping %d already exported)", 
                       len(problems_to_export), len(all_problems) - len(problems_to_export))

            if not problems_to_export:
                logger.info("All problems already exported!")
                console.print("[green]✓ All problems have been exported![/green]")
            else:
                # Step 4: Export each problem
                submission_crawler = SubmissionCrawler(driver)
                detail_crawler = SubmissionDetailCrawler(driver)
                
                exported_problems = []
                failed_problems = []

                with tqdm(total=len(problems_to_export), desc="Exporting problems", ncols=80) as pbar:
                    for problem in problems_to_export:
                        try:
                            # Open problem and get latest accepted submission
                            submission_url = submission_crawler.open_problem_submissions(problem)
                            
                            # Extract source code
                            submission_code = detail_crawler.extract_code(submission_url)
                            
                            # Save solution to file
                            export_service.save_solution(problem, submission_code)
                            
                            # Mark as done in resume state
                            resume_state.mark_problem_done(problem.problem_id)
                            exported_problems.append(problem)
                            
                            pbar.update(1)
                            pbar.set_postfix({"problem": f"{problem.problem_id} - {problem.title}"})
                            
                        except LeetCodeExporterException as exc:
                            logger.warning("Failed to export problem %s: %s", problem.problem_id, str(exc))
                            failed_problems.append((problem, exc))
                            pbar.update(1)
                        except Exception as exc:
                            logger.error("Unexpected error exporting problem %s: %s", problem.problem_id, str(exc))
                            failed_problems.append((problem, exc))
                            pbar.update(1)

                logger.info("Export complete: %d successful, %d failed", len(exported_problems), len(failed_problems))

                if failed_problems:
                    console.print("[yellow]⚠ Failed to export the following problems:[/yellow]")
                    for problem, exc in failed_problems:
                        console.print(f"  - {problem.problem_id}: {problem.title}")
                        logger.debug("Error details: %s", str(exc))

                # Step 5: Generate README
                readme_service.generate_readme(all_problems)
                console.print("[green]✓ Generated README.md[/green]")

                # Step 6: Commit and push
                git_manager.stage_all()
                git_manager.commit(f"[LeetCode Exporter] Export {len(exported_problems)} solutions")
                
                try:
                    git_manager.push()
                    console.print("[green]✓ Pushed to GitHub[/green]")
                except LeetCodeExporterException as exc:
                    logger.warning("Failed to push to GitHub (repository may not have remote configured): %s", str(exc))
                    console.print("[yellow]⚠ Changes committed but failed to push to GitHub[/yellow]")

                # Summary
                console.print("\n[bold green]✓ LeetCode Exporter Completed Successfully![/bold green]")
                console.print(f"  Exported: {len(exported_problems)} solutions")
                console.print(f"  Failed: {len(failed_problems)}")
                console.print(f"  Output path: {config.output_path}")

        finally:
            chrome_manager.quit()
            logger.info("Closed Chrome WebDriver")

    except Exception as exc:
        logger.error("Fatal error: %s", str(exc), exc_info=True)
        console.print(f"[red]✗ Error: {str(exc)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

