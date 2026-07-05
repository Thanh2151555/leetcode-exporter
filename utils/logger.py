import logging
from pathlib import Path

from rich.logging import RichHandler


def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("leetcode_exporter")
    logger.setLevel(level.upper())

    if not logger.handlers:
        console_handler = RichHandler(rich_tracebacks=True)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(console_handler)

        log_path = Path.cwd() / "leetcode_exporter.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(file_handler)

    return logger
