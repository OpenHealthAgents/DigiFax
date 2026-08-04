"""
intake_controller.py
FastAPI REST API controller handling multi-tenant manual faxes and document uploads with permissions.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.application.common.tenant_context import TenantContext
from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.application.use_cases.intake.handlers import IngestDocumentUseCase
from src.domain.common.exceptions import DomainException
from src.infrastructure.controllers.api_guard import require_permissions
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
    """
    return IngestDocumentUseCase(
        repository=_repo,
        tenant_repository=_tenant_repo,
        storage=_storage,
        event_bus=_event_bus
    )


@router.post(
    "/upload",
    summary="Ingest manual document upload",
    description="Validates tenant authorization and uploads PDFs/documents scoped by TenantContext.",
    responses={
        200: {
            "description": "Document uploaded successfully",
            "content": {
                "application/json": {
                    "example": {"status": "success", "document_id": "doc-uuid-123"}
                }
            }
        },
        400: {
            "description": "Invalid format or tenant validation errors",
            "content": {
                "application/json": {
                    "example": {"detail": {"message": "Tenant not found: tenant-missing", "code": "TENANT_NOT_FOUND"}}
                }
            }
        },
        403: {
            "description": "Forbidden: Insufficient role permissions or missing feature flags",
            "content": {
                "application/json": {
                    "example": {"detail": {"message": "Forbidden: Insufficient permissions", "code": "FORBIDDEN_PERMISSIONS"}}
                }
            }
        }
    }
)
async def upload_document(
    file: UploadFile = File(..., description="Document file binary payload"),
    source: str = Form("API_UPLOAD", description="Upload source channel"),
    context: TenantContext = Depends(require_permissions("document:write")),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Ingests manual user document uploads, verifying tenant active state.

    Workflow breakdown:
      - Validates permissions: 'Depends(require_permissions("document:write"))' ensures user has write authorization.
      - Resolves Dependencies: Injecting IngestDocumentUseCase dynamically via FastAPI's Depend mechanism.
      - Reads request files: Reads uploaded document file binary content.
      - Executes command: Compiles parameters into IngestDocumentCommand DTO and runs the ingestion use case pipeline.
      - Maps Exceptions: Catches DomainException and translates it to HTTP 400 Bad Request error detail.
    """
    try:
        # Step A: Read incoming request file stream bytes
        content = await file.read()
        
        # Step B: Instantiate command transfer object encapsulating tenant scope and file metadata
        command = IngestDocumentCommand(
            context=context,
            filename=file.filename or "document.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source=source
        )
        
        # Step C: Dispatch command to application core service layer
        doc_id = use_case.execute(command)
        
        # Return transactional success outcome
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        # Translate internal domain exception codes cleanly to JSON API spec responses
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})


@router.post(
    "/fax",
    summary="Ingest telephony FoIP fax",
    description="Webhook endpoint mapping incoming faxes to FAX_UPLOAD.",
    responses={
        200: {"description": "Fax document registered successfully"},
        403: {"description": "Forbidden: Insufficient permissions"}
    }
)
async def upload_fax(
    file: UploadFile = File(..., description="Fax image or TIFF payload"),
    context: TenantContext = Depends(require_permissions("document:write")),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Simulates telephony FoIP webhook ingestion mapping source to FAX_UPLOAD.
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            context=context,
            filename=file.filename or "fax.tiff",
            content_type=file.content_type or "image/tiff",
            file_bytes=content,
            source="FAX_UPLOAD"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})


@router.post(
    "/email",
    summary="Ingest email parser attachment",
    description="Webhook endpoint mapping attachments to EMAIL_ATTACHMENT.",
    responses={
        200: {"description": "Email attachment registered successfully"},
        403: {"description": "Forbidden: Insufficient permissions"}
    }
)
async def ingest_email(
    file: UploadFile = File(..., description="Email attachment payload"),
    context: TenantContext = Depends(require_permissions("document:write")),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Simulates email parser worker webhooks mapping source to EMAIL_ATTACHMENT.
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            context=context,
            filename=file.filename or "attachment.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source="EMAIL_ATTACHMENT"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})


@router.post(
    "/scan",
    summary="Ingest scanned document",
    description="Webhook or scanner integration endpoint mapping files to SCAN_UPLOAD.",
    responses={
        200: {"description": "Scanned document registered successfully"},
        403: {"description": "Forbidden: Insufficient permissions"}
    }
)
async def upload_scan(
    file: UploadFile = File(..., description="Scanned document file payload"),
    context: TenantContext = Depends(require_permissions("document:write")),
    use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
) -> dict[str, str]:
    """
    Simulates scanned file upload from an office scanner/MFD mapping source to SCAN_UPLOAD.
    """
    try:
        content = await file.read()
        command = IngestDocumentCommand(
            context=context,
            filename=file.filename or "scan.pdf",
            content_type=file.content_type or "application/pdf",
            file_bytes=content,
            source="SCAN_UPLOAD"
        )
        doc_id = use_case.execute(command)
        return {"status": "success", "document_id": doc_id}
    except DomainException as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "code": e.code})

