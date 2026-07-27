"""
intake_controller.py
FastAPI REST API controller handling multi-tenant manual faxes and document uploads.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Header

from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.application.use_cases.intake.handlers import IngestDocumentUseCase
from src.domain.common.exceptions import DomainException
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.persistence.in_memory_intake_repository import (
    InMemoryIntakeDocumentRepository,
)
from src.infrastructure.persistence.in_memory_tenant_repository import (
    InMemoryTenantRepository,
)
from src.infrastructure.storage.in_memory_storage import InMemoryStorage

router = APIRouter(prefix="/api/intake", tags=["Intake"])

# Singletons representing in-memory storage/database contexts
_repo = InMemoryIntakeDocumentRepository()
_tenant_repo = InMemoryTenantRepository()
_storage = InMemoryStorage()
_event_bus = InMemoryEventBus()


def get_ingest_use_case() -> IngestDocumentUseCase:
    """
    Dependency injection lookup mapping repositories to use case handlers.

    Purpose:
        Build IngestDocumentUseCase instances with injected port adapters.
    Business Reasoning:
        Dependency inversion decouples domain use cases from infrastructure choices.
    Inputs:
        None.
    Outputs:
        IngestDocumentUseCase: Hydrated instance.
    Assumptions:
        Singletons are initialized.
    Edge Cases:
        None.
    """
    return IngestDocumentUseCase(
        repository=_repo,
        tenant_repository=_tenant_repo,
        storage=_storage,
        event_bus=_event_bus
    )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="Document file binary payload"),
    source: str = Form("API_UPLOAD", description="Upload source channel"),
    x_tenant_id: str = Header(..., description="Unique UUID identifying the clinical tenant"),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Ingests manual user document uploads, verifying tenant active state.

    Purpose:
        Authenticate tenant header and ingest document.
    Business Reasoning:
        Guarantees that uploads are logically isolated by tenant boundaries.
    Inputs:
        file (UploadFile): Inbound binary payload.
        source (str): Source type.
        x_tenant_id (str): Tenant header.
        use_case (IngestDocumentUseCase): Injected handler.
    Outputs:
        dict: Ingestion status and generated document_id.
    Assumptions:
        Tenant ID header is supplied.
    Edge Cases:
        Returns 400 Bad Request on DomainExceptions (Suspended or Missing tenants).
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            tenant_id=x_tenant_id,
            filename=file.filename or "document.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source=source
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})


@router.post("/fax")
async def upload_fax(
    file: UploadFile = File(..., description="Fax image or TIFF payload"),
    x_tenant_id: str = Header(..., description="Unique UUID identifying the clinical tenant"),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Simulates telephony FoIP webhook ingestion mapping source to FAX_UPLOAD.

    Purpose:
        Ingest incoming telephony faxes.
    Business Reasoning:
        Isolates incoming faxes under the receiving medical facility's tenant ID.
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            tenant_id=x_tenant_id,
            filename=file.filename or "fax.tiff",
            content_type=file.content_type or "image/tiff",
            file_bytes=content,
            source="FAX_UPLOAD"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})


@router.post("/email")
async def ingest_email(
    file: UploadFile = File(..., description="Email attachment payload"),
    x_tenant_id: str = Header(..., description="Unique UUID identifying the clinical tenant"),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Simulates email parser worker webhooks mapping source to EMAIL_ATTACHMENT.

    Purpose:
        Ingest clinical attachments from email.
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            tenant_id=x_tenant_id,
            filename=file.filename or "attachment.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source="EMAIL_ATTACHMENT"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})
