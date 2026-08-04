"""
migration_utility.py
Data migration utility mapping legacy single-tenant data structures to the multi-tenant model.
"""

import copy
import time
from datetime import datetime
from typing import Any

from src.domain.organizations.entities import Tenant as DomainTenant, TenantStatus
from src.domain.organizations.value_objects import TenantConfiguration


class MigrationUtility:
    """
    Utility class governing data transformation rules and database porting.

    Purpose:
        Perform migrations of users, faxes, and workflow logs into isolated tenant boundaries.
    Business Reasoning:
        Secures system transition to multi-tenancy without losing legacy operational records.
    """

    def __init__(
        self,
        tenant_repo: Any,
        intake_repo: Any,
        auth_service: Any,
        workflow_registry: dict[str, Any] | None = None
    ):
        self.tenant_repo = tenant_repo
        self.intake_repo = intake_repo
        self.auth_service = auth_service
        self.workflow_registry = workflow_registry if workflow_registry is not None else {}

        self._backup_tenant_records = None
        self._backup_intake_records = None
        self._backup_auth_users = None
        self._backup_workflows = None

    def backup(self) -> None:
        """
        Captures deep-copied state snapshots of databases/adapters prior to mutations.
        """
        self._backup_tenant_records = copy.deepcopy(self.tenant_repo._records)
        self._backup_intake_records = copy.deepcopy(self.intake_repo._records)
        self._backup_auth_users = copy.deepcopy(self.auth_service._mock_users)
        self._backup_workflows = copy.deepcopy(self.workflow_registry)

    def rollback(self) -> None:
        """
        Rollback procedure. Restores all repository and adapter states to target snapshots.
        """
        if self._backup_tenant_records is None:
            raise RuntimeError("Cannot rollback. No backup snapshot has been captured.")

        self.tenant_repo._records = copy.deepcopy(self._backup_tenant_records)
        self.intake_repo._records = copy.deepcopy(self._backup_intake_records)
        self.auth_service._mock_users = copy.deepcopy(self._backup_auth_users)
        self.workflow_registry.clear()
        self.workflow_registry.update(copy.deepcopy(self._backup_workflows))

    def execute_migration(self, default_tenant_id: str = "tenant-default") -> dict[str, Any]:
        """
        Executes the migration process.

        Steps:
            1. Creates target backup snapshot.
            2. Creates/asserts a default active tenant with standard configurations.
            3. Maps all user profiles memberships.
            4. Maps all inbound documents.
            5. Maps all workflow execution contexts.

        Inputs:
            default_tenant_id (str): ID namespace to bind records to.
        Outputs:
            dict: Structured migration summary report.
        """
        start_time = time.time()
        self.backup()

        migrated_users = 0
        migrated_documents = 0
        migrated_workflows = 0

        # 1. Create or Verify Default Tenant
        tenant = self.tenant_repo.get_by_id(default_tenant_id)
        if not tenant:
            default_config = TenantConfiguration(
                max_daily_uploads=1000,
                allowed_mime_types=["application/pdf", "image/tiff"],
                feature_flags={"auto_ocr": True, "beta_opt_in": ["ai_summarization"]}
            )
            tenant = DomainTenant(
                id=default_tenant_id,
                name="Default Healthcare Network",
                status=TenantStatus.ACTIVE,
                configuration=default_config
            )
            self.tenant_repo.save(tenant)

        # 2. Assign existing users to default tenant
        for email, user_data in self.auth_service._mock_users.items():
            if "tenant_id" not in user_data or user_data.get("tenant_id") != default_tenant_id:
                user_data["tenant_id"] = default_tenant_id
                migrated_users += 1

        # 3. Assign existing documents to default tenant
        for doc_id, doc_record in self.intake_repo._records.items():
            current_tenant = doc_record.get("tenant_id")
            if not current_tenant or current_tenant in ["", "none", "single-tenant"]:
                doc_record["tenant_id"] = default_tenant_id
                migrated_documents += 1

        # 4. Assign workflows to default tenant
        for wf_id, wf_record in self.workflow_registry.items():
            current_tenant = wf_record.get("tenant_id")
            if not current_tenant or current_tenant in ["", "none", "single-tenant"]:
                wf_record["tenant_id"] = default_tenant_id
                migrated_workflows += 1

        duration = time.time() - start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "Success",
            "default_tenant_id": default_tenant_id,
            "migrated_users": migrated_users,
            "migrated_documents": migrated_documents,
            "migrated_workflows": migrated_workflows,
            "duration_seconds": duration,
            "rollback_available": True
        }

        return report
