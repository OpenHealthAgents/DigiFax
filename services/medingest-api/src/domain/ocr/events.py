"""
events.py
Domain events emitted by the OCR bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class OcrCompletedEvent(DomainEvent):
    """
    Domain event published when OCR engine completes text extraction for a document.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        engine_name: str,
        execution_time_seconds: float,
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
        self.engine_name = engine_name
        self.execution_time_seconds = execution_time_seconds
