"""
manage_custom_domain.py
Use Case implementation allowing Tenant to register and verify DNS domain routing.
"""

from src.application.ports.itenant_branding_repository import ITenantBrandingRepository
from src.domain.common.event_bus import IEventBus
from src.domain.tenant_branding.entities import TenantBranding


class ManageCustomDomainUseCase:
    """
    Inbound Use Case registering and validating tenant vanity subdomains.
    """

    def __init__(self, repo: ITenantBrandingRepository, event_bus: IEventBus):
        self.repo = repo
        self.event_bus = event_bus

    def register_domain(self, tenant_id: str, hostname: str) -> TenantBranding:
        """Configures custom domain under PENDING status."""
        branding = self.repo.get_by_tenant_id(tenant_id)
        if not branding:
            raise ValueError(f"Visual branding must be configured for tenant {tenant_id} before domain setup.")

        branding.configure_custom_domain(hostname)
        self.repo.save(branding)

        # Dispatch events
        for event in branding._domain_events:
            self.event_bus.publish(event)
        branding._domain_events.clear()

        return branding

    def verify_domain(self, tenant_id: str) -> TenantBranding:
        """Confirms DNS verification and activates routing maps."""
        branding = self.repo.get_by_tenant_id(tenant_id)
        if not branding:
            raise ValueError(f"No branding setup located for tenant {tenant_id}.")

        branding.verify_custom_domain()
        self.repo.save(branding)

        # Dispatch events
        for event in branding._domain_events:
            self.event_bus.publish(event)
        branding._domain_events.clear()

        return branding
