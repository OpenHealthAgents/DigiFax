"""
value_objects.py
Domain Value Objects representing operations metrics.
"""

from dataclasses import dataclass
from src.domain.common.value_object import ValueObject

ALLOWED_COMPONENTS = {
    "DATABASE",
    "STORAGE",
    "TEMPORAL",
    "QUEUE",
    "AI_PROVIDER",
    "OCR_PROVIDER",
    "TENANT_HEALTH"
}
ALLOWED_STATUSES = {"HEALTHY", "DEGRADED", "DOWN"}


@dataclass(frozen=True)
class HealthMetric(ValueObject):
    """Immutable representation of component latency and status checks."""
    component_name: str
    status: str
    latency_ms: float
    timestamp: str

    def __post_init__(self) -> None:
        if self.component_name not in ALLOWED_COMPONENTS:
            raise ValueError(f"Invalid component name: {self.component_name}")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status code: {self.status}")
        if self.latency_ms < 0:
            raise ValueError("Component latency cannot be negative")
