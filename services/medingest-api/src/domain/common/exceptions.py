class DomainException(Exception):  # noqa: N818
    """Base exception for all domain business rule violations."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or "DOMAIN_ERROR"
