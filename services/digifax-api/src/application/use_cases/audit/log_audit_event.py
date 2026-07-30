"""
log_audit_event.py
Use case appending cryptographic hash-linked audit records.
"""

import uuid
from src.application.ports.iaudit_repository import IAuditRepository
from src.domain.audit.entities import AuditEvent
from src.domain.audit.value_objects import AuditActor, AuditPayload


class LogAuditEventUseCase:
    """
    Usecase creating new audit log entries linked to previous hash chains.
    """

    def __init__(self, repo: IAuditRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        user_id: str,
        role: str,
        ip_address: str,
        action: str,
        entity_type: str,
        entity_id: str,
        before_state: dict = None,
        after_state: dict = None
    ) -> AuditEvent:
        """Resolves previous chain hash values, signs the new event, and commits it to persistence."""
        event_id = f"aud-{uuid.uuid4().hex[:8]}"
        actor = AuditActor(user_id=user_id, role=role, ip_address=ip_address)
        payload = AuditPayload(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state
        )

        event = AuditEvent(
            event_id=event_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=payload
        )

        # Retrieve previous log hash value to build cryptographic link
        previous_hash = self.repo.get_last_event_hash(tenant_id)
        event.sign_event(previous_hash)

        self.repo.save_event(event)
        return event
