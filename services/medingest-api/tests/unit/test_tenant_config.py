"""
test_tenant_config.py
Unit tests verifying Tenant Configuration DDD components, services, repositories, use cases, and controllers.
"""

import pytest
from fastapi import HTTPException

from src.domain.tenant_config.entities import TenantConfiguration
from src.domain.tenant_config.value_objects import LocaleSettings, ClinicalFormats, RetentionSettings
from src.domain.tenant_config.events import TenantConfigurationUpdatedEvent
from src.domain.tenant_config.domain_services import ClinicalNumberingService
from src.application.use_cases.tenant_config.get_tenant_config import GetTenantConfigUseCase
from src.application.use_cases.tenant_config.configure_tenant_config import ConfigureTenantConfigUseCase
from src.infrastructure.persistence.in_memory_tenant_config_repository import InMemoryTenantConfigurationRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.controllers.tenant_config_controller import (
    ConfigureTenantConfigRequest,
    get_tenant_config,
    update_tenant_config
)
from src.application.common.tenant_context import TenantContext


def test_locale_settings_validations() -> None:
    # 1. Valid locale settings
    locale = LocaleSettings("YYYY-MM-DD", "HH:mm:ss", "UTC", "en", "USD", "en-US", "1,234.56")
    assert locale.timezone == "UTC"

    # 2. Invalid locale format
    with pytest.raises(ValueError):
        LocaleSettings("YYYY-MM-DD", "HH:mm:ss", "UTC", "en", "USD", "invalidlocale", "1,234.56")


def test_clinical_formats_validations() -> None:
    # 1. Valid formats
    formats = ClinicalFormats(r"PAT-\d{6}", r"MRN-\d{8}", r"DOC-\d{10}")
    assert formats.patient_id_format == r"PAT-\d{6}"

    # 2. Invalid regex pattern format (raises ValueError)
    with pytest.raises(ValueError):
        ClinicalFormats("PAT-[[[", r"MRN-\d{8}", r"DOC-\d{10}")


def test_retention_settings_validations() -> None:
    # 1. Valid retention
    ret = RetentionSettings(120)
    assert ret.default_retention_days == 120

    # 2. Invalid retention days < 1
    with pytest.raises(ValueError):
        RetentionSettings(0)


def test_clinical_numbering_service() -> None:
    formats = ClinicalFormats(r"PAT-\d{6}", r"MRN-\d{8}", r"DOC-\d{10}")

    # Patient ID check
    assert ClinicalNumberingService.validate_patient_id("PAT-123456", formats) is True
    assert ClinicalNumberingService.validate_patient_id("PAT-ABCDEF", formats) is False

    # MRN check
    assert ClinicalNumberingService.validate_mrn("MRN-98765432", formats) is True
    assert ClinicalNumberingService.validate_mrn("MRN-987654", formats) is False

    # Document number check
    assert ClinicalNumberingService.validate_document_number("DOC-1234567890", formats) is True
    assert ClinicalNumberingService.validate_document_number("DOC-123", formats) is False


def test_get_tenant_config_use_case_fallback() -> None:
    repo = InMemoryTenantConfigurationRepository()
    use_case = GetTenantConfigUseCase(repo)

    # Empty repository (unseeded tenant) should fallback to Global Defaults
    config = use_case.execute("tenant-new")
    assert config.tenant_id == "tenant-new"
    assert config.locale_settings.timezone == "UTC"
    assert config.locale_settings.locale == "en-US"
    assert config.clinical_formats.patient_id_format == r"PAT-\d{6}"
    assert config.retention_settings.default_retention_days == 365
    assert config.version == 1


