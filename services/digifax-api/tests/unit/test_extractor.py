import sys
from unittest.mock import MagicMock, patch

# --- Pre-emptively mock litellm module in sys.modules ---
mock_litellm_module = MagicMock()
sys.modules["litellm"] = mock_litellm_module

import pytest

from src.domain.common.exceptions import DomainException
from src.domain.extraction.layout import (
    LayoutHierarchyNode,
    LayoutSection,
    LayoutTable,
    NormalizedLayoutDocument,
)
from src.domain.extraction.schemas import StructuredClinicalReport
from src.domain.ocr.value_objects import BoundingBox
from src.infrastructure.extraction.litellm_extractor import LiteLlmExtractor

# --- Mock Document Setup Helper ---

def get_mock_layout_doc() -> NormalizedLayoutDocument:
    bbox = BoundingBox(0.0, 0.0, 1.0, 1.0)
    sec1 = LayoutSection("CLINICAL LAB REPORT", 1, 1, 0, bbox)
    sec2 = LayoutSection("Patient: John Doe", 0, 1, 1, bbox)
    table = LayoutTable([["Glucose", "95", "mg/dL"]], 1, bbox)
    hierarchy = LayoutHierarchyNode("Root", "document", None)

    return NormalizedLayoutDocument(
        document_id="doc-123",
        sections=[sec1, sec2],
        tables=[table],
        key_value_pairs=[],
        hierarchy_root=hierarchy,
        reading_order=["section_0", "section_1", "table_0"]
    )

def setup_function() -> None:
    mock_litellm_module.reset_mock(return_value=True, side_effect=True)
    mock_litellm_module.completion.reset_mock(return_value=True, side_effect=True)


# --- 1. Serialization Tests ---

def test_document_serialization() -> None:
    doc = get_mock_layout_doc()
    extractor = LiteLlmExtractor()
    serialized = extractor._serialize_document(doc)

    expected = (
        "# CLINICAL LAB REPORT\n\n"
        "Patient: John Doe\n\n"
        "[Table]\n\n"
        "Glucose | 95 | mg/dL\n\n"
        "[End Table]"
    )
    assert serialized == expected


# --- 2. Successful Extraction Tests ---

@patch("time.sleep")
def test_successful_extraction(mock_sleep: MagicMock) -> None:
    # Setup mock litellm response content
    valid_json = (
        "{\n"
        "  \"patient\": {\n"
        "    \"name\": { \"value\": \"John Doe\", \"evidence\": \"John Doe\", \"confidence\": 0.99 }\n"
        "  },\n"
        "  \"observations\": [\n"
        "    {\n"
        "      \"analyte_name\": { \"value\": \"Glucose\", \"evidence\": \"Glucose\", \"confidence\": 0.95 },\n"
        "      \"value\": { \"value\": \"95\", \"evidence\": \"95\", \"confidence\": 0.95 }\n"
        "    }\n"
        "  ],\n"
        "  \"document_type\": { \"value\": \"Lab Report\", \"evidence\": \"LAB REPORT\", \"confidence\": 0.95 }\n"
        "}"
    )

    mock_choice = MagicMock()
    mock_choice.message.content = valid_json
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_litellm_module.completion.return_value = mock_response

    extractor = LiteLlmExtractor(fallback_models=["test-model"])
    doc = get_mock_layout_doc()

    report = extractor.extract_clinical_data(doc)

    assert isinstance(report, StructuredClinicalReport)
    assert report.patient.name.value == "John Doe"
    assert report.document_type.value == "Lab Report"
    assert len(report.observations) == 1
    assert report.observations[0].analyte_name.value == "Glucose"
    assert report.observations[0].value.value == "95"


# --- 3. Retries Tests ---

@patch("time.sleep")
def test_extraction_retries_on_failure(mock_sleep: MagicMock) -> None:
    # First 2 calls raise API error; 3rd succeeds
    valid_json = (
        "{\n"
        "  \"patient\": {\n"
        "    \"name\": { \"value\": \"John Doe\", \"evidence\": \"John Doe\", \"confidence\": 0.99 }\n"
        "  },\n"
        "  \"observations\": [],\n"
        "  \"document_type\": { \"value\": \"Lab Report\", \"evidence\": \"LAB REPORT\", \"confidence\": 0.95 }\n"
        "}"
    )
    mock_choice = MagicMock()
    mock_choice.message.content = valid_json
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_litellm_module.completion.side_effect = [
        Exception("Rate limit exceeded"),
        Exception("Timeout"),
        mock_response
    ]

    extractor = LiteLlmExtractor(fallback_models=["test-model"], max_retries=3)
    doc = get_mock_layout_doc()

    report = extractor.extract_clinical_data(doc)
    assert report.patient.name.value == "John Doe"
    assert mock_sleep.call_count == 2  # Verifies exponential backoff slept twice


# --- 4. Failover Tests ---

@patch("time.sleep")
def test_extractor_failover_to_fallback_model(mock_sleep: MagicMock) -> None:
    # First model always fails; second model succeeds
    valid_json = (
        "{\n"
        "  \"patient\": {\n"
        "    \"name\": { \"value\": \"John Doe\", \"evidence\": \"John Doe\", \"confidence\": 0.99 }\n"
        "  },\n"
        "  \"observations\": [],\n"
        "  \"document_type\": { \"value\": \"Lab Report\", \"evidence\": \"LAB REPORT\", \"confidence\": 0.95 }\n"
        "}"
    )
    mock_choice = MagicMock()
    mock_choice.message.content = valid_json
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    # First 3 calls (first model) fail, 4th call (second model) succeeds
    mock_litellm_module.completion.side_effect = [
        Exception("API Error"),
        Exception("API Error"),
        Exception("API Error"),
        mock_response
    ]

    extractor = LiteLlmExtractor(fallback_models=["failing-model", "succeeding-model"], max_retries=3)
    doc = get_mock_layout_doc()

    report = extractor.extract_clinical_data(doc)
    assert report.patient.name.value == "John Doe"
    assert mock_litellm_module.completion.call_count == 4


# --- 5. Global Failures ---

@patch("time.sleep")
def test_extractor_global_failure_raises_exception(mock_sleep: MagicMock) -> None:
    mock_litellm_module.completion.side_effect = Exception("Permanent API Outage")

    extractor = LiteLlmExtractor(fallback_models=["model1", "model2"], max_retries=2)
    doc = get_mock_layout_doc()

    with pytest.raises(DomainException) as exc_info:
        extractor.extract_clinical_data(doc)
    assert exc_info.value.code == "AI_EXTRACTION_FAILED"
