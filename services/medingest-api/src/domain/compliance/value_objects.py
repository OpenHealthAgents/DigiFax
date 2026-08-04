"""
value_objects.py
Domain Value Objects representing privacy regulations, consent policies, retention schedules, and audits.
"""

from dataclasses import dataclass
from datetime import datetime
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class ComplianceRegulation(ValueObject):
    """Represents a selectable active privacy regulation constraint."""
    name: str  # e.g., HIPAA, GDPR, PIPEDA, APA (Australian Privacy Act)
    description: str
    region: str


@dataclass(frozen=True)
class ConsentPolicy(ValueObject):
    """Represents patient consent opt-in details."""
    consent_type: str  # OPT_IN, OPT_OUT
    scope: str        # e.g., CLINICAL_SHARING, PHI_TRANSMISSION
    signed_date: str

    def __post_init__(self) -> None:
        if self.consent_type not in ("OPT_IN", "OPT_OUT"):
            raise ValueError("Invalid consent type. Must be OPT_IN or OPT_OUT")
        if not self.scope.strip():
            raise ValueError("Consent scope cannot be empty")


@dataclass(frozen=True)
class RetentionRule(ValueObject):
    """Defines retention duration and actions for resources."""
    resource_type: str  # e.g. Patient, Observation, Document
    retention_days: int
    expiration_action: str  # PURGE, ARCHIVE

    def __post_init__(self) -> None:
        if self.retention_days < 0:
            raise ValueError("Retention days cannot be negative")
        if self.expiration_action not in ("PURGE", "ARCHIVE"):
            raise ValueError("Invalid expiration action. Must be PURGE or ARCHIVE")


@dataclass(frozen=True)
class AuditLogEntry(ValueObject):
    """Represents compliance access logs."""
    user_id: str
    resource_id: str
    action: str  # e.g., READ, WRITE, EXPORT, PURGE
    justification: str
    timestamp: str = None

    def __post_init__(self) -> None:
        if not self.user_id.strip():
            raise ValueError("Audit log user ID cannot be empty")
        if not self.resource_id.strip():
            raise ValueError("Audit log resource ID cannot be empty")
        if not self.justification.strip():
            raise ValueError("Audit access justification cannot be empty")
        
        # Auto timestamp if empty
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now().isoformat())
