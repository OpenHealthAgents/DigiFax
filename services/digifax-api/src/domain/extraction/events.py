"""
events.py
Domain events emitted by the extraction bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class ExtractionCompletedEvent(DomainEvent):
    """
    Domain event published when clinical attributes are extracted via AI.

    Purpose:
        Signal validation services to enforce rule constraints.
    Business Reasoning:
        Asynchronously triggers downstream medical validation pipelines.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        extractor_engine: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, tenant_id, occurred_at)
        self.extractor_engine = extractor_engine
