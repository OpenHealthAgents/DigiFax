"""
test_migration.py
Unit tests asserting MigrationUtility operations, default tenant mappings, and rollbacks.
"""

import pytest

from src.infrastructure.persistence.in_memory_tenant_repository import InMemoryTenantRepository
from src.infrastructure.persistence.in_memory_intake_repository import InMemoryIntakeDocumentRepository
from src.infrastructure.auth.better_auth_adapter import BetterAuthAdapter
from src.infrastructure.persistence.migration_utility import MigrationUtility


def test_migration_and_rollback_flow() -> None:
    # 1. Setup target adapters and repositories
    tenant_repo = InMemoryTenantRepository()
    intake_repo = InMemoryIntakeDocumentRepository()
    auth_service = BetterAuthAdapter()
    
    # Setup mock workflows dictionary
    workflow_registry = {
        "wf-998": {"id": "wf-998", "tenant_id": "single-tenant", "status": "RUNNING"},
        "wf-999": {"id": "wf-999", "tenant_id": "", "status": "COMPLETED"}
    }

    # 2. Seed "single-tenant" legacy data
    # Pre-seed user with no tenant_id scope
    auth_service._mock_users["legacy-user@hospital.org"] = {
        "user_id": "usr-legacy-9",
        "memberships": {"org-main": "CLINICAL_REVIEWER"}
    }

    # Pre-seed document record with "single-tenant" designation
    intake_repo._save_record("doc-legacy-1", {
        "id": "doc-legacy-1",
        "tenant_id": "single-tenant",
        "filename": "old_chart.pdf",
        "content_type": "application/pdf",
        "size_bytes": 1024,
        "hash_sha256": "abc",
        "storage_path": "old/path.pdf",
        "status": "INGESTED"
    })

    # Assert pre-migration state is indeed single-tenant
    assert "tenant_id" not in auth_service._mock_users["legacy-user@hospital.org"]
    assert intake_repo._records["doc-legacy-1"]["tenant_id"] == "single-tenant"
    assert workflow_registry["wf-998"]["tenant_id"] == "single-tenant"

    # 3. Execute Migration
    utility = MigrationUtility(tenant_repo, intake_repo, auth_service, workflow_registry)
    report = utility.execute_migration(default_tenant_id="tenant-default")

    # Assert report summary counts
    assert report["status"] == "Success"
    assert report["migrated_users"] == 2
    assert report["migrated_documents"] == 1
    assert report["migrated_workflows"] == 2
    assert report["default_tenant_id"] == "tenant-default"

    # Assert multi-tenant mappings are enforced
    assert auth_service._mock_users["legacy-user@hospital.org"]["tenant_id"] == "tenant-default"
    assert intake_repo._records["doc-legacy-1"]["tenant_id"] == "tenant-default"
    assert workflow_registry["wf-998"]["tenant_id"] == "tenant-default"
    assert workflow_registry["wf-999"]["tenant_id"] == "tenant-default"

    # Check that default tenant registry is persisted
    default_tenant = tenant_repo.get_by_id("tenant-default")
    assert default_tenant is not None
    assert default_tenant.name == "Default Healthcare Network"

    # 4. Trigger Rollback
    utility.rollback()

    # Assert records returned to their original legacied state
    assert "tenant_id" not in auth_service._mock_users["legacy-user@hospital.org"]
    assert intake_repo._records["doc-legacy-1"]["tenant_id"] == "single-tenant"
    assert workflow_registry["wf-998"]["tenant_id"] == "single-tenant"
    assert workflow_registry["wf-999"]["tenant_id"] == ""


def test_rollback_preconditions() -> None:
    tenant_repo = InMemoryTenantRepository()
    intake_repo = InMemoryIntakeDocumentRepository()
    auth_service = BetterAuthAdapter()
    
    utility = MigrationUtility(tenant_repo, intake_repo, auth_service)
    
    # Try rollback prior to backup/migration
    with pytest.raises(RuntimeError):
        utility.rollback()
