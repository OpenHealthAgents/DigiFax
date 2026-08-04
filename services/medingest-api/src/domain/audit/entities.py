"""
entities.py
Domain Entities representing cryptographic immutable AuditEvent aggregate roots.
"""

import hashlib
import json
from datetime import datetime
from src.domain.common.entity import Entity
from src.domain.audit.value_objects import AuditActor, AuditPayload


class AuditEvent(Entity):
    """
    Aggregate Root scoping a tamper-detectable Audit Event.
    """

    def __init__(
        self,
        event_id: str,
        tenant_id: str,
        actor: AuditActor,
        payload: AuditPayload,
        timestamp: str = None,
        log_hash: str = "",
        version: int = 1
    ):
        super().__init__(id=event_id)
        self.event_id = event_id
        self.tenant_id = tenant_id
        self.actor = actor
        self.payload = payload
        self.timestamp = timestamp or datetime.now().isoformat()
        self.log_hash = log_hash
        self.version = version

    def calculate_hash(self, previous_hash: str) -> str:
        """
        Computes SHA256 hash chaining over variables and the previous hash reference.
        """
        raw_payload = {
            "action": self.payload.action,
            "entity_type": self.payload.entity_type,
            "entity_id": self.payload.entity_id,
            "before_state": self.payload.before_state,
            "after_state": self.payload.after_state
        }
        
        raw_data = (
            f"{self.event_id}|"
            f"{self.tenant_id}|"
            f"{self.timestamp}|"
            f"{self.actor.user_id}|"
            f"{json.dumps(raw_payload, sort_keys=True)}|"
            f"{previous_hash}"
        )
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def sign_event(self, previous_hash: str) -> None:
        """Sets the log_hash by calculating the chain hash value."""
        self.log_hash = self.calculate_hash(previous_hash)

    def verify_integrity(self, previous_hash: str) -> bool:
        """Checks if current log_hash matches the re-computed chain hash value."""
        if not self.log_hash:
            return False
        return self.log_hash == self.calculate_hash(previous_hash)
class SecurityTamperException(Exception):
    """Exception raised when audit log tampering is detected."""
    pass
