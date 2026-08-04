"""
events.py
Domain events emitted by the Ingestion aggregate. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class DocumentIngestedEvent(DomainEvent):
    """
    Event emitted when a document is successfully saved and registered.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        filename: str,
        source: str,
        storage_path: str,
        hash_sha256: str,
        organization_id: str | None = None,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.filename = filename
        self.source = source
        self.storage_path = storage_path
        self.hash_sha256 = hash_sha256


class DocumentIntakeFailedEvent(DomainEvent):
    """
    Event emitted when ingestion validation or storage fails.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        filename: str,
        reason: str,
        organization_id: str | None = None,
        correlation_id: str = "",
        trace_id: str = "",
        user_id: str = "system",
        version: int = 1,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            user_id=user_id,
            version=version,
            occurred_at=occurred_at
        )
        self.filename = filename
        self.reason = reason
