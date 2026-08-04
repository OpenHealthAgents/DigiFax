"""
events.py
Domain events emitted by the validation bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class ValidationCompletedEvent(DomainEvent):
    """
    Domain event published when clinical data passes validation rules.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        is_valid: bool,
        error_count: int,
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
        self.is_valid = is_valid
        self.error_count = error_count
