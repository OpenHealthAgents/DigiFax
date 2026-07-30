"""
in_memory_tenant_branding_repository.py
In-memory persistence adapter for TenantBranding aggregate.
"""

from typing import Any
from src.application.ports.itenant_branding_repository import ITenantBrandingRepository
from src.domain.tenant_branding.entities import TenantBranding
from src.domain.tenant_branding.value_objects import (
    ColorPalette, 
    Typography, 
    ContactSupport, 
    EmailBranding, 
    CustomAssets, 
    DocumentAssets,
    BrandingTheme,
    LogoSettings,
    CustomDomain
)
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTenantBrandingRepository(BaseInMemoryRepository, ITenantBrandingRepository):
    """
    Thread-safe in-memory adapter isolating TenantBranding queries logically.
    """

    def __init__(self) -> None:
        super().__init__()

    def save(self, branding: TenantBranding) -> None:
        """
        Saves or updates the TenantBranding aggregate record.
        """
        record_data = {
            "id": branding.tenant_id,
            "tenant_id": branding.tenant_id,
            "company_name": branding.company_name,
            "theme": {
                "palette": {
                    "primary": branding.theme.palette.primary,
                    "secondary": branding.theme.palette.secondary,
                    "accent": branding.theme.palette.accent,
                    "background": branding.theme.palette.background
                },
                "typography": {
                    "font_family": branding.theme.typography.font_family,
                    "font_size_base": branding.theme.typography.font_size_base
                },
                "dark_mode_preferred": branding.theme.dark_mode_preferred
            },
            "logo_settings": {
                "light_logo_url": branding.logo_settings.light_logo_url,
                "dark_logo_url": branding.logo_settings.dark_logo_url,
                "fav_icon_url": branding.logo_settings.fav_icon_url
            },
            "support_info": {
                "support_email": branding.support_info.support_email,
                "support_phone": branding.support_info.support_phone,
                "support_website": branding.support_info.support_website
            },
            "email_branding": {
                "primary_color": branding.email_branding.primary_color,
                "header_html": branding.email_branding.header_html,
                "footer_html": branding.email_branding.footer_html
            },
            "custom_assets": {
                "login_background_url": branding.custom_assets.login_background_url,
                "dashboard_banner_url": branding.custom_assets.dashboard_banner_url
            },
            "document_assets": {
                "watermark_text_or_url": branding.document_assets.watermark_text_or_url,
                "report_header_html": branding.document_assets.report_header_html,
                "report_footer_html": branding.document_assets.report_footer_html
            },
            "footer_text": branding.footer_text,
            "custom_domain": {
                "hostname": branding.custom_domain.hostname,
                "status": branding.custom_domain.status,
                "ssl_configured": branding.custom_domain.ssl_configured
            } if branding.custom_domain else None,
            "version": getattr(branding, "version", 1)
        }

        # Call base save executing OCC version check
        self._save_record(branding.tenant_id, record_data)
        
        saved_record = self._records[branding.tenant_id]
        branding.version = saved_record["version"]

    def get_by_tenant_id(self, tenant_id: str) -> TenantBranding | None:
        """
        Loads a TenantBranding record scoped to a specific tenant ID.
        """
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        palette = ColorPalette(
            primary=record["theme"]["palette"]["primary"],
            secondary=record["theme"]["palette"]["secondary"],
            accent=record["theme"]["palette"]["accent"],
            background=record["theme"]["palette"]["background"]
        )
        typography = Typography(
            font_family=record["theme"]["typography"]["font_family"],
            font_size_base=record["theme"]["typography"]["font_size_base"]
        )
        theme = BrandingTheme(
            palette=palette,
            typography=typography,
            dark_mode_preferred=record["theme"]["dark_mode_preferred"]
        )
        logos = LogoSettings(
            light_logo_url=record["logo_settings"]["light_logo_url"],
            dark_logo_url=record["logo_settings"]["dark_logo_url"],
            fav_icon_url=record["logo_settings"]["fav_icon_url"]
        )
        support = ContactSupport(
            support_email=record["support_info"]["support_email"],
            support_phone=record["support_info"]["support_phone"],
            support_website=record["support_info"]["support_website"]
        )
        emails = EmailBranding(
            primary_color=record["email_branding"]["primary_color"],
            header_html=record["email_branding"]["header_html"],
            footer_html=record["email_branding"]["footer_html"]
        )
        assets = CustomAssets(
            login_background_url=record["custom_assets"]["login_background_url"],
            dashboard_banner_url=record["custom_assets"]["dashboard_banner_url"]
        )
        docs = DocumentAssets(
            watermark_text_or_url=record["document_assets"]["watermark_text_or_url"],
            report_header_html=record["document_assets"]["report_header_html"],
            report_footer_html=record["document_assets"]["report_footer_html"]
        )
        domain = None
        if record["custom_domain"]:
            domain = CustomDomain(
                hostname=record["custom_domain"]["hostname"],
                status=record["custom_domain"]["status"],
                ssl_configured=record["custom_domain"]["ssl_configured"]
            )

        branding = TenantBranding(
            tenant_id=record["tenant_id"],
            company_name=record["company_name"],
            theme=theme,
            logo_settings=logos,
            support_info=support,
            email_branding=emails,
            custom_assets=assets,
            document_assets=docs,
            footer_text=record["footer_text"],
            custom_domain=domain,
            version=record["version"]
        )
        return branding
