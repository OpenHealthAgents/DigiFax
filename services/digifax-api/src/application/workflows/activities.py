from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

if TYPE_CHECKING:
    class MockActivity:
        def defn(self, *args: Any, **kwargs: Any) -> Callable[[T], T]: ...
    activity: MockActivity
else:
    try:
        from temporalio import activity
    except ImportError:
        class MockActivity:  # type: ignore[no-redef]
            def defn(self, *args: Any, **kwargs: Any) -> Callable[[T], T]:
                if args and callable(args[0]):
                    return args[0]
                return lambda f: f
        activity = MockActivity()  # type: ignore[assignment]

# --- Activity Implementations ---

@activity.defn(name="intake_document")
async def intake_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Captures and registers incoming document metadata."""
    doc_id = payload.get("document_id", "doc-default")
    return {
        "document_id": doc_id,
        "file_name": payload.get("file_name", "report.pdf"),
        "status": "ingested",
        "raw_bytes_len": len(payload.get("content", b""))
    }


@activity.defn(name="perform_ocr")
async def ocr_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Runs layout OCR extraction on document bytes."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "engine": "tesseract",
        "pages": [{"page_number": 1, "text": "Patient Name: John Doe DOB: 1990-01-01. Fasting Glucose 145 mg/dL."}],
        "status": "ocr_completed"
    }


@activity.defn(name="parse_layout")
async def parsing_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Extracts structural sections and reading order from document."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "sections": [
            {"text": "Patient Name: John Doe", "type": "paragraph"},
            {"text": "Glucose 145 mg/dL", "type": "table_cell"}
        ],
        "reading_order": ["section_0", "section_1"],
        "status": "layout_parsed"
    }


@activity.defn(name="extract_clinical_data")
async def extraction_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Invokes LLM extraction for clinical variables."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "patient": {
            "name": "John Doe",
            "dob": "1990-01-01"
        },
        "observations": [
            {"analyte_name": "Glucose", "value": "145", "unit": "mg/dL"}
        ],
        "document_type": "Lab Report",
        "status": "extracted"
    }


@activity.defn(name="resolve_terminology")
async def terminology_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalizes analyte, specimen, and unit to LOINC/UCUM/SNOMED."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "resolved_observations": [
            {
                "analyte_name": "Glucose",
                "value": "145",
                "unit": "mg/dL",
                "loinc": "15074-8",
                "snomed": "434912009",
                "ucum": "mg/dL",
                "icd10": "E11.9"
            }
        ],
        "status": "terminology_resolved"
    }


@activity.defn(name="generate_fhir_bundle")
async def fhir_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Builds FHIR R4 Bundle transaction resources."""
    doc_id = payload.get("document_id")
    # Simulate Bundle JSON output
    bundle_json = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "pat-1",
                    "name": [{"family": "Doe", "given": ["John"]}],
                    "gender": "male"
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-1",
                    "status": "final",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "15074-8"}]},
                    "valueQuantity": {"value": 145, "unit": "mg/dL"}
                }
            }
        ]
    }
    return {
        "document_id": doc_id,
        "fhir_bundle": bundle_json,
        "status": "fhir_generated"
    }


@activity.defn(name="validate_bundle")
async def validation_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Runs clinical validations and FHIR compliance checks."""
    doc_id = payload.get("document_id")
    # Simulate validation results: flag elevated Glucose value warning (not impossible error)
    return {
        "document_id": doc_id,
        "is_valid": True,
        "issues": [
            {"code": "ELEVATED_GLUCOSE", "message": "Glucose 145 mg/dL is elevated.", "severity": "warning"}
        ],
        "status": "validated"
    }


@activity.defn(name="export_data")
async def export_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatches validated bundle to external EHR ports."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "exported": True,
        "destination": "EHR_HL7_FHIR_ENDPOINT",
        "status": "exported"
    }


@activity.defn(name="archive_document")
async def archival_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Archives raw document and clinical JSON outcomes."""
    doc_id = payload.get("document_id")
    return {
        "document_id": doc_id,
        "archived": True,
        "storage_bucket": "digifax-cold-archive",
        "status": "archived"
    }
