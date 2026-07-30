"""
value_objects.py
Domain Value Objects representing report schedules and parameters.
"""

from dataclasses import dataclass
from src.domain.common.value_object import ValueObject

ALLOWED_FORMATS = {"CSV", "EXCEL", "PDF"}


@dataclass(frozen=True)
class ReportSchedule(ValueObject):
    """Immutable representation of a report delivery schedule schedule."""
    cron_expression: str
    recipient_email: str
    file_format: str  # CSV, EXCEL, PDF
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.cron_expression.strip():
            raise ValueError("Cron expression cannot be empty")
        if "@" not in self.recipient_email:
            raise ValueError("Invalid recipient email address")
        if self.file_format not in ALLOWED_FORMATS:
            raise ValueError(f"Invalid file format: {self.file_format}. Must be one of {ALLOWED_FORMATS}")
