"""
value_objects.py
Domain Value Objects representing templates, rules, and tracking logs.
"""

from dataclasses import dataclass
from src.domain.common.value_object import ValueObject

ALLOWED_CHANNELS = {"EMAIL", "SMS", "IN_APP", "WEBHOOK", "SLACK", "TEAMS"}
ALLOWED_STATUSES = {"PENDING", "SENT", "DELIVERED", "FAILED"}


@dataclass(frozen=True)
class NotificationTemplate(ValueObject):
    """Immutable representation of a notification layout template."""
    template_id: str
    subject_template: str
    body_template: str

    def __post_init__(self) -> None:
        if not self.template_id.strip():
            raise ValueError("Template ID cannot be empty")
        if not self.body_template.strip():
            raise ValueError("Body template cannot be empty")


@dataclass(frozen=True)
class EscalationRule(ValueObject):
    """Configuration detailing channel switches when primary delivery fails."""
    delay_minutes: int
    next_channel: str
    backup_recipient: str

    def __post_init__(self) -> None:
        if self.delay_minutes < 0:
            raise ValueError("Escalation delay cannot be negative")
        if self.next_channel not in ALLOWED_CHANNELS:
            raise ValueError(f"Invalid escalation channel: {self.next_channel}")
        if not self.backup_recipient.strip():
            raise ValueError("Backup recipient cannot be empty")


@dataclass(frozen=True)
class DeliveryLog(ValueObject):
    """Diagnostic tracking record logging dispatch runs."""
    dispatch_time: str
    channel: str
    status: str  # PENDING, SENT, DELIVERED, FAILED
    error_message: str | None = None
    retry_count: int = 0

    def __post_init__(self) -> None:
        if self.channel not in ALLOWED_CHANNELS:
            raise ValueError(f"Invalid delivery channel: {self.channel}")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid delivery status: {self.status}")
        if self.retry_count < 0:
            raise ValueError("Retry count cannot be negative")
