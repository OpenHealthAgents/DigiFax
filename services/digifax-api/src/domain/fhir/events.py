"""
events.py
Domain events emitted by the FHIR bounded context. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class FhirResourceGeneratedEvent(DomainEvent):
    """
    Domain event published when clinical faxes are compiled to FHIR bundles.

    Purpose:
        Trigger outbound integrations export workers.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        resource_type: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, tenant_id, occurred_at)
        self.resource_type = resource_type
