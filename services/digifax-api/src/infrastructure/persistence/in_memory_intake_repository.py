"""
in_memory_intake_repository.py
In-memory partition repository verifying tenant scopes.
"""

import threading

from src.application.ports.iintake_document_repository import IIntakeDocumentRepository
from src.domain.intake.entities import IntakeDocument


class InMemoryIntakeDocumentRepository(IIntakeDocumentRepository):
    """
    Thread-safe, in-memory implementation of IIntakeDocumentRepository.

    Purpose:
        Store document ingestion session aggregates partitioned logically.
    Business Reasoning:
        Enforces tenant query isolations to block cross-subscriber leaks in sandboxes.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._documents: dict[str, IntakeDocument] = {}

    def save(self, document: IntakeDocument) -> None:
        """
        Saves or updates the IntakeDocument.

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
            Uses thread-safe locking to prevent write collisions.
        """
        with self._lock:
            self._documents[document.id] = document

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
        with self._lock:
            doc = self._documents.get(id)
            if doc and doc.tenant_id == tenant_id:
                return doc
            return None
