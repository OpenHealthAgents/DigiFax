import enum

from src.domain.common.entity import AggregateRoot
from src.domain.intake.events import DocumentIngestedEvent, DocumentIntakeFailedEvent
from src.domain.intake.value_objects import FileMetadata, IntakeSource


class IntakeStatus(enum.StrEnum):
    INGESTED = "INGESTED"
    FAILED = "FAILED"


class IntakeDocument(AggregateRoot):
    """Aggregate Root representing an incoming clinical document ingestion session."""

    def __init__(
        self,
        id: str,
        source: IntakeSource,
        metadata: FileMetadata,
        storage_path: str,
        status: IntakeStatus = IntakeStatus.INGESTED
    ):
        super().__init__(id)
        self.source = source
        self.metadata = metadata
        self.storage_path = storage_path
        self.status = status

    @classmethod
    def create_ingested(
        cls,
        id: str,
        source: IntakeSource,
        metadata: FileMetadata,
        storage_path: str
    ) -> 'IntakeDocument':
        """Creates a successfully ingested document and publishes the event."""
        doc = cls(id, source, metadata, storage_path, IntakeStatus.INGESTED)
        doc.add_domain_event(
            DocumentIngestedEvent(
                aggregate_id=doc.id,
                filename=metadata.filename,
                source=source.value,
                storage_path=storage_path,
                hash_sha256=metadata.hash_sha256
            )
        )
        return doc

    def fail(self, reason: str) -> None:
        """Marks the intake document session as failed and publishes the error event."""
        self.status = IntakeStatus.FAILED
        self.add_domain_event(
            DocumentIntakeFailedEvent(
                aggregate_id=self.id,
                filename=self.metadata.filename,
                reason=reason
            )
        )
