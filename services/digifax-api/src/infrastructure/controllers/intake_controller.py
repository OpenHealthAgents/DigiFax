from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.application.use_cases.intake.handlers import IngestDocumentUseCase
from src.domain.common.exceptions import DomainException
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.persistence.in_memory_intake_repository import (
    InMemoryIntakeDocumentRepository,
)
from src.infrastructure.storage.in_memory_storage import InMemoryStorage

router = APIRouter(prefix="/api/intake", tags=["Intake"])

# Singletons representing in-memory storage/database contexts
_repo = InMemoryIntakeDocumentRepository()
_storage = InMemoryStorage()
_event_bus = InMemoryEventBus()

def get_ingest_use_case() -> IngestDocumentUseCase:
    return IngestDocumentUseCase(repository=_repo, storage=_storage, event_bus=_event_bus)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    source: str = Form("API_UPLOAD"),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """Ingests manual user document uploads."""
    try:
        content = await file.read()
        command = IngestDocumentCommand(
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
    file: UploadFile = File(...),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """Simulates telephony FoIP webhook ingestion mapping source to FAX_UPLOAD."""
    try:
        content = await file.read()
        command = IngestDocumentCommand(
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
    file: UploadFile = File(...),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """Simulates email parser worker webhooks mapping source to EMAIL_ATTACHMENT."""
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            filename=file.filename or "attachment.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source="EMAIL_ATTACHMENT"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})
