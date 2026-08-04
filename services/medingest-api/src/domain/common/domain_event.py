"""
domain_event.py
Base domain event carrying transaction identities, tenant identifier, and tracing correlation scopes.
"""

from abc import ABC
from datetime import UTC, datetime
from src.domain.common.uuid import UniqueId


class DomainEvent(ABC):
    """
    Base class for all system domain events carrying compliance and audit trails metadata.

    Purpose:
        Unify messaging payloads to support partitioned downstream routing.
    Business Reasoning:
        Decoupled async pipelines must resolve tenant namespaces for logging and tracing.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        organization_id: str | None = None,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        if not tenant_id.strip():
            raise ValueError("tenant_id is required for domain events")
        self.event_id = UniqueId.generate()
        self.aggregate_id = aggregate_id
        self.tenant_id = tenant_id
        self.organization_id = organization_id
        self.correlation_id = correlation_id or str(UniqueId.generate())
        self.trace_id = trace_id or str(UniqueId.generate())
        self.user_id = user_id
        self.version = version
        self.occurred_at = occurred_at or datetime.now(UTC)
