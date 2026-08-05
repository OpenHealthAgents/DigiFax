"""
in_memory_audit_repository.py
In-memory persistence adapter storing immutable hash-chained AuditEvent logs.
"""

from src.application.ports.iaudit_repository import IAuditRepository
from src.domain.audit.entities import AuditEvent
from src.domain.audit.value_objects import AuditActor, AuditPayload
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryAuditRepository(BaseInMemoryRepository, IAuditRepository):
    """
    Thread-safe in-memory adapter storing immutable logs.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_event(self, event: AuditEvent) -> None:
        """Saves a signed audit event log."""
        actor_data = {
            "user_id": event.actor.user_id,
            "role": event.actor.role,
            "ip_address": event.actor.ip_address
        }
        payload_data = {
            "action": event.payload.action,
            "entity_type": event.payload.entity_type,
            "entity_id": event.payload.entity_id,
            "before_state": event.payload.before_state,
            "after_state": event.payload.after_state
        }
        record_data = {
            "id": f"aud:{event.tenant_id}:{event.event_id}",
            "event_id": event.event_id,
            "tenant_id": event.tenant_id,
            "actor": actor_data,
            "payload": payload_data,
            "timestamp": event.timestamp,
            "log_hash": event.log_hash,
            "version": event.version
        }
        with self._lock:
            self._records[record_data["id"]] = record_data

    def get_event(self, tenant_id: str, event_id: str) -> AuditEvent | None:
        """Loads a signed audit event log."""
        aud_key = f"aud:{tenant_id}:{event_id}"
        record = self._get_record_by_id(aud_key, tenant_id)
        if not record:
            return None

        actor = AuditActor(
            user_id=record["actor"]["user_id"],
            role=record["actor"]["role"],
            ip_address=record["actor"]["ip_address"]
        )
        payload = AuditPayload(
            action=record["payload"]["action"],
            entity_type=record["payload"]["entity_type"],
            entity_id=record["payload"]["entity_id"],
            before_state=record["payload"]["before_state"],
            after_state=record["payload"]["after_state"]
        )

        return AuditEvent(
            event_id=record["event_id"],
            tenant_id=record["tenant_id"],
            actor=actor,
            payload=payload,
            timestamp=record["timestamp"],
            log_hash=record["log_hash"],
            version=record["version"]
        )

    def list_events(
        self,
        tenant_id: str,
        actor_id: str | None = None,
        action: str | None = None
    ) -> list[AuditEvent]:
        """Lists and filters audit logs for the tenant."""
        with self._lock:
            results = []
            for r in self._records.values():
                if r.get("id", "").startswith("aud:") and r.get("tenant_id") == tenant_id:
                    # Match optional actor filter
                    if actor_id and r["actor"]["user_id"] != actor_id:
                        continue
                    # Match optional action filter
                    if action and r["payload"]["action"] != action:
                        continue

                    actor = AuditActor(
                        user_id=r["actor"]["user_id"],
                        role=r["actor"]["role"],
                        ip_address=r["actor"]["ip_address"]
                    )
                    payload = AuditPayload(
                        action=r["payload"]["action"],
                        entity_type=r["payload"]["entity_type"],
                        entity_id=r["payload"]["entity_id"],
                        before_state=r["payload"]["before_state"],
                        after_state=r["payload"]["after_state"]
                    )
                    results.append(
                        AuditEvent(
                            event_id=r["event_id"],
                            tenant_id=r["tenant_id"],
                            actor=actor,
                            payload=payload,
                            timestamp=r["timestamp"],
                            log_hash=r["log_hash"],
                            version=r["version"]
                        )
                    )
            # Sort descending by timestamp, preserving latest-inserted-first for equal timestamps
            results.sort(key=lambda x: x.timestamp)
            results.reverse()
            return results

    def get_last_event_hash(self, tenant_id: str) -> str:
        """Resolves the log_hash of the most recently inserted event to enable chaining."""
        events = self.list_events(tenant_id)
        if not events:
            return "GENESIS"
        # Since list_events is sorted descending, the first one is the latest
        return events[0].log_hash
