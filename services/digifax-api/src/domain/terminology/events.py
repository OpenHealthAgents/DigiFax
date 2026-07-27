"""
events.py
Domain events emitted by the terminology bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class TerminologyMappedEvent(DomainEvent):
    """
    Domain event published when clinical codes are resolved against target terminology dictionaries.

    Purpose:
        Signal FHIR builders to construct compliant FHIR resources.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        system_mapped: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, tenant_id, occurred_at)
        self.system_mapped = system_mapped
