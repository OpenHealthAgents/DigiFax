"""
value_objects.py
Domain Value Objects representing actors and payload modifications.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from src.domain.common.value_object import ValueObject

ALLOWED_ACTIONS = {
    "CREATE",
    "READ",
    "UPDATE",
    "DELETE",
    "CONFIG_CHANGE",
    "WORKFLOW_RUN",
    "ADMIN_ACTION",
    "KEY_ROTATION",
    "TAMPER_SCAN"
}


@dataclass(frozen=True)
class AuditActor(ValueObject):
    """Immutable representation of the transaction initiator actor."""
    user_id: str
    role: str
    ip_address: str

    def __post_init__(self) -> None:
        if not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not self.role.strip():
            raise ValueError("Actor role cannot be empty")


@dataclass(frozen=True)
class AuditPayload(ValueObject):
    """Details of the specific clinical database modification payload."""
    action: str
    entity_type: str
    entity_id: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.action not in ALLOWED_ACTIONS:
            raise ValueError(f"Invalid audit action: {self.action}")
        if not self.entity_type.strip():
            raise ValueError("Entity type cannot be empty")
        if not self.entity_id.strip():
            raise ValueError("Entity ID reference cannot be empty")
