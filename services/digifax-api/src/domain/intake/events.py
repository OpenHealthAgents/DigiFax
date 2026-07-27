"""
events.py
Domain events emitted by the Ingestion aggregate. Scoped by tenant.
"""

from datetime import datetime
from src.domain.common.domain_event import DomainEvent


class DocumentIngestedEvent(DomainEvent):
    """
    Event emitted when a document is successfully saved and registered.

    Purpose:
        Notify downstream subscribers (e.g. OCR parser, extraction agent) of a new document.
    Business Reasoning:
        Clinical pipelines process faxes asynchronously. Events decouple ingestion from OCR/AI workers.
    Inputs:
        aggregate_id (str): Document ID.
        tenant_id (str): Associated tenant ID.
        filename (str): Ingested filename.
        source (str): Intake channel type.
        storage_path (str): File location.
        hash_sha256 (str): Unique file checksum.
        occurred_at (datetime): Timestamp.
    Outputs:
        A DocumentIngestedEvent instance.
    Assumptions:
        None.
    Edge Cases:
        None.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        filename: str,
        source: str,
        storage_path: str,
        hash_sha256: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.tenant_id = tenant_id
        self.filename = filename
        self.source = source
        self.storage_path = storage_path
        self.hash_sha256 = hash_sha256


class DocumentIntakeFailedEvent(DomainEvent):
    """
    Event emitted when ingestion validation or storage fails.

    Purpose:
        Notify downstream systems (logging, alerts) of ingestion failure.
    Business Reasoning:
        Failure metrics must trace back to the initiating tenant for billing adjustments.
    Inputs:
        aggregate_id (str): Session ID.
        tenant_id (str): Associated tenant ID.
        filename (str): Filename.
        reason (str): Error description.
        occurred_at (datetime): Timestamp.
    Outputs:
        A DocumentIntakeFailedEvent instance.
    Assumptions:
        None.
    Edge Cases:
        None.
    """

    def __init__(
        self,
        aggregate_id: str,
        tenant_id: str,
        filename: str,
        reason: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.tenant_id = tenant_id
        self.filename = filename
        self.reason = reason
