"""
test_intake.py
Unit tests verifying multi-tenant document ingestion pipelines, use cases, and route filters.
"""

import pytest
from fastapi.testclient import TestClient

from src.application.common.tenant_context import TenantContext
from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.application.use_cases.intake.handlers import IngestDocumentUseCase
from src.domain.common.exceptions import DomainException
from src.domain.intake.entities import IntakeStatus
from src.domain.intake.events import DocumentIngestedEvent
from src.domain.intake.value_objects import FileMetadata, IntakeSource
from src.domain.organizations.entities import Tenant, TenantStatus
from src.domain.organizations.value_objects import TenantConfiguration
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.persistence.in_memory_intake_repository import (
    InMemoryIntakeDocumentRepository,
)
from src.infrastructure.persistence.in_memory_tenant_repository import (
    InMemoryTenantRepository,
)
from src.infrastructure.storage.in_memory_storage import InMemoryStorage
from src.main import app

client = TestClient(app)


# --- 1. Domain FileMetadata Value Object Tests ---

def test_file_metadata_validation_success() -> None:
    # Valid PDF
    meta = FileMetadata("report.pdf", "application/pdf", 1024, "mock_sha")
    assert meta.filename == "report.pdf"
    assert meta.content_type == "application/pdf"
    assert meta.extension == "pdf"


def test_file_metadata_validation_invalid_extension() -> None:
    with pytest.raises(DomainException) as exc_info:
        FileMetadata("script.py", "text/plain", 123, "mock_sha")
    assert exc_info.value.code == "UNSUPPORTED_FILE_TYPE"


# --- 2. IngestDocumentUseCase Multi-Tenant Tests ---

def test_ingest_use_case_success() -> None:
    repo = InMemoryIntakeDocumentRepository()
    tenant_repo = InMemoryTenantRepository()
    storage = InMemoryStorage()
    event_bus = InMemoryEventBus()
    use_case = IngestDocumentUseCase(repo, tenant_repo, storage, event_bus)

    # Ingest document under active tenant-123 context
    context = TenantContext(tenant_id="tenant-123")
    command = IngestDocumentCommand(
        context=context,
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=b"mock pdf content",
        source="FAX_UPLOAD"
    )

    doc_id = use_case.execute(command)

    # Enforce database partitioning - get_by_id returns document if tenant match
    saved_doc = repo.get_by_id(doc_id, "tenant-123")
    assert saved_doc is not None
    assert saved_doc.id == doc_id
    assert saved_doc.tenant_id == "tenant-123"

    # Enforce database partitioning - get_by_id returns None on cross-tenant query
    cross_tenant_doc = repo.get_by_id(doc_id, "tenant-456")
    assert cross_tenant_doc is None

    # Verify isolated physical path S3 storage save
    expected_path = f"raw/tenant-123/{doc_id}.pdf"
    assert storage.get(expected_path) == b"mock pdf content"


def test_ingest_use_case_tenant_not_found() -> None:
    repo = InMemoryIntakeDocumentRepository()
    tenant_repo = InMemoryTenantRepository()
    storage = InMemoryStorage()
    event_bus = InMemoryEventBus()
    use_case = IngestDocumentUseCase(repo, tenant_repo, storage, event_bus)

    # Command with invalid tenant context
    context = TenantContext(tenant_id="tenant-missing")
    command = IngestDocumentCommand(
        context=context,
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=b"pdf",
        source="FAX_UPLOAD"
    )

    with pytest.raises(DomainException) as exc_info:
        use_case.execute(command)
    assert exc_info.value.code == "TENANT_NOT_FOUND"


def test_ingest_use_case_tenant_suspended() -> None:
    repo = InMemoryIntakeDocumentRepository()
    tenant_repo = InMemoryTenantRepository()
    storage = InMemoryStorage()
    event_bus = InMemoryEventBus()
    use_case = IngestDocumentUseCase(repo, tenant_repo, storage, event_bus)

    # Command with suspended tenant context
    context = TenantContext(tenant_id="tenant-suspended")
    command = IngestDocumentCommand(
        context=context,
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=b"pdf",
        source="FAX_UPLOAD"
    )

    with pytest.raises(DomainException) as exc_info:
        use_case.execute(command)
    assert exc_info.value.code == "TENANT_SUSPENDED"


# --- 3. FastAPI HTTP Inbound Adapter Controller Tests ---

def test_api_upload_endpoint_success() -> None:
    response = client.post(
        "/api/intake/upload",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")},
        data={"source": "API_UPLOAD"},
        headers={"X-Tenant-ID": "tenant-123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "document_id" in json_data


def test_api_upload_endpoint_missing_tenant_header() -> None:
    response = client.post(
        "/api/intake/upload",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")},
        data={"source": "API_UPLOAD"}
    )
    # FastAPI returns 400 Bad Request now on our custom context resolver
    assert response.status_code == 400


def test_api_upload_endpoint_suspended_tenant() -> None:
    response = client.post(
        "/api/intake/upload",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")},
        data={"source": "API_UPLOAD"},
        headers={"X-Tenant-ID": "tenant-suspended"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TENANT_SUSPENDED"


def test_api_fax_endpoint_success() -> None:
    response = client.post(
        "/api/intake/fax",
        files={"file": ("fax.tiff", b"tiff content", "image/tiff")},
        headers={"X-Tenant-ID": "tenant-123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"


def test_api_email_endpoint_success() -> None:
    response = client.post(
        "/api/intake/email",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")},
        headers={"X-Tenant-ID": "tenant-123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
