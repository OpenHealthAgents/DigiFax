"""
test_tenant.py
Unit tests for the Tenant domain aggregate, configuration value objects, and repository adapters.
"""

import pytest

from src.domain.organizations.entities import Tenant, TenantStatus
from src.domain.organizations.value_objects import TenantConfiguration
from src.infrastructure.persistence.in_memory_tenant_repository import InMemoryTenantRepository


def test_tenant_configuration_success() -> None:
    config = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=["application/pdf"])
    assert config.max_daily_uploads == 50
    assert "application/pdf" in config.allowed_mime_types


def test_tenant_configuration_invalid_limit() -> None:
    with pytest.raises(ValueError):
        TenantConfiguration(max_daily_uploads=-10, allowed_mime_types=[])


def test_tenant_configuration_equality() -> None:
    config1 = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=["application/pdf"])
    config2 = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=["application/pdf"])
    config3 = TenantConfiguration(max_daily_uploads=100, allowed_mime_types=["application/pdf"])

    assert config1 == config2
    assert config1 != config3
    assert config1 != "not-a-config"


def test_tenant_creation_success() -> None:
    config = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=["application/pdf"])
    tenant = Tenant.create(id="tenant-abc", name="OpenHealth St. Jude", configuration=config)
    
    assert tenant.id == "tenant-abc"
    assert tenant.name == "OpenHealth St. Jude"
    assert tenant.status == TenantStatus.ACTIVE
    assert tenant.is_active() is True


def test_tenant_creation_empty_name() -> None:
    config = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=[])
    with pytest.raises(ValueError):
        Tenant.create(id="tenant-abc", name="   ", configuration=config)


def test_tenant_status_transitions() -> None:
    config = TenantConfiguration(max_daily_uploads=50, allowed_mime_types=[])
    tenant = Tenant.create(id="tenant-abc", name="OpenHealth St. Jude", configuration=config)
    
    # Suspend
    tenant.suspend()
    assert tenant.status == TenantStatus.SUSPENDED
    assert tenant.is_active() is False

    # Reactivate
    tenant.activate()
    assert tenant.status == TenantStatus.ACTIVE
    assert tenant.is_active() is True


def test_in_memory_tenant_repository() -> None:
    repo = InMemoryTenantRepository()
    config = TenantConfiguration(max_daily_uploads=10, allowed_mime_types=["image/tiff"])
    new_tenant = Tenant.create(id="tenant-custom", name="Custom Clinic", configuration=config)

    # Save
    repo.save(new_tenant)

    # Retrieve
    retrieved = repo.get_by_id("tenant-custom")
    assert retrieved is not None
    assert retrieved.id == "tenant-custom"
    assert retrieved.name == "Custom Clinic"
    assert retrieved.configuration.max_daily_uploads == 10
