"""
test_tenant_branding.py
Unit tests verifying Tenant Branding DDD components, use cases, and repository isolation.
"""

import pytest

from src.domain.tenant_branding.entities import TenantBranding
from src.domain.tenant_branding.value_objects import ColorPalette, BrandingTheme, LogoSettings, CustomDomain
from src.domain.tenant_branding.events import (
    BrandingUpdatedEvent, 
    CustomDomainConfiguredEvent, 
    CustomDomainVerifiedEvent
)
from src.application.use_cases.tenant_branding.configure_branding import ConfigureBrandingUseCase
from src.application.use_cases.tenant_branding.manage_custom_domain import ManageCustomDomainUseCase
from src.infrastructure.persistence.in_memory_tenant_branding_repository import InMemoryTenantBrandingRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


def test_color_palette_validations() -> None:
    # 1. Valid color pallete (hex)
    palette = ColorPalette("#3B82F6", "#10B981", "#F59E0B", "#F9FAFB")
    assert palette.primary == "#3B82F6"

    # 2. Invalid colors format (raises ValueError)
    with pytest.raises(ValueError):
        ColorPalette("red", "#fff", "#abc", "#123")
    
    with pytest.raises(ValueError):
        ColorPalette("#3B82F6", "#10B981", "not-a-color", "#F9FAFB")


def test_custom_domain_validations() -> None:
    # 1. Valid custom domain format
    domain = CustomDomain("portal.hospital.org", "PENDING")
    assert domain.hostname == "portal.hospital.org"

    # 2. Invalid domain hostname format (raises ValueError)
    with pytest.raises(ValueError):
        CustomDomain("hospital", "PENDING")


def test_configure_branding_use_case() -> None:
    repo = InMemoryTenantBrandingRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureBrandingUseCase(repo, bus)

    # Execute branding save
    branding = use_case.execute(
        tenant_id="tenant-alice",
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#F9FAFB",
        font_family="Inter",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico"
    )

    assert branding.tenant_id == "tenant-alice"
    assert branding.theme.palette.primary == "#3B82F6"
    assert branding.theme.font_family == "Inter"

    # Confirm record is persisted
    saved = repo.get_by_tenant_id("tenant-alice")
    assert saved is not None
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
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#F9FAFB",
        font_family="Outfit",
        light_logo_url="https://bob.org/light.png",
        dark_logo_url="https://bob.org/dark.png",
        fav_icon_url="https://bob.org/fav.ico"
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
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#F9FAFB",
        font_family="Inter",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico"
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
        primary_color="#3B82F6",
        secondary_color="#10B981",
        accent_color="#F59E0B",
        background_color="#F9FAFB",
        font_family="Inter",
        light_logo_url="https://alice.org/light.png",
        dark_logo_url="https://alice.org/dark.png",
        fav_icon_url="https://alice.org/fav.ico"
    )
    assert branding_v1.version == 1

    # Simulate concurrently loaded instance v1
    branding_stale = repo.get_by_tenant_id("tenant-alice")
    
    # Save updates using primary instance, incrementing version to 2
    branding_v1.theme = BrandingTheme(
        palette=branding_v1.theme.palette,
        font_family="Inter",
        dark_mode_preferred=True
    )
    repo.save(branding_v1)
    assert branding_v1.version == 2

    # Attempt save using stale v1 instance (raises ConcurrencyException)
    with pytest.raises(ConcurrencyException):
        repo.save(branding_stale)
