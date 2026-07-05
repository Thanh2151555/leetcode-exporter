import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AppConfig:
    """Application configuration loaded from config.yaml and environment variables."""
    
    username: str
    password: str
    output_path: Path
    repo_path: Path
    log_level: str = "INFO"
    headless: bool = True
    browser: str = "chrome"
    user_data_dir: Path = Path(".selenium_user_data")
    profile_dir: str = "Default"

    @classmethod
    def load(cls, config_file: str = "config.yaml") -> "AppConfig":
        """
        Load configuration from YAML file with environment variable overrides.
        
        Environment variables take precedence:
        - LEETCODE_USERNAME
        - LEETCODE_PASSWORD
        - OUTPUT_PATH
        - REPO_PATH
        - LOG_LEVEL
        - HEADLESS (true/false)
        - BROWSER (chrome, edge, auto)
        - USER_DATA_DIR
        - PROFILE_DIR
        """
        with open(config_file, encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}

        # Extract from YAML with env var overrides
        username = os.getenv("LEETCODE_USERNAME") or raw.get("leetcode", {}).get("username", "")
        password = os.getenv("LEETCODE_PASSWORD") or raw.get("leetcode", {}).get("password", "")
        output_path = os.getenv("OUTPUT_PATH") or raw.get("output_path", "exported_solutions")
        repo_path = os.getenv("REPO_PATH") or raw.get("repo_path", ".")
        log_level = os.getenv("LOG_LEVEL", raw.get("log_level", "INFO"))
        headless = os.getenv("HEADLESS", str(raw.get("headless", True))).lower() in ("true", "1", "yes")
        browser = os.getenv("BROWSER", raw.get("browser", "chrome")).lower()
        user_data_dir = os.getenv("USER_DATA_DIR") or raw.get("user_data_dir", ".selenium_user_data")
        profile_dir = os.getenv("PROFILE_DIR") or raw.get("profile_dir", "Default")

        return cls(
            username=username,
            password=password,
            output_path=Path(output_path).expanduser().resolve(),
            repo_path=Path(repo_path).expanduser().resolve(),
            log_level=log_level.upper(),
            headless=headless,
            browser=browser,
            user_data_dir=Path(user_data_dir).expanduser().resolve(),
            profile_dir=profile_dir,
        )
