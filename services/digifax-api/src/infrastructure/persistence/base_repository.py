"""
base_repository.py
Thread-safe, generic base in-memory repository implementing multi-tenancy and transactional safety policies.
"""

import threading
from datetime import datetime


class ConcurrencyException(Exception):
    """Exception raised when an optimistic concurrency version check fails."""
    pass


class BaseInMemoryRepository:
    """
    Base class for thread-safe in-memory repositories.

    Purpose:
        Encapsulate tenant isolation, soft deletes, auditing, concurrency checks, and pagination.
    Business Reasoning:
        Standardizes database features across repositories to prevent code duplication.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, dict] = {}

    def _save_record(self, record_id: str, data: dict, user_id: str | None = None) -> None:
        """
        Saves or updates a record, executing optimistic concurrency (version) validations.

        Purpose:
            Persist data with auditing and OCC version checks.
        Business Reasoning:
            Prevents concurrent write race conditions.
        Inputs:
            record_id (str): Primary key.
            data (dict): Record dict payload.
            user_id (str): Creator/Updater ID.
        Outputs:
            None.
        Assumptions:
            Data contains 'tenant_id'.
        Edge Cases:
            Throws ConcurrencyException if version mismatches on update.
        """
        with self._lock:
            now = datetime.now()
            
            if record_id in self._records:
                # Update flow
                existing = self._records[record_id]
                expected_version = data.get("version", 1)
                actual_version = existing.get("version", 1)
                
                if expected_version != actual_version:
                    raise ConcurrencyException(
                        f"Concurrency conflict on record {record_id}: "
                        f"expected version {expected_version}, actual is {actual_version}"
                    )
                
                # Update audit fields and increment version
                data["version"] = actual_version + 1
                data["created_at"] = existing.get("created_at")
                data["created_by"] = existing.get("created_by")
                data["updated_at"] = now
                data["updated_by"] = user_id
                data["is_deleted"] = existing.get("is_deleted", False)
                data["deleted_at"] = existing.get("deleted_at")
                data["deleted_by"] = existing.get("deleted_by")
            else:
                # Insert flow
                data["version"] = 1
                data["created_at"] = now
                data["created_by"] = user_id
                data["updated_at"] = now
                data["updated_by"] = user_id
                data["is_deleted"] = False
                data["deleted_at"] = None
                data["deleted_by"] = None

            self._records[record_id] = dict(data)

    def _get_record_by_id(
        self,
        record_id: str,
        tenant_id: str,
        organization_id: str | None = None,
        include_deleted: bool = False
    ) -> dict | None:
        """
        Retrieves a record, applying strict tenant/organization isolation and soft delete exclusions.

        Purpose:
            Load a record securely.
        Business Reasoning:
            Prevents cross-tenant leak vectors.
        """
        with self._lock:
            record = self._records.get(record_id)
            if not record:
                return None

            # Enforce Tenant Isolation
            if record.get("tenant_id") != tenant_id:
                return None

            # Enforce optional Organization Isolation
            if organization_id and record.get("organization_id") != organization_id:
                return None

            # Enforce Soft Deletes exclusions
            if record.get("is_deleted") and not include_deleted:
                return None

            return dict(record)

    def _soft_delete_record(self, record_id: str, tenant_id: str, user_id: str | None = None) -> None:
        """
        Marks a record as deleted logically.

        Purpose:
            Soft delete data.
        Business Reasoning:
            Maintains compliance retention rules.
        """
        with self._lock:
            record = self._records.get(record_id)
            if not record or record.get("tenant_id") != tenant_id:
                return

            record["is_deleted"] = True
            record["deleted_at"] = datetime.now()
            record["deleted_by"] = user_id

    def _list_records(
        self,
        tenant_id: str,
        organization_id: str | None = None,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Queries and paginates records under tenant bounds.

        Purpose:
            Enforce lists isolation and pagination limits.
        """
        with self._lock:
            filtered = []
            for record in self._records.values():
                # Filter by Tenant
                if record.get("tenant_id") != tenant_id:
                    continue

                # Filter by Org
                if organization_id and record.get("organization_id") != organization_id:
                    continue

                # Filter soft deletes
                if record.get("is_deleted") and not include_deleted:
                    continue

                filtered.append(dict(record))

            # Apply offset/limit pagination
            total_count = len(filtered)
            paginated = filtered[offset : offset + limit]

            return paginated, total_count
