import hashlib

from src.application.ports.idocument_storage import IDocumentStorage
from src.application.ports.iintake_document_repository import IIntakeDocumentRepository
from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.domain.common.event_bus import IEventBus
from src.domain.common.exceptions import DomainException
from src.domain.common.uuid import UniqueId
from src.domain.intake.entities import IntakeDocument
from src.domain.intake.value_objects import FileMetadata, IntakeSource


class IngestDocumentUseCase:
    """Orchestrates document ingestion, metadata calculation, and persistence."""

    def __init__(
        self,
        repository: IIntakeDocumentRepository,
        storage: IDocumentStorage,
        event_bus: IEventBus
    ):
        self.repository = repository
        self.storage = storage
        self.event_bus = event_bus

    def execute(self, command: IngestDocumentCommand) -> str:
        """Processes document ingestion.

        Returns:
            The generated unique document ID.
        """
        # Validate intake source
        try:
            source = IntakeSource(command.source)
        except ValueError as e:
            raise DomainException(
                message=f"Invalid intake source: {command.source}. Allowed sources are FAX_UPLOAD, EMAIL_ATTACHMENT, API_UPLOAD.",
                code="INVALID_INTAKE_SOURCE"
            ) from e

        # Calculate file size and sha-256 hash
        size_bytes = len(command.file_bytes)
        hash_sha256 = hashlib.sha256(command.file_bytes).hexdigest()

        # Validate file type / metadata
        metadata = FileMetadata(
            filename=command.filename,
            content_type=command.content_type,
            size_bytes=size_bytes,
            hash_sha256=hash_sha256
        )

        document_id = UniqueId.generate()

        # Save raw file bytes to storage
        storage_path = f"raw/{document_id}.{metadata.extension}"
        resolved_path = self.storage.save(storage_path, command.file_bytes)

        # Create aggregate and publish event
        doc = IntakeDocument.create_ingested(
            id=document_id,
            source=source,
            metadata=metadata,
            storage_path=resolved_path
        )

        # Save to database
        self.repository.save(doc)

        # Dispatch domain events
        for event in doc.domain_events:
            self.event_bus.publish(event)
        doc.clear_domain_events()

        return document_id
