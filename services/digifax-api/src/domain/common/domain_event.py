"""
domain_event.py
Base domain event carrying transaction identities and tenant identifier.
"""

from abc import ABC
from datetime import UTC, datetime
from src.domain.common.uuid import UniqueId


class DomainEvent(ABC):
    """
    Base class for all system domain events.

    Purpose:
        Unify messaging payloads carrying tenant_id to support partitioned downstream routing.
    Business Reasoning:
        Decoupled async pipelines must resolve tenant namespaces for logging and tracing.
    """

    def __init__(self, aggregate_id: str, tenant_id: str, occurred_at: datetime | None = None):
        if not tenant_id.strip():
            raise ValueError("tenant_id is required for domain events")
        self._event_id = UniqueId.generate()
        self._aggregate_id = aggregate_id
        self._tenant_id = tenant_id
        self._occurred_at = occurred_at or datetime.now(UTC)

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at
