"""Application-level errors that map cleanly onto HTTP responses."""


class AppError(Exception):
    """Base error carrying a machine-readable code, message and HTTP status."""

    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class ValidationError(AppError):
    """Raised when an uploaded file or request input is rejected."""


class NotFoundError(AppError):
    def __init__(self, message: str = "Analysis not found or expired."):
        super().__init__("not_found", message, 404)
