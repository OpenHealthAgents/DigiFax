"""
value_objects.py
Domain Value Objects representing tracked clinical system usage metrics.
"""

from dataclasses import dataclass
from datetime import datetime
from src.domain.common.value_object import ValueObject

# Allowed metrics definitions matching user request
ALLOWED_METRICS = {
    "DOCUMENTS_UPLOADED",
    "PAGES_PROCESSED",
    "OCR_REQUESTS",
    "AI_REQUESTS",
    "FHIR_RESOURCES",
    "VALIDATION_REQUESTS",
    "EXPORTS",
    "STORAGE_BYTES",
    "BANDWIDTH_BYTES",
    "USERS_COUNT",
    "API_CALLS",
    "WORKFLOW_EXECUTIONS",
    "REVIEW_SESSIONS"
}


@dataclass(frozen=True)
class MeteredMetric(ValueObject):
    """Immutable log of a metered usage event."""
    metric_name: str
    quantity: float
    timestamp: str = None

    def __post_init__(self) -> None:
        if self.metric_name not in ALLOWED_METRICS:
            raise ValueError(f"Invalid metric name: {self.metric_name}. Must be one of {ALLOWED_METRICS}")
        if self.quantity < 0:
            raise ValueError("Accrued metered quantity cannot be negative")
        
        # Auto timestamp if empty
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now().isoformat())
