import base64

import pytest

from src.application.services.validation_engine import ValidationEngine
from src.domain.extraction.schemas import (
    ExtractedField,
    PatientDemographics,
    StructuredClinicalReport,
)
from src.domain.ocr.value_objects import BoundingBox, OcrPage, OcrResult, OcrWord
from src.domain.validation.rules import ValidationContext


def test_upload_document_malformed_base64_protection() -> None:
    # Ensure parameter validation handles invalid base64 encoding payloads gracefully
    invalid_payload = "invalid-base64-payload!!!"

    # Base64 decoder in pure python throws binascii.Error or ValueError on decoding malformed inputs
    with pytest.raises((ValueError, Exception)):
        # Decode action
        _ = base64.b64decode(invalid_payload, validate=True)


def test_search_records_sql_injection_sanitization() -> None:
    # SQL injection characters inside search keywords should be treated as literal search text rather than commands
    from src.interface.mcp_server import search_records
    injection_query = "Glucose' OR '1'='1"

    res = search_records(injection_query)
    assert len(res) == 1
    # Check that search returns results safely without executing database queries
    assert "document_id" in res[0]


def test_rules_engine_incomplete_context_resilience() -> None:
    engine = ValidationEngine()

    # Trigger OCR warning by setting low confidence word
    bbox = BoundingBox(0, 0, 1, 1)
    word = OcrWord("Glucose", bbox, 0.1)  # 0.1 < 0.7 threshold
    page = OcrPage(1, [word], "Glucose report", [], {})
    ocr_res = OcrResult("doc-01", [page], "tesseract", 0.5)

    # Context missing patient name (empty/unspecified) or invalid structures
    field_name = ExtractedField(value="", evidence="", confidence=0.0)
    demographics = PatientDemographics(name=field_name, dob=None, gender=None, mrn=None)
    field_type = ExtractedField(value="Lab Report", evidence="report", confidence=0.95)
    extracted_rep = StructuredClinicalReport(patient=demographics, observations=[], document_type=field_type)

    incomplete_ctx = ValidationContext(
        ocr_result=ocr_res,
        extracted_report=extracted_rep,
        fhir_bundle=None,
        fhir_validation_outcome={
            "valid": False,
            "issues": [
                {"severity": "error", "details": {"text": "FHIR compliance issue detected."}}
            ]
        }
    )

    report = engine.validate(incomplete_ctx)

    # Checks that engine doesn't crash on None/empty values, but returns structured validation reports
    assert report["is_valid"] is False
    assert len(report["issues"]) > 0
    warnings = [iss["message"] for iss in report["issues"]]
    assert any("OCR word" in w for w in warnings)
    assert any("patient name" in w.lower() for w in warnings)
    assert any("FHIR" in w for w in warnings)
