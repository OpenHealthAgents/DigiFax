"""
in_memory_tenant_branding_repository.py
In-memory persistence adapter for TenantBranding aggregate.
"""

from typing import Any
from src.application.ports.itenant_branding_repository import ITenantBrandingRepository
from src.domain.tenant_branding.entities import TenantBranding
from src.domain.tenant_branding.value_objects import ColorPalette, BrandingTheme, LogoSettings, CustomDomain
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
            "theme": {
                "palette": {
                    "primary": branding.theme.palette.primary,
                    "secondary": branding.theme.palette.secondary,
                    "accent": branding.theme.palette.accent,
                    "background": branding.theme.palette.background
                },
                "font_family": branding.theme.font_family,
                "dark_mode_preferred": branding.theme.dark_mode_preferred
            },
            "logo_settings": {
                "light_logo_url": branding.logo_settings.light_logo_url,
                "dark_logo_url": branding.logo_settings.dark_logo_url,
                "fav_icon_url": branding.logo_settings.fav_icon_url
            },
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
        theme = BrandingTheme(
            palette=palette,
            font_family=record["theme"]["font_family"],
            dark_mode_preferred=record["theme"]["dark_mode_preferred"]
        )
        logos = LogoSettings(
            light_logo_url=record["logo_settings"]["light_logo_url"],
            dark_logo_url=record["logo_settings"]["dark_logo_url"],
            fav_icon_url=record["logo_settings"]["fav_icon_url"]
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
            theme=theme,
            logo_settings=logos,
            custom_domain=domain,
            version=record["version"]
        )
        return branding
