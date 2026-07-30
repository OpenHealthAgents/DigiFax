"""
entities.py
Domain Entities and Aggregate Root for Tenant Branding.
"""

from typing import Any
from src.domain.common.entity import Entity
from src.domain.tenant_branding.value_objects import (
    BrandingTheme, 
    LogoSettings, 
    CustomDomain,
    ContactSupport,
    EmailBranding,
    CustomAssets,
    DocumentAssets
)
from src.domain.tenant_branding.events import (
    BrandingUpdatedEvent, 
    CustomDomainConfiguredEvent, 
    CustomDomainVerifiedEvent
)


class TenantBranding(Entity):
    """
    Aggregate Root representing white-label branding properties for a Tenant portal.
    
    Business Context:
        Clinical enterprise subscribers require unique vanity domains and styling guides
        to ensure unified practitioner experiences.
    """

    def __init__(
        self,
        tenant_id: str,
        company_name: str,
        theme: BrandingTheme,
        logo_settings: LogoSettings,
        support_info: ContactSupport,
        email_branding: EmailBranding,
        custom_assets: CustomAssets,
        document_assets: DocumentAssets,
        footer_text: str,
        custom_domain: CustomDomain | None = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.theme = theme
        self.logo_settings = logo_settings
        self.support_info = support_info
        self.email_branding = email_branding
        self.custom_assets = custom_assets
        self.document_assets = document_assets
        self.footer_text = footer_text
        self.custom_domain = custom_domain
        self.version = version
        self._domain_events = []

    def configure_branding(
        self,
        company_name: str,
        theme: BrandingTheme,
        logo_settings: LogoSettings,
        support_info: ContactSupport,
        email_branding: EmailBranding,
        custom_assets: CustomAssets,
        document_assets: DocumentAssets,
        footer_text: str
    ) -> None:
        """Updates styling theme, support contacts, emails, backgrounds, and document assets templates."""
        self.company_name = company_name
        self.theme = theme
        self.logo_settings = logo_settings
        self.support_info = support_info
        self.email_branding = email_branding
        self.custom_assets = custom_assets
        self.document_assets = document_assets
        self.footer_text = footer_text
        
        event = BrandingUpdatedEvent(
            tenant_id=self.tenant_id,
            changes={
                "company_name": company_name,
                "primary_color": theme.palette.primary,
                "font_family": theme.typography.font_family,
                "fav_icon_url": logo_settings.fav_icon_url,
                "support_email": support_info.support_email,
                "watermark_text": document_assets.watermark_text_or_url
            }
        )
        self._domain_events.append(event)

    def configure_custom_domain(self, hostname: str) -> None:
        """Requests custom routing subdomain setup."""
        self.custom_domain = CustomDomain(
            hostname=hostname,
            status="PENDING",
            ssl_configured=False
        )
        
        event = CustomDomainConfiguredEvent(
            tenant_id=self.tenant_id,
            hostname=hostname
        )
        self._domain_events.append(event)

    def verify_custom_domain(self) -> None:
        """Registers active DNS validation."""
        if not self.custom_domain:
            raise ValueError("No custom domain has been registered to verify.")

        self.custom_domain = CustomDomain(
            hostname=self.custom_domain.hostname,
            status="ACTIVE",
            ssl_configured=True
        )

        event = CustomDomainVerifiedEvent(
            tenant_id=self.tenant_id,
            hostname=self.custom_domain.hostname
        )
        self._domain_events.append(event)