def test_configure_tenant_config_use_case() -> None:
    repo = InMemoryTenantConfigurationRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureTenantConfigUseCase(repo, bus)

    # Configure custom settings
    config = use_case.execute(
        tenant_id="tenant-alice",
        date_format="DD/MM/YYYY",
        time_format="hh:mm A",
        timezone="America/New_York",
        language="en",
        currency="USD",
        locale="en-US",
        number_format="1.234,56",
        patient_id_format=r"ALICE-PAT-\d{4}",
        medical_record_format=r"ALICE-MRN-\d{6}",
        document_number_format=r"ALICE-DOC-\d{8}",
        default_retention_days=180
    )

    assert config.tenant_id == "tenant-alice"
    assert config.locale_settings.timezone == "America/New_York"
    assert config.clinical_formats.patient_id_format == r"ALICE-PAT-\d{4}"
    assert config.retention_settings.default_retention_days == 180
    assert config.version == 1

    # Check memory persistence
    saved = repo.get_by_tenant_id("tenant-alice")
    assert saved is not None
    assert saved.locale_settings.date_format == "DD/MM/YYYY"

    # Confirm domain event published
    assert len(bus.published_events) == 1
    assert isinstance(bus.published_events[0], TenantConfigurationUpdatedEvent)
    assert bus.published_events[0].tenant_id == "tenant-alice"


def test_repository_concurrency_and_isolation() -> None:
    repo = InMemoryTenantConfigurationRepository()
    bus = InMemoryEventBus()
    use_case = ConfigureTenantConfigUseCase(repo, bus)

    # Save initial version 1
    config_v1 = use_case.execute(
        tenant_id="tenant-bob",
        date_format="YYYY-MM-DD",
        time_format="HH:mm:ss",
        timezone="UTC",
        language="en",
        currency="EUR",
        locale="fr-FR",
        number_format="1 234,56",
        patient_id_format=r"BOB-PAT-\d{4}",
        medical_record_format=r"BOB-MRN-\d{6}",
        document_number_format=r"BOB-DOC-\d{8}",
        default_retention_days=90
    )
    assert config_v1.version == 1

    # Concurrent stale loads
    stale_config = repo.get_by_tenant_id("tenant-bob")

    # Update version to 2
    config_v1.retention_settings = RetentionSettings(120)
    repo.save(config_v1)
    assert config_v1.version == 2

    # Save attempt using stale loads triggers ConcurrencyException
    with pytest.raises(ConcurrencyException):
        repo.save(stale_config)

    # Logical isolation check: Bob's config shouldn't load for Alice
    assert repo.get_by_tenant_id("tenant-alice") is None


def test_api_controller_handlers() -> None:
    # Set up mock payload context
    context = TenantContext(
        tenant_id="tenant-alice",
        organization_id=None,
        user_id="user-1",
        roles=["CLINICAL_REVIEWER"],
        permissions=["document:read", "document:write"],
        subscription_tier="Enterprise",
        feature_flags={},
        locale="en-US",
        timezone="UTC",
        correlation_id="corr-1",
        trace_id="trace-1"
    )

    # 1. Test GET (resolves fallback default initially)
    get_res = get_tenant_config(context=context, use_case=GetTenantConfigUseCase(InMemoryTenantConfigurationRepository()))
    assert get_res["tenant_id"] == "tenant-alice"
    assert get_res["locale_settings"]["timezone"] == "UTC"
    assert get_res["retention_settings"]["default_retention_days"] == 365

    # 2. Test POST update
    payload = ConfigureTenantConfigRequest(
        date_format="DD-MM-YYYY",
        time_format="HH:mm",
        timezone="Europe/Paris",
        language="fr",
        currency="EUR",
        locale="fr-FR",
        number_format="1.234,56",
        patient_id_format=r"FR-PAT-\d{5}",
        medical_record_format=r"FR-MRN-\d{7}",
        document_number_format=r"FR-DOC-\d{9}",
        default_retention_days=90
    )

    repo = InMemoryTenantConfigurationRepository()
    post_res = update_tenant_config(
        payload=payload,
        context=context,
        use_case=ConfigureTenantConfigUseCase(repo, InMemoryEventBus())
    )
    assert post_res["status"] == "success"
    assert post_res["version"] == 1

    # Verify loaded model has correct settings
    saved = repo.get_by_tenant_id("tenant-alice")
    assert saved.locale_settings.timezone == "Europe/Paris"
