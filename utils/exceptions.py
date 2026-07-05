class LeetCodeExporterException(Exception):
    """Base exception for LeetCode Exporter."""
    pass


class LoginFailedException(LeetCodeExporterException):
    """Raised when login to LeetCode fails."""
    pass


class CrawlerException(LeetCodeExporterException):
    """Raised when crawling LeetCode fails."""
    pass


class ExportException(LeetCodeExporterException):
    """Raised when exporting solutions fails."""
    pass


class GitException(LeetCodeExporterException):
    """Raised when Git operations fail."""
    pass


class ResumeException(LeetCodeExporterException):
    """Raised when resuming from checkpoint fails."""
    pass
