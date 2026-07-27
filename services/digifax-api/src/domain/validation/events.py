"""
events.py
Domain events emitted by the validation bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class ValidationCompletedEvent(DomainEvent):
    """
    Domain event published when clinical data passes validation rules.

    Purpose:
        Approve document or alert clinical practitioners of validation errors.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        is_valid: bool,
        error_count: int,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, tenant_id, occurred_at)
        self.is_valid = is_valid
        self.error_count = error_count
