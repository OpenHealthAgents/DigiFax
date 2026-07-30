"""
events.py
Domain Events raised by the Tenant Branding bounded context.
"""

from src.domain.common.domain_event import DomainEvent


class BrandingUpdatedEvent(DomainEvent):
    """Event raised when a Tenant modifies theme colors, logos, or font assets."""
    
    def __init__(self, tenant_id: str, changes: dict):
        super().__init__(
            aggregate_id=tenant_id,
            tenant_id=tenant_id
        )
        self.changes = changes


class CustomDomainConfiguredEvent(DomainEvent):
    """Event raised when a Custom Domain hostname is requested for routing."""
    
    def __init__(self, tenant_id: str, hostname: str):
        super().__init__(
            aggregate_id=tenant_id,
            tenant_id=tenant_id
        )
        self.hostname = hostname


class CustomDomainVerifiedEvent(DomainEvent):
    """Event raised when custom domain DNS certificate assertions pass successfully."""
    
    def __init__(self, tenant_id: str, hostname: str):
        super().__init__(
            aggregate_id=tenant_id,
            tenant_id=tenant_id
        )
        self.hostname = hostname
