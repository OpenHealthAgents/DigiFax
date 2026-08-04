"""
handlers.py
Handler orchestrating the Intake Document Use Case.

Sequence Diagram:

    [Client] ---> [FastAPI Controller] ---> [IngestDocumentUseCase.execute]
                                                       |
                                         [TenantRepository.get_by_id]
                                                       | (Check Status)
                                        [DocumentStorage.save(partitioned)]
                                                       |
                                        [IntakeDocument.create_ingested]
                                                       |
                                         [IntakeRepository.save]
                                                       |
                                           [EventBus.publish]
"""

import hashlib

from src.application.ports.idocument_storage import IDocumentStorage
from src.application.ports.iintake_document_repository import IIntakeDocumentRepository
from src.application.ports.itenant_repository import ITenantRepository
from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.domain.common.event_bus import IEventBus
from src.domain.common.exceptions import DomainException
from src.domain.common.uuid import UniqueId
from src.domain.intake.entities import IntakeDocument
from src.domain.intake.value_objects import FileMetadata, IntakeSource


class IngestDocumentUseCase:
    """
    Orchestrates document ingestion, metadata calculation, and persistence scoped by TenantContext.

    Purpose:
        Verify tenant status, store raw binaries physically isolated, and register Intake aggregates.
    Business Reasoning:
        Verifying tenant active status prevents unsanctioned system resource consumption.
        Partitioning storage layout guarantees physical/logical segregation.
    """

    def __init__(
        self,
        repository: IIntakeDocumentRepository,
        tenant_repository: ITenantRepository,
        storage: IDocumentStorage,
        event_bus: IEventBus
    ):
        """
        Constructor injects required ports.
        """
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.storage = storage
        self.event_bus = event_bus

    def execute(self, command: IngestDocumentCommand) -> str:
        """
        Processes document ingestion, validates tenant active checks, and saves the payload.

        Purpose:
            Verify, partition, and save files.
        Business Reasoning:
            Ensures that only authorized accounts inject faxes into system pipelines.
        Inputs:
            command (IngestDocumentCommand): Contains file bytes, type, source, and TenantContext.
        Outputs:
            str: Generated unique document ID.
        Assumptions:
            Storage adapter is accessible.
        Edge Cases:
            - Tenant ID does not exist: throws DomainException (TENANT_NOT_FOUND).
            - Tenant account is suspended: throws DomainException (TENANT_SUSPENDED).
            - Invalid upload source string: throws DomainException (INVALID_INTAKE_SOURCE).
        """
        tenant_id = command.context.tenant_id

        # Validate tenant status
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise DomainException(
                message=f"Tenant not found: {tenant_id}",
                code="TENANT_NOT_FOUND"
            )

        if not tenant.is_active():
            raise DomainException(
                message=f"Tenant account is suspended: {tenant_id}",
                code="TENANT_SUSPENDED"
            )

        # Validate intake source
        try:
            source = IntakeSource(command.source)
        except ValueError as e:
            raise DomainException(
                message=f"Invalid intake source: {command.source}. Allowed sources are FAX_UPLOAD, EMAIL_ATTACHMENT, API_UPLOAD, SCAN_UPLOAD.",
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

        # Save raw file bytes to storage partitioned by tenant ID
        storage_path = f"raw/{tenant.id}/{document_id}.{metadata.extension}"
        resolved_path = self.storage.save(
            filepath=storage_path,
            data=command.file_bytes,
            tenant_id=tenant.id
        )

        # Create aggregate and publish event
        doc = IntakeDocument.create_ingested(
            id=document_id,
            tenant_id=tenant.id,
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
