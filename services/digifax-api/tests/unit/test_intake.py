import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.intake.commands import IngestDocumentCommand
from src.application.use_cases.intake.handlers import IngestDocumentUseCase
from src.domain.common.exceptions import DomainException
from src.domain.intake.entities import IntakeStatus
from src.domain.intake.events import DocumentIngestedEvent
from src.domain.intake.value_objects import FileMetadata, IntakeSource
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.persistence.in_memory_intake_repository import (
    InMemoryIntakeDocumentRepository,
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

    # Valid TIFF
    meta = FileMetadata("fax.tiff", "image/tiff", 2048, "mock_sha")
    assert meta.extension == "tiff"

    # Valid PNG
    meta = FileMetadata("image.png", "image/png", 512, "mock_sha")
    assert meta.extension == "png"

    # Valid JPEG (maps image/jpg to image/jpeg)
    meta = FileMetadata("scan.jpg", "image/jpg", 4096, "mock_sha")
    assert meta.extension == "jpg"
    assert meta.content_type == "image/jpeg"


def test_file_metadata_validation_invalid_extension() -> None:
    with pytest.raises(DomainException) as exc_info:
        FileMetadata("script.py", "text/plain", 123, "mock_sha")
    assert exc_info.value.code == "UNSUPPORTED_FILE_TYPE"


def test_file_metadata_validation_invalid_mime_type() -> None:
    with pytest.raises(DomainException) as exc_info:
        FileMetadata("report.pdf", "text/plain", 123, "mock_sha")
    assert exc_info.value.code == "UNSUPPORTED_MIME_TYPE"


def test_file_metadata_validation_invalid_file_size() -> None:
    with pytest.raises(DomainException) as exc_info:
        FileMetadata("report.pdf", "application/pdf", 0, "mock_sha")
    assert exc_info.value.code == "INVALID_FILE_SIZE"


def test_file_metadata_validation_missing_extension() -> None:
    with pytest.raises(DomainException) as exc_info:
        FileMetadata("report", "application/pdf", 100, "mock_sha")
    assert exc_info.value.code == "MISSING_FILE_EXTENSION"


# --- 2. IngestDocumentUseCase Tests ---

def test_ingest_use_case_success() -> None:
    repo = InMemoryIntakeDocumentRepository()
    storage = InMemoryStorage()
    event_bus = InMemoryEventBus()
    use_case = IngestDocumentUseCase(repo, storage, event_bus)

    file_bytes = b"mock pdf content"
    command = IngestDocumentCommand(
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=file_bytes,
        source="FAX_UPLOAD"
    )

    doc_id = use_case.execute(command)

    # Check database persistence
    saved_doc = repo.get_by_id(doc_id)
    assert saved_doc is not None
    assert saved_doc.id == doc_id
    assert saved_doc.status == IntakeStatus.INGESTED
    assert saved_doc.source == IntakeSource.FAX_UPLOAD
    assert saved_doc.metadata.filename == "report.pdf"

    # Check S3 storage save
    expected_path = f"raw/{doc_id}.pdf"
    assert storage.get(expected_path) == file_bytes

    # Check domain event publishing
    assert len(event_bus.published_events) == 1
    event = event_bus.published_events[0]
    assert isinstance(event, DocumentIngestedEvent)
    assert event.aggregate_id == doc_id
    assert event.filename == "report.pdf"
    assert event.source == "FAX_UPLOAD"
    assert event.storage_path == expected_path


def test_ingest_use_case_invalid_source() -> None:
    repo = InMemoryIntakeDocumentRepository()
    storage = InMemoryStorage()
    event_bus = InMemoryEventBus()
    use_case = IngestDocumentUseCase(repo, storage, event_bus)

    command = IngestDocumentCommand(
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=b"bytes",
        source="INVALID_SOURCE"
    )

    with pytest.raises(DomainException) as exc_info:
        use_case.execute(command)
    assert exc_info.value.code == "INVALID_INTAKE_SOURCE"


# --- 3. FastAPI HTTP Inbound Adapter Controller Tests ---

def test_api_upload_endpoint_success() -> None:
    response = client.post(
        "/api/intake/upload",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")},
        data={"source": "API_UPLOAD"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "document_id" in json_data


def test_api_upload_endpoint_validation_error() -> None:
    response = client.post(
        "/api/intake/upload",
        files={"file": ("script.py", b"python code", "text/plain")},
        data={"source": "API_UPLOAD"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_api_fax_endpoint_success() -> None:
    response = client.post(
        "/api/intake/fax",
        files={"file": ("fax.tiff", b"tiff content", "image/tiff")}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "document_id" in json_data


def test_api_email_endpoint_success() -> None:
    response = client.post(
        "/api/intake/email",
        files={"file": ("report.pdf", b"pdf content", "application/pdf")}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "document_id" in json_data
