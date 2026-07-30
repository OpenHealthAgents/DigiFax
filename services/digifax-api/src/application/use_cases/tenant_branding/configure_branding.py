"""
configure_branding.py
Use Case implementation allowing Tenant to update color themes and custom logos.
"""

from src.application.ports.itenant_branding_repository import ITenantBrandingRepository
from src.domain.common.event_bus import IEventBus
from src.domain.tenant_branding.entities import TenantBranding
from src.domain.tenant_branding.value_objects import ColorPalette, BrandingTheme, LogoSettings


class ConfigureBrandingUseCase:
    """
    Inbound Use Case configuring visual branding assets for white-label portals.
    """

    def __init__(self, repo: ITenantBrandingRepository, event_bus: IEventBus):
        self.repo = repo
        self.event_bus = event_bus

    def execute(
        self,
        tenant_id: str,
        primary_color: str,
        secondary_color: str,
        accent_color: str,
        background_color: str,
        font_family: str,
        light_logo_url: str,
        dark_logo_url: str,
        fav_icon_url: str,
        dark_mode_preferred: bool = False
    ) -> TenantBranding:
        """
        Executes the branding update transaction.
        """
        palette = ColorPalette(
            primary=primary_color,
            secondary=secondary_color,
            accent=accent_color,
            background=background_color
        )
        theme = BrandingTheme(
            palette=palette,
            font_family=font_family,
            dark_mode_preferred=dark_mode_preferred
        )
        logos = LogoSettings(
            light_logo_url=light_logo_url,
            dark_logo_url=dark_logo_url,
            fav_icon_url=fav_icon_url
        )

        branding = self.repo.get_by_tenant_id(tenant_id)
        if not branding:
            branding = TenantBranding(
                tenant_id=tenant_id,
                theme=theme,
                logo_settings=logos
            )
            from src.domain.tenant_branding.events import BrandingUpdatedEvent
            branding._domain_events.append(
                BrandingUpdatedEvent(
                    tenant_id=tenant_id,
                    changes={
                        "primary_color": theme.palette.primary,
                        "font_family": theme.font_family,
                        "fav_icon_url": logos.fav_icon_url
                    }
                )
            )
        else:
            branding.configure_branding(theme, logos)

        self.repo.save(branding)

        # Dispatch domain events
        for event in branding._domain_events:
            self.event_bus.publish(event)
        branding._domain_events.clear()

        return branding
