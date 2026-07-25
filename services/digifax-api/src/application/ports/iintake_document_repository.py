import abc

from src.domain.intake.entities import IntakeDocument


class IIntakeDocumentRepository(abc.ABC):
    """Outbound port interface for persisting Ingested Document Aggregate state."""

    @abc.abstractmethod
    def save(self, document: IntakeDocument) -> None:
        """Saves or updates the IntakeDocument aggregate in the persistent database."""
        pass

    @abc.abstractmethod
    def get_by_id(self, id: str) -> IntakeDocument | None:
        """Retrieves an IntakeDocument aggregate by its unique identifier."""
        pass
