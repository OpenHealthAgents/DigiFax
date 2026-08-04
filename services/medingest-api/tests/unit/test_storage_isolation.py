"""
test_storage_isolation.py
Unit tests asserting multi-tenant directory isolation, encryption, compliance locks, and lifecycle.
"""

from datetime import datetime, timedelta
import pytest

from src.domain.common.exceptions import DomainException
from src.infrastructure.storage.in_memory_storage import InMemoryStorage


def test_storage_tenant_isolation() -> None:
    storage = InMemoryStorage()
    content = b"critical patient data"
    path = "documents/patient_report.pdf"

    # Save under tenant-123
    storage.save(filepath=path, data=content, tenant_id="tenant-123")

    # Read back under tenant-123 should succeed
    assert storage.get(path, tenant_id="tenant-123") == content

    # Read under tenant-456 should raise FILE_NOT_FOUND
    with pytest.raises(DomainException) as exc_info:
        storage.get(path, tenant_id="tenant-456")
    assert exc_info.value.code == "FILE_NOT_FOUND"


def test_storage_encryption() -> None:
    storage = InMemoryStorage()
    content = b"extremely confidential file content"
    path = "raw/confidential.pdf"
    key = "super-secret-key"

    # Save with encryption key
    storage.save(filepath=path, data=content, tenant_id="tenant-123", encryption_key=key)

    # Retrieval without key or with wrong key should fail
    with pytest.raises(PermissionError):
        storage.get(path, tenant_id="tenant-123", decryption_key=None)

    with pytest.raises(PermissionError):
        storage.get(path, tenant_id="tenant-123", decryption_key="wrong-key")

    # Correct key decrypts correctly
    assert storage.get(path, tenant_id="tenant-123", decryption_key=key) == content


def test_storage_retention_hold() -> None:
    storage = InMemoryStorage()
    content = b"legal record"
    path = "raw/legal.pdf"

    # Save with retention hold
    storage.save(filepath=path, data=content, tenant_id="tenant-123", retention_days=5)

    # Overwrite attempt should fail
    with pytest.raises(PermissionError) as exc_info:
        storage.save(filepath=path, data=b"hacked record", tenant_id="tenant-123")
    assert "locked under active retention hold" in str(exc_info.value)


def test_storage_lifecycle_policy() -> None:
    storage = InMemoryStorage()
    content = b"old archives"
    path = "raw/old.pdf"

    storage.save(filepath=path, data=content, tenant_id="tenant-123")

    # Transition to cold storage archive
    storage.apply_lifecycle_policy(tenant_id="tenant-123", rule_name="ColdGlacierArchive", days_to_archive=30)

    # Fetch should fail because object is archived
    with pytest.raises(PermissionError) as exc_info:
        storage.get(path, tenant_id="tenant-123")
    assert "archived in cold storage" in str(exc_info.value)


def test_apply_retention_hold_directly() -> None:
    storage = InMemoryStorage()
    content = b"medical record"
    path = "raw/med.pdf"

    storage.save(filepath=path, data=content, tenant_id="tenant-123")
    
    # Apply manual retention hold until tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    storage.apply_retention_hold(path, tenant_id="tenant-123", until_date=tomorrow)

    # Overwrite attempt should fail
    with pytest.raises(PermissionError):
        storage.save(filepath=path, data=b"overwrite", tenant_id="tenant-123")


def test_invalid_retention_date_parsing() -> None:
    storage = InMemoryStorage()
    content = b"medical record"
    path = "raw/med.pdf"

    storage.save(filepath=path, data=content, tenant_id="tenant-123")
    storage.apply_retention_hold(path, tenant_id="tenant-123", until_date="invalid-date")

    # Overwrite attempt should succeed because parsing fails and defaults/ignores
    storage.save(filepath=path, data=b"overwrite", tenant_id="tenant-123")
    assert storage.get(path, tenant_id="tenant-123") == b"overwrite"

