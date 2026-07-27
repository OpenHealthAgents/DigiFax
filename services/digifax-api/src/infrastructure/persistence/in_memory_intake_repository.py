"""
in_memory_intake_repository.py
In-memory partition repository verifying tenant scopes and implementing BaseInMemoryRepository features.
"""

from src.application.ports.iintake_document_repository import IIntakeDocumentRepository
from src.domain.intake.entities import IntakeDocument, IntakeStatus
from src.domain.intake.value_objects import FileMetadata, IntakeSource
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryIntakeDocumentRepository(BaseInMemoryRepository, IIntakeDocumentRepository):
    """
    In-memory implementation of IIntakeDocumentRepository with multi-tenancy and OCC.

    Purpose:
        Store document ingestion session aggregates partitioned logically.
    Business Reasoning:
        Enforces tenant query isolations to block cross-subscriber leaks.
    """

    def __init__(self) -> None:
        super().__init__()

    def save(self, document: IntakeDocument) -> None:
        """
        Saves or updates the IntakeDocument aggregate.

        Purpose:
            Persist aggregates.
        Business Reasoning:
            Clinical indexes must register in secure stores.
        Inputs:
            document (IntakeDocument): Agg root.
        Outputs:
            None.
        Assumptions:
            Target dictionary is writeable.
        Edge Cases:
            Optimistic concurrency verification.
        """
        record_data = {
            "id": document.id,
            "tenant_id": document.tenant_id,
            "source": document.source.value,
            "filename": document.metadata.filename,
            "content_type": document.metadata.content_type,
            "size_bytes": document.metadata.size_bytes,
            "hash_sha256": document.metadata.hash_sha256,
            "storage_path": document.storage_path,
            "status": document.status.value,
            "version": getattr(document, "version", 1)
        }

        # Call base save executing OCC check and auditing
        self._save_record(document.id, record_data)
        
        # Sync version back to domain aggregate
        saved_record = self._records[document.id]
        document.version = saved_record["version"]

    def get_by_id(self, id: str, tenant_id: str) -> IntakeDocument | None:
        """
        Retrieves a document matching both ID and tenant ID.

        Purpose:
            Query document metadata.
        Business Reasoning:
            Verifies requesting scope before return.
        Inputs:
            id (str): Document UUID.
            tenant_id (str): Requesting tenant ID.
        Outputs:
            IntakeDocument | None: Matched aggregate, or None if missing or unauthorized.
        Assumptions:
            None.
        Edge Cases:
            If document exists but belongs to a different tenant, returns None.
        """
        record = self._get_record_by_id(id, tenant_id)
        if not record:
            return None

        # Reconstruct domain aggregate
        metadata = FileMetadata(
            filename=record["filename"],
            content_type=record["content_type"],
            size_bytes=record["size_bytes"],
            hash_sha256=record["hash_sha256"]
        )
        doc = IntakeDocument(
            id=record["id"],
            tenant_id=record["tenant_id"],
            source=IntakeSource(record["source"]),
            metadata=metadata,
            storage_path=record["storage_path"],
            status=IntakeStatus(record["status"])
        )
        # Hydrate dynamic properties
        doc.version = record["version"]
        return doc

    def list_documents(
        self,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[IntakeDocument], int]:
        """
        Retrieves a paginated list of active documents for a tenant.

        Purpose:
            Paginate faxes listings.
        """
        records, total_count = self._list_records(tenant_id, limit=limit, offset=offset)
        docs = []
        for record in records:
            metadata = FileMetadata(
                filename=record["filename"],
                content_type=record["content_type"],
                size_bytes=record["size_bytes"],
                hash_sha256=record["hash_sha256"]
            )
            doc = IntakeDocument(
                id=record["id"],
                tenant_id=record["tenant_id"],
                source=IntakeSource(record["source"]),
                metadata=metadata,
                storage_path=record["storage_path"],
                status=IntakeStatus(record["status"])
            )
            doc.version = record["version"]
            docs.append(doc)

        return docs, total_count
