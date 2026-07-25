
from src.application.ports.iintake_document_repository import IIntakeDocumentRepository
from src.domain.intake.entities import IntakeDocument


class InMemoryIntakeDocumentRepository(IIntakeDocumentRepository):
    """Thread-safe, in-memory implementation of IIntakeDocumentRepository for testing."""

    def __init__(self) -> None:
        self._documents: dict[str, IntakeDocument] = {}

    def save(self, document: IntakeDocument) -> None:
        self._documents[document.id] = document

    def get_by_id(self, id: str) -> IntakeDocument | None:
        return self._documents.get(id)
