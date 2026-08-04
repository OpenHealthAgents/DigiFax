"""
idocument_storage.py
Outbound port interface defining isolated document storage behaviors.
"""

import abc


class IDocumentStorage(abc.ABC):
    """
    Outbound port interface for saving and retrieving raw document file bytes.

    Purpose:
        Enforce strict isolation, encryption at rest, and retention compliance.
    Business Reasoning:
        Clinical storage adapters must segregate tenant file directories to block leakages.
    """

    @abc.abstractmethod
    def save(
        self,
        filepath: str,
        data: bytes,
        tenant_id: str,
        encryption_key: str | None = None,
        retention_days: int | None = None
    ) -> str:
        """
        Saves the raw bytes to storage partitioned by tenant.

        Inputs:
            filepath (str): Target key location.
            data (bytes): Payload bytes.
            tenant_id (str): Associated tenant context.
            encryption_key (str): Optional customer key (SSE-C).
            retention_days (int): Optional retention hold lock period.
        Outputs:
            str: Resolved storage key path.
        """
        pass

    @abc.abstractmethod
    def get(
        self,
        storage_path: str,
        tenant_id: str,
        decryption_key: str | None = None
    ) -> bytes:
        """
        Retrieves raw file bytes from storage by its key/URI.

        Inputs:
            storage_path (str): Target key location.
            tenant_id (str): Fetching tenant context.
            decryption_key (str): Optional customer key.
        Outputs:
            bytes: Restored original document payload.
        """
        pass

    @abc.abstractmethod
    def apply_lifecycle_policy(
        self,
        tenant_id: str,
        rule_name: str,
        days_to_archive: int
    ) -> None:
        """
        Applies dynamic transitioning rules to archivable records.

        Inputs:
            tenant_id (str): Target tenant.
            rule_name (str): Compliance policy name.
            days_to_archive (int): Age threshold.
        """
        pass

    @abc.abstractmethod
    def apply_retention_hold(
        self,
        storage_path: str,
        tenant_id: str,
        until_date: str
    ) -> None:
        """
        Enforces a compliance legal/retention lock on storage records.

        Inputs:
            storage_path (str): Target key location.
            tenant_id (str): Tenant context.
            until_date (str): Timestamp until which deletions are blocked.
        """
        pass
