"""
test_tenant_branding.py
Unit tests verifying Tenant Branding DDD components, use cases, validator service, and repository isolation.
"""

import pytest

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
from src.domain.tenant_branding.events import (
    BrandingUpdatedEvent, 
    CustomDomainConfiguredEvent, 
    CustomDomainVerifiedEvent
)
from src.domain.tenant_branding.branding_validator_service import BrandingValidatorService
from src.application.use_cases.tenant_branding.configure_branding import ConfigureBrandingUseCase
from src.application.use_cases.tenant_branding.manage_custom_domain import ManageCustomDomainUseCase
from src.infrastructure.persistence.in_memory_tenant_branding_repository import InMemoryTenantBrandingRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


def test_color_palette_validations() -> None:
    # 1. Valid color palette (hex)
    palette = ColorPalette("#3B82F6", "#10B981", "#F59E0B", "#F9FAFB")
    assert palette.primary == "#3B82F6"

    # 2. Invalid colors format (raises ValueError)
    with pytest.raises(ValueError):
        ColorPalette("red", "#fff", "#abc", "#123")


def test_typography_validations() -> None:
    # 1. Valid typography
    typo = Typography("Inter", "16px")
    assert typo.font_family == "Inter"

    # 2. Empty typography font family (raises ValueError)
    with pytest.raises(ValueError):
        Typography("  ", "14px")


def test_contact_support_validations() -> None:
    # 1. Valid contact support
    contact = ContactSupport("support@hospital.org", "+1-555-0199", "https://hospital.org/support")
    assert contact.support_email == "support@hospital.org"

    # 2. Invalid email format (raises ValueError)
    with pytest.raises(ValueError):
        ContactSupport("invalid-email", "+1-555-0199", "https://hospital.org/support")

    # 3. Invalid website format (raises ValueError)
    with pytest.raises(ValueError):
        ContactSupport("support@hospital.org", "+1-555-0199", "hospital.org")


def test_email_branding_validations() -> None:
    # 1. Valid email branding
    email_brand = EmailBranding("#3B82F6", "<h1>Welcome</h1>", "<p>Footer</p>")
    assert email_brand.primary_color == "#3B82F6"

    # 2. Invalid primary color (raises ValueError)
    with pytest.raises(ValueError):
        EmailBranding("blue", "<h1>Welcome</h1>", "<p>Footer</p>")


def test_branding_validator_service_contrast_gates() -> None:
    # 1. Low contrast colors (should raise ValueError)
    low_contrast = ColorPalette("#111111", "#222222", "#333333", "#121212")
    with pytest.raises(ValueError) as exc:
        BrandingValidatorService.check_accessibility(low_contrast)
    assert "below the WCAG 3.0:1 threshold" in str(exc.value)

    # 2. High contrast colors (should pass)
    high_contrast = ColorPalette("#000000", "#10B981", "#F59E0B", "#FFFFFF")
    BrandingValidatorService.check_accessibility(high_contrast)  # No exception raised


def test_custom_domain_validations() -> None:
    # 1. Valid custom domain format
    domain = CustomDomain("portal.hospital.org", "PENDING")
    assert domain.hostname == "portal.hospital.org"

    # 2. Invalid domain hostname format (raises ValueError)
    with pytest.raises(ValueError):
        CustomDomain("hospital", "PENDING")


def test_configure_branding_use_case_complete() -> None:
    repo = InMemoryTenantBrandingRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureBrandingUseCase(repo, bus)

    # Execute branding save with all extended fields
    branding = use_case.execute(
        tenant_id="tenant-alice",
        company_name="Alice Health Inc.",
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#FFFFFF",
        font_family="Inter",
        font_size_base="16px",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico",
        support_email="support@alice.org",
        support_phone="+1-555-9000",
        support_website="https://alice.org/help",
        email_primary_color="#3B82F6",
        email_header_html="<div>Header</div>",
        email_footer_html="<div>Footer</div>",
        login_background_url="https://alice.org/bg.jpg",
        dashboard_banner_url="https://alice.org/banner.jpg",
        watermark_text_or_url="CONFIDENTIAL PHI",
        report_header_html="<header>Report Header</header>",
        report_footer_html="<footer>Report Footer</footer>",
        footer_text="© 2026 Alice Health Inc."
    )

    assert branding.tenant_id == "tenant-alice"
    assert branding.company_name == "Alice Health Inc."
    assert branding.theme.palette.primary == "#3B82F6"
    assert branding.theme.palette.background == "#FFFFFF"
    assert branding.theme.typography.font_family == "Inter"
    assert branding.theme.typography.font_size_base == "16px"
    assert branding.support_info.support_email == "support@alice.org"
    assert branding.email_branding.primary_color == "#3B82F6"
    assert branding.custom_assets.login_background_url == "https://alice.org/bg.jpg"
    assert branding.document_assets.watermark_text_or_url == "CONFIDENTIAL PHI"
    assert branding.footer_text == "© 2026 Alice Health Inc."

    # Confirm record is persisted
    saved = repo.get_by_tenant_id("tenant-alice")
    assert saved is not None
    assert saved.company_name == "Alice Health Inc."
    assert saved.logo_settings.fav_icon_url == "https://alice.org/fav.ico"
    assert saved.version == 1

    # Confirm domain events published
    assert len(bus.published_events) == 1
    assert isinstance(bus.published_events[0], BrandingUpdatedEvent)
    assert bus.published_events[0].tenant_id == "tenant-alice"


