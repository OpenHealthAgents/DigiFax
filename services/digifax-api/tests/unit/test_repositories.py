"""
test_repositories.py
Unit tests verifying multi-tenant repository isolation, soft deletes, auditing, OCC, and pagination.
"""

import pytest
from datetime import datetime

from src.infrastructure.persistence.base_repository import BaseInMemoryRepository, ConcurrencyException
from src.infrastructure.persistence.in_memory_intake_repository import InMemoryIntakeDocumentRepository
from src.domain.intake.entities import IntakeDocument
from src.domain.intake.value_objects import FileMetadata, IntakeSource


def test_base_repository_tenant_isolation() -> None:
    repo = BaseInMemoryRepository()
    
    # Save record for tenant-123
    repo._save_record("rec-1", {"id": "rec-1", "tenant_id": "tenant-123", "value": "A"})
    # Save record for tenant-456
    repo._save_record("rec-2", {"id": "rec-2", "tenant_id": "tenant-456", "value": "B"})

    # Query matching tenant ID
    res = repo._get_record_by_id("rec-1", "tenant-123")
    assert res is not None
    assert res["value"] == "A"

    # Query with mismatching tenant ID (Isolation enforcement)
    res_mismatch = repo._get_record_by_id("rec-1", "tenant-456")
    assert res_mismatch is None


def test_base_repository_soft_delete_and_auditing() -> None:
    repo = BaseInMemoryRepository()
    
    # Save new record (Auditing: created_at, created_by, version = 1)
    repo._save_record("rec-1", {"id": "rec-1", "tenant_id": "tenant-123"}, user_id="user-1")
    
    res = repo._get_record_by_id("rec-1", "tenant-123")
    assert res["version"] == 1
    assert res["created_by"] == "user-1"
    assert res["updated_by"] == "user-1"
    assert res["is_deleted"] is False

    # Soft Delete
    repo._soft_delete_record("rec-1", "tenant-123", user_id="user-deleter")
    
    # Query without include_deleted (should omit)
    assert repo._get_record_by_id("rec-1", "tenant-123") is None

    # Query with include_deleted (should return)
    res_deleted = repo._get_record_by_id("rec-1", "tenant-123", include_deleted=True)
    assert res_deleted is not None
    assert res_deleted["is_deleted"] is True
    assert res_deleted["deleted_by"] == "user-deleter"


def test_base_repository_optimistic_concurrency() -> None:
    repo = BaseInMemoryRepository()
    
    # Insert version 1
    repo._save_record("rec-1", {"id": "rec-1", "tenant_id": "tenant-123"})
    
    # Fetch record version
    record = repo._get_record_by_id("rec-1", "tenant-123")
    assert record["version"] == 1

    # Update success (version matches expected)
    record["value"] = "Updated"
    repo._save_record("rec-1", record)
    
    updated = repo._get_record_by_id("rec-1", "tenant-123")
    assert updated["version"] == 2
    assert updated["value"] == "Updated"

    # Update fail (version mismatch - simulates concurrent updates conflict)
    stale_record = {"id": "rec-1", "tenant_id": "tenant-123", "version": 1, "value": "Concurrent"}
    with pytest.raises(ConcurrencyException):
        repo._save_record("rec-1", stale_record)


def test_base_repository_pagination() -> None:
    repo = BaseInMemoryRepository()
    
    # Ingest 5 records
    for i in range(5):
        repo._save_record(f"rec-{i}", {"id": f"rec-{i}", "tenant_id": "tenant-123"})

    # Limit = 2, Offset = 0 (Page 1)
    page1, total = repo._list_records("tenant-123", limit=2, offset=0)
    assert len(page1) == 2
    assert total == 5
    assert page1[0]["id"] == "rec-0"
    assert page1[1]["id"] == "rec-1"

    # Limit = 2, Offset = 2 (Page 2)
    page2, _ = repo._list_records("tenant-123", limit=2, offset=2)
    assert len(page2) == 2
    assert page2[0]["id"] == "rec-2"
    assert page2[1]["id"] == "rec-3"


def test_intake_repository_operations() -> None:
    repo = InMemoryIntakeDocumentRepository()
    metadata = FileMetadata("report.pdf", "application/pdf", 100, "sha")
    doc = IntakeDocument("doc-1", "tenant-123", IntakeSource.FAX_UPLOAD, metadata, "raw/doc-1.pdf")

    # Save
    repo.save(doc)
    assert doc.version == 1

    # Get
    retrieved = repo.get_by_id("doc-1", "tenant-123")
    assert retrieved is not None
    assert retrieved.id == "doc-1"
    assert retrieved.version == 1

    # Update OCC
    doc.metadata.filename = "new_report.pdf"
    repo.save(doc)
    assert doc.version == 2

    # Listing paginated
    docs, total = repo.list_documents("tenant-123", limit=10, offset=0)
    assert len(docs) == 1
    assert total == 1
    assert docs[0].metadata.filename == "new_report.pdf"
