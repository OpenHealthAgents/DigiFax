"""
events.py
Domain events emitted by the OCR bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class OcrCompletedEvent(DomainEvent):
    """
    Domain event published when OCR engine completes text extraction for a document.

    Purpose:
        Notify layout parser to process reading order and tables.
    Business Reasoning:
        Decouples OCR from layout analysis models.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        engine_name: str,
        execution_time_seconds: float,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, tenant_id, occurred_at)
        self.engine_name = engine_name
        self.execution_time_seconds = execution_time_seconds
