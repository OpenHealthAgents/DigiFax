import time
from unittest.mock import MagicMock

from src.application.services.search_orchestrator import SearchOrchestrator
from src.application.services.validation_engine import ValidationEngine
from src.domain.extraction.schemas import (
    ExtractedField,
    PatientDemographics,
    StructuredClinicalReport,
)
from src.domain.ocr.value_objects import BoundingBox, OcrPage, OcrResult, OcrWord
from src.domain.search.models import SearchResult
from src.domain.validation.rules import ValidationContext


def test_rules_engine_performance_throughput() -> None:
    engine = ValidationEngine()

    bbox = BoundingBox(0, 0, 1, 1)
    word = OcrWord("Glucose", bbox, 0.95)
    page = OcrPage(1, [word], "Glucose report", [], {})
    ocr_res = OcrResult("doc-01", [page], "tesseract", 0.5)

    field_name = ExtractedField(value="Elizabeth Blackwell", evidence="Elizabeth", confidence=0.88)
    demographics = PatientDemographics(name=field_name, dob=None, gender=None, mrn=None)
    field_type = ExtractedField(value="Lab Report", evidence="report", confidence=0.95)
    extracted_rep = StructuredClinicalReport(patient=demographics, observations=[], document_type=field_type)

    ctx = ValidationContext(
        ocr_result=ocr_res,
        extracted_report=extracted_rep,
        fhir_bundle={"resourceType": "Bundle", "entry": []}
    )

    # Run 100 iterations to measure validation throughput
    start_time = time.perf_counter()
    for _ in range(100):
        _ = engine.validate(ctx)
    duration = time.perf_counter() - start_time

    avg_latency_ms = (duration / 100.0) * 1000.0
    print(f"Validation Engine average latency: {avg_latency_ms:.4f} ms")

    # Assert validation is highly performant (e.g. under 10ms per document validation)
    assert avg_latency_ms < 10.0


def test_rrf_rank_fusion_latency() -> None:
    # Setup mock services for SearchOrchestrator
    mock_search = MagicMock()
    mock_search.keyword_search.return_value = [
        SearchResult(document_id=f"doc-{i}", score=10.0 - i, highlights={}, metadata={})
        for i in range(10)
    ]
    mock_search.vector_search.return_value = [
        SearchResult(document_id=f"doc-{i}", score=1.0 - (i * 0.1), highlights={}, metadata={})
        for i in range(5, 15)
    ]
    mock_generator = MagicMock()
    mock_generator.generate_embedding.return_value = [0.1] * 1536

    orchestrator = SearchOrchestrator(mock_search, mock_generator)

    # Run 50 iterations to measure RRF scoring performance
    start_time = time.perf_counter()
    for _ in range(50):
        _ = orchestrator.hybrid_search("Glucose report query", limit=10)
    duration = time.perf_counter() - start_time

    avg_latency_ms = (duration / 50.0) * 1000.0
    print(f"RRF Hybrid Search average latency: {avg_latency_ms:.4f} ms")

    # Assert ranking fusion runs under 15ms
    assert avg_latency_ms < 15.0
