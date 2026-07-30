"""
configure_branding.py
Use Case implementation allowing Tenant to update color themes and custom logos.
"""

from src.application.ports.itenant_branding_repository import ITenantBrandingRepository
from src.domain.common.event_bus import IEventBus
from src.domain.tenant_branding.entities import TenantBranding
from src.domain.tenant_branding.branding_validator_service import BrandingValidatorService
from src.domain.tenant_branding.value_objects import (
    ColorPalette, 
    Typography, 
    ContactSupport, 
    EmailBranding, 
    CustomAssets, 
    DocumentAssets,
    BrandingTheme,
    LogoSettings
)


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
        company_name: str,
        primary_color: str,
        secondary_color: str,
        accent_color: str,
        background_color: str,
        font_family: str,
        font_size_base: str,
        light_logo_url: str,
        dark_logo_url: str,
        fav_icon_url: str,
        support_email: str,
        support_phone: str,
        support_website: str,
        email_primary_color: str,
        email_header_html: str,
        email_footer_html: str,
        login_background_url: str,
        dashboard_banner_url: str,
        watermark_text_or_url: str,
        report_header_html: str,
        report_footer_html: str,
        footer_text: str,
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
        
        # Enforce domain validation rules: WCAG contrast check
        BrandingValidatorService.check_accessibility(palette)

        typography = Typography(
            font_family=font_family,
            font_size_base=font_size_base
        )
        theme = BrandingTheme(
            palette=palette,
            typography=typography,
            dark_mode_preferred=dark_mode_preferred
        )
        logos = LogoSettings(
            light_logo_url=light_logo_url,
            dark_logo_url=dark_logo_url,
            fav_icon_url=fav_icon_url
        )
        support = ContactSupport(
            support_email=support_email,
            support_phone=support_phone,
            support_website=support_website
        )
        emails = EmailBranding(
            primary_color=email_primary_color,
            header_html=email_header_html,
            footer_html=email_footer_html
        )
        assets = CustomAssets(
            login_background_url=login_background_url,
            dashboard_banner_url=dashboard_banner_url
        )
        docs = DocumentAssets(
            watermark_text_or_url=watermark_text_or_url,
            report_header_html=report_header_html,
            report_footer_html=report_footer_html
        )

        branding = self.repo.get_by_tenant_id(tenant_id)
        if not branding:
            branding = TenantBranding(
                tenant_id=tenant_id,
                company_name=company_name,
                theme=theme,
                logo_settings=logos,
                support_info=support,
                email_branding=emails,
                custom_assets=assets,
                document_assets=docs,
                footer_text=footer_text
            )
            # Dispatch event for initial creation
            from src.domain.tenant_branding.events import BrandingUpdatedEvent
            branding._domain_events.append(
                BrandingUpdatedEvent(
                    tenant_id=tenant_id,
                    changes={
                        "company_name": company_name,
                        "primary_color": primary_color,
                        "font_family": font_family,
                        "fav_icon_url": fav_icon_url,
                        "support_email": support_email,
                        "watermark_text": watermark_text_or_url
                    }
                )
            )
        else:
            branding.configure_branding(
                company_name=company_name,
                theme=theme,
                logo_settings=logos,
                support_info=support,
                email_branding=emails,
                custom_assets=assets,
                document_assets=docs,
                footer_text=footer_text
            )

        self.repo.save(branding)

        # Dispatch domain events
        for event in branding._domain_events:
            self.event_bus.publish(event)
        branding._domain_events.clear()

        return branding
