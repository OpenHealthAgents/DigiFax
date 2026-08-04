"""
iaudit_repository.py
Outbound port repository interface for clinical audit event logs.
"""

from abc import ABC, abstractmethod
from src.domain.audit.entities import AuditEvent


class IAuditRepository(ABC):
    """
    Interface for persistence of immutable AuditEvent records.
    """

    @abstractmethod
    def save_event(self, event: AuditEvent) -> None:
        """Saves a signed audit event log."""
        pass

    @abstractmethod
    def get_event(self, tenant_id: str, event_id: str) -> AuditEvent | None:
        """Loads a signed audit event log."""
        pass

    @abstractmethod
    def list_events(
        self,
        tenant_id: str,
        actor_id: str | None = None,
        action: str | None = None
    ) -> list[AuditEvent]:
        """Lists and filters audit logs for the tenant."""
        pass

    @abstractmethod
    def get_last_event_hash(self, tenant_id: str) -> str:
        """Resolves the log_hash of the most recently inserted event to enable chaining."""
        pass
