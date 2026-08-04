"""
entities.py
Ingestion document aggregate root, representing fax metadata and storage endpoints scoped by tenant.
"""

import enum

from src.domain.common.entity import AggregateRoot
from src.domain.intake.events import DocumentIngestedEvent, DocumentIntakeFailedEvent
from src.domain.intake.value_objects import FileMetadata, IntakeSource


class IntakeStatus(enum.StrEnum):
    """
    Enum representing document ingestion status.

    Purpose:
        Track document processing states.
    Business Reasoning:
        Allows users to filter documents by their ingestion stage.
    """
    INGESTED = "INGESTED"
    FAILED = "FAILED"


class IntakeDocument(AggregateRoot):
    """
    Aggregate Root representing an incoming clinical document ingestion session.

    Purpose:
        Catalog metadata, validation states, and file access locations for a fax transmission.
    Business Reasoning:
        Clinical documents must be indexed under strict ownership scopes to prevent unauthorized access.
    Inputs:
        id (str): Document unique identifier.
        tenant_id (str): Owner tenant UUID.
        source (IntakeSource): Ingestion pathway channel.
        metadata (FileMetadata): Ingested file size, hashes, and type.
        storage_path (str): File destination path on S3 storage.
        status (IntakeStatus): Current ingestion state.
    Outputs:
        An IntakeDocument aggregate root instance.
    Assumptions:
        The target tenant_id is active and verified before instantiation.
    Edge Cases:
        Validation warnings do not block instance creation but generate flags.
    """

    def __init__(
        self,
        id: str,
        tenant_id: str,
        source: IntakeSource,
        metadata: FileMetadata,
        storage_path: str,
        status: IntakeStatus = IntakeStatus.INGESTED
    ):
        """
        Initializes a new IntakeDocument instance.

        Detailed Parameter Breakdown:
          - id (str): The aggregate identity. This matches document_id generated globally.
          - tenant_id (str): The multi-tenant partition key. This is critical for PostgreSQL
            Row-Level Security (RLS) policies to avoid cross-tenant information disclosure.
          - source (IntakeSource): The pathway source (e.g. FAX_UPLOAD, EMAIL_ATTACHMENT,
            SCAN_UPLOAD, or API_UPLOAD). Tells the parsing worker which custom logic to use.
          - metadata (FileMetadata): Encapsulates validated metadata including size, mime types,
            extensions, and secure SHA-256 hash.
          - storage_path (str): The logical S3 object storage location path.
          - status (IntakeStatus): Tracks whether the document is successfully INGESTED or FAILED.
        """
        # Call the parent AggregateRoot constructor to initialize internal event list
        # and set the core aggregate root ID.
        super().__init__(id)

        # Enforce that every clinical entity MUST belong to a valid, non-blank tenant.
        # Failing this assertion is treated as an illegal state boundary.
        if not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        # Set domain fields ensuring strict logical segregation
        self.tenant_id = tenant_id
        self.source = source
        self.metadata = metadata
        self.storage_path = storage_path
        self.status = status

    @classmethod
    def create_ingested(
        cls,
        id: str,
        tenant_id: str,
        source: IntakeSource,
        metadata: FileMetadata,
        storage_path: str
    ) -> 'IntakeDocument':
        """
        Creates a successfully ingested document and publishes the event.

        Purpose:
            Instantiate and publish ingest confirmation domain events.
        Business Reasoning:
            Subsequent parsing stages (like OCR and LLM extraction) trigger asynchronously off domain events.
        Inputs:
            id (str): Document ID.
            tenant_id (str): Owner tenant ID.
            source (IntakeSource): Upload channel.
            metadata (FileMetadata): File metadata.
            storage_path (str): Storage path.
        Outputs:
            A new IntakeDocument aggregate root instance.
        Assumptions:
            Target tenant is verified active.
        Edge Cases:
            Domain events include tenant identifiers to scope downstream workers.
        """
        doc = cls(id, tenant_id, source, metadata, storage_path, IntakeStatus.INGESTED)
        doc.add_domain_event(
            DocumentIngestedEvent(
                aggregate_id=doc.id,
                tenant_id=tenant_id,
                filename=metadata.filename,
                source=source.value,
                storage_path=storage_path,
                hash_sha256=metadata.hash_sha256
            )
        )
        return doc

    def fail(self, reason: str) -> None:
        """
        Marks the intake document session as failed and publishes the error event.

        Purpose:
            Indicate ingestion failure.
        Business Reasoning:
            Maintains historical trace logs of failures for clinical auditing.
        Inputs:
            reason (str): Error reason.
        Outputs:
            None.
        Assumptions:
            None.
        Edge Cases:
            Saves audit messages detailing the failure vector.
        """
        self.status = IntakeStatus.FAILED
        self.add_domain_event(
            DocumentIntakeFailedEvent(
                aggregate_id=self.id,
                tenant_id=self.tenant_id,
                filename=self.metadata.filename,
                reason=reason
            )
        )