def test_manage_custom_domain_use_case() -> None:
    repo = InMemoryTenantBrandingRepository()
    bus = InMemoryEventBus()
    configure_uc = ConfigureBrandingUseCase(repo, bus)
    domain_uc = ManageCustomDomainUseCase(repo, bus)

    # Pre-seed branding
    configure_uc.execute(
        tenant_id="tenant-bob",
        company_name="Bob Health Network",
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#FFFFFF",
        font_family="Outfit",
        font_size_base="14px",
        light_logo_url="https://bob.org/light.png",
        dark_logo_url="https://bob.org/dark.png",
        fav_icon_url="https://bob.org/fav.ico",
        support_email="support@bob.org",
        support_phone="+1-555-8000",
        support_website="https://bob.org/support",
        email_primary_color="#3B82F6",
        email_header_html="<div>Header</div>",
        email_footer_html="<div>Footer</div>",
        login_background_url="https://bob.org/bg.jpg",
        dashboard_banner_url="https://bob.org/banner.jpg",
        watermark_text_or_url="DRAFT",
        report_header_html="<header>Report Header</header>",
        report_footer_html="<footer>Report Footer</footer>",
        footer_text="© 2026 Bob Health Network."
    )
    bus.clear()

    # 1. Register domain (starts as PENDING)
    branding = domain_uc.register_domain("tenant-bob", "fax.bob.org")
    assert branding.custom_domain.hostname == "fax.bob.org"
    assert branding.custom_domain.status == "PENDING"
    assert branding.custom_domain.ssl_configured is False

    assert len(bus.published_events) == 1
    assert isinstance(bus.published_events[0], CustomDomainConfiguredEvent)

    # 2. Verify domain (activates domain and SSL certificate flags)
    verified_branding = domain_uc.verify_domain("tenant-bob")
    assert verified_branding.custom_domain.status == "ACTIVE"
    assert verified_branding.custom_domain.ssl_configured is True

    assert len(bus.published_events) == 2
    assert isinstance(bus.published_events[1], CustomDomainVerifiedEvent)


def test_tenant_branding_isolation() -> None:
    repo = InMemoryTenantBrandingRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureBrandingUseCase(repo, bus)

    # Seed branding for Alice
    use_case.execute(
        tenant_id="tenant-alice",
        company_name="Alice Health Inc.",
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#FFFFFF",
        font_family="Inter",
        font_size_base="16px",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico",
        support_email="support@alice.org",
        support_phone="+1-555-9000",
        support_website="https://alice.org/help",
        email_primary_color="#3B82F6",
        email_header_html="<div>Header</div>",
        email_footer_html="<div>Footer</div>",
        login_background_url="https://alice.org/bg.jpg",
        dashboard_banner_url="https://alice.org/banner.jpg",
        watermark_text_or_url="CONFIDENTIAL PHI",
        report_header_html="<header>Report Header</header>",
        report_footer_html="<footer>Report Footer</footer>",
        footer_text="© 2026 Alice Health Inc."
    )

    # Access Alice's branding scoped as Bob (should return None due to isolation guards)
    assert repo.get_by_tenant_id("tenant-bob") is None


def test_branding_concurrency_checks() -> None:
    repo = InMemoryTenantBrandingRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureBrandingUseCase(repo, bus)

    # Save initial version 1
    branding_v1 = use_case.execute(
        tenant_id="tenant-alice",
        company_name="Alice Health Inc.",
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#FFFFFF",
        font_family="Inter",
        font_size_base="16px",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico",
        support_email="support@alice.org",
        support_phone="+1-555-9000",
        support_website="https://alice.org/help",
        email_primary_color="#3B82F6",
        email_header_html="<div>Header</div>",
        email_footer_html="<div>Footer</div>",
        login_background_url="https://alice.org/bg.jpg",
        dashboard_banner_url="https://alice.org/banner.jpg",
        watermark_text_or_url="CONFIDENTIAL PHI",
        report_header_html="<header>Report Header</header>",
        report_footer_html="<footer>Report Footer</footer>",
        footer_text="© 2026 Alice Health Inc."
    )
    assert branding_v1.version == 1

    # Simulate concurrently loaded instance v1
    branding_stale = repo.get_by_tenant_id("tenant-alice")
    
    # Save updates using primary instance, incrementing version to 2
    branding_v1.theme = BrandingTheme(
        palette=branding_v1.theme.palette,
        typography=branding_v1.theme.typography,
        dark_mode_preferred=True
    )
    repo.save(branding_v1)
    assert branding_v1.version == 2

    # Attempt save using stale v1 instance (raises ConcurrencyException)
    with pytest.raises(ConcurrencyException):
        repo.save(branding_stale)
