"""
in_memory_storage.py
In-memory multi-tenant isolated document storage adapter supporting encryption, retention, and lifecycle.
"""

from datetime import datetime
from src.application.ports.idocument_storage import IDocumentStorage
from src.domain.common.exceptions import DomainException


class InMemoryStorage(IDocumentStorage):
    """
    In-memory isolated storage adapter mimicking S3 tenant separation and encryption at rest.

    Purpose:
        Ensure directory-level segmentation, customer keys (SSE-C), and retention holds.
    Business Reasoning:
        Clinical documents must be strictly isolated to avoid cross-tenant access.
    """

    def __init__(self) -> None:
        # Structure: tenant_id -> storage_path -> {data, key, retention_until, status}
        self._storage: dict[str, dict[str, dict[str, Any]]] = {}

    def save(
        self,
        filepath: str,
        data: bytes,
        tenant_id: str,
        encryption_key: str | None = None,
        retention_days: int | None = None
    ) -> str:
        """
        Saves raw bytes into the tenant-specific namespace folder path.
        """
        if tenant_id not in self._storage:
            self._storage[tenant_id] = {}

        # 1. Enforce active retention check on overwrite
        if filepath in self._storage[tenant_id]:
            existing = self._storage[tenant_id][filepath]
            ret_until = existing.get("retention_until")
            if ret_until:
                # Parse date to evaluate lock status
                try:
                    lock_date = datetime.fromisoformat(ret_until)
                    if datetime.now() < lock_date:
                        raise PermissionError(
                            f"File {filepath} is locked under active retention hold until {ret_until}"
                        )
                except ValueError:
                    pass

        # 2. Simulate Server-Side Encryption (SSE-C)
        processed_data = data
        if encryption_key:
            # Simple reversable transform to simulate encryption
            processed_data = bytes(reversed(data))

        # 3. Calculate retention date
        retention_until_str = None
        if retention_days:
            # We can calculate datetime or set mock
            import datetime as dt
            retention_until_str = (dt.datetime.now() + dt.timedelta(days=retention_days)).isoformat()

        self._storage[tenant_id][filepath] = {
            "data": processed_data,
            "encryption_key": encryption_key,
            "retention_until": retention_until_str,
            "status": "ACTIVE"
        }
        return filepath

    def get(
        self,
        storage_path: str,
        tenant_id: str,
        decryption_key: str | None = None
    ) -> bytes:
        """
        Retrieves file bytes from target tenant partitioned directory.
        """
        if tenant_id not in self._storage or storage_path not in self._storage[tenant_id]:
            raise DomainException(
                message=f"File not found in tenant storage: {storage_path}",
                code="FILE_NOT_FOUND"
            )

        record = self._storage[tenant_id][storage_path]

        # 1. Check lifecycle archiving status
        if record.get("status") == "ARCHIVED":
            raise PermissionError(
                f"Object {storage_path} is archived in cold storage. Restore it first."
            )

        # 2. Verify decryption key (SSE-C) matches
        stored_key = record.get("encryption_key")
        if stored_key and stored_key != decryption_key:
            raise PermissionError("Decryption failed: Incorrect key")

        data = record["data"]
        # Decrypt if key was used
        if stored_key:
            data = bytes(reversed(data))

        return data

    def apply_lifecycle_policy(
        self,
        tenant_id: str,
        rule_name: str,
        days_to_archive: int
    ) -> None:
        """
        Transitions active files belonging to a tenant to archived state.
        """
        if tenant_id in self._storage:
            for path in self._storage[tenant_id]:
                self._storage[tenant_id][path]["status"] = "ARCHIVED"

    def apply_retention_hold(
        self,
        storage_path: str,
        tenant_id: str,
        until_date: str
    ) -> None:
        """
        Locks a file from overwrite/deletion.
        """
        if tenant_id in self._storage and storage_path in self._storage[tenant_id]:
            self._storage[tenant_id][storage_path]["retention_until"] = until_date
