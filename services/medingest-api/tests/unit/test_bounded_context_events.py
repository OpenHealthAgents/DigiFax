"""
test_bounded_context_events.py
Unit tests verifying tenant awareness across all bounded contexts' domain events.
"""

from src.domain.ocr.events import OcrCompletedEvent
from src.domain.extraction.events import ExtractionCompletedEvent
from src.domain.terminology.events import TerminologyMappedEvent
from src.domain.fhir.events import FhirResourceGeneratedEvent
from src.domain.validation.events import ValidationCompletedEvent


def test_bounded_contexts_events_are_tenant_aware() -> None:
    # 1. OCR Event
    ocr_event = OcrCompletedEvent(
        aggregate_id="doc-123",
        tenant_id="tenant-123",
        engine_name="GoogleDocumentAI",
        execution_time_seconds=1.45
    )
    assert ocr_event.aggregate_id == "doc-123"
    assert ocr_event.tenant_id == "tenant-123"
    assert ocr_event.engine_name == "GoogleDocumentAI"

    # 2. Extraction Event
    ext_event = ExtractionCompletedEvent(
        aggregate_id="doc-123",
        tenant_id="tenant-123",
        extractor_engine="Gemini-2.0"
    )
    assert ext_event.aggregate_id == "doc-123"
    assert ext_event.tenant_id == "tenant-123"

    # 3. Terminology Event
    term_event = TerminologyMappedEvent(
        aggregate_id="doc-123",
        tenant_id="tenant-123",
        system_mapped="LOINC"
    )
    assert term_event.aggregate_id == "doc-123"
    assert term_event.tenant_id == "tenant-123"

    # 4. FHIR Event
    fhir_event = FhirResourceGeneratedEvent(
        aggregate_id="doc-123",
        tenant_id="tenant-123",
        resource_type="DiagnosticReport"
    )
    assert fhir_event.aggregate_id == "doc-123"
    assert fhir_event.tenant_id == "tenant-123"

    # 5. Validation Event
    val_event = ValidationCompletedEvent(
        aggregate_id="doc-123",
        tenant_id="tenant-123",
        is_valid=True,
        error_count=0
    )
    assert val_event.aggregate_id == "doc-123"
    assert val_event.tenant_id == "tenant-123"
    assert val_event.is_valid is True
