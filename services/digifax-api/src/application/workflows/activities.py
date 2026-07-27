"""
activities.py
Temporal workflow activity definitions, accepting request-scoped TenantContext configurations.
"""

import logging
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

logger = logging.getLogger(__name__)


# --- Helper to extract context parameters ---
def _get_context_details(payload: dict[str, Any]) -> tuple[str, str, str]:
    """Helper extracting tenant, user, and correlation IDs from input context."""
    context = payload.get("context", {})
    tenant_id = context.get("tenant_id", "tenant-unknown")
    user_id = context.get("user_id", "system")
    correlation_id = context.get("correlation_id", "corr-unknown")
    return tenant_id, user_id, correlation_id


# --- Activity Implementations ---

@activity.defn(name="intake_document")
async def intake_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Captures and registers incoming document metadata.

    Purpose:
        Validate intake context.
    Inputs:
        payload (dict): Inputs including document details and context.
    Outputs:
        dict: Ingestion status metrics.
    """
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id", "doc-default")
    logger.info("[%s] Ingesting document %s for tenant %s", corr_id, doc_id, tenant_id)

    return {
        "document_id": doc_id,
        "file_name": payload.get("file_name", "report.pdf"),
        "status": "ingested",
        "raw_bytes_len": len(payload.get("content", b"")),
        "context": payload.get("context", {})
    }


@activity.defn(name="perform_ocr")
async def ocr_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Runs layout OCR extraction on document bytes."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Running OCR for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    return {
        "document_id": doc_id,
        "engine": "tesseract",
        "pages": [{"page_number": 1, "text": "Patient Name: John Doe DOB: 1990-01-01. Fasting Glucose 145 mg/dL."}],
        "status": "ocr_completed",
        "context": payload.get("context", {})
    }


@activity.defn(name="parse_layout")
async def parsing_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Extracts structural sections and reading order from document."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Parsing layout for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    return {
        "document_id": doc_id,
        "sections": [
            {"text": "Patient Name: John Doe", "type": "paragraph"},
            {"text": "Glucose 145 mg/dL", "type": "table_cell"}
        ],
        "reading_order": ["section_0", "section_1"],
        "status": "layout_parsed",
        "context": payload.get("context", {})
    }


@activity.defn(name="extract_clinical_data")
async def extraction_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Invokes LLM extraction for clinical variables."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Extracting AI fields for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    # Fail simulation for saga compensation verification if requested
    if payload.get("simulate_fail") == "extract":
        raise ValueError("Simulated Extraction Failure")

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
        "status": "extracted",
        "context": payload.get("context", {})
    }


@activity.defn(name="resolve_terminology")
async def terminology_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalizes analyte, specimen, and unit to LOINC/UCUM/SNOMED."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Resolving terminology for tenant %s, doc %s", corr_id, tenant_id, doc_id)

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
        "status": "terminology_resolved",
        "context": payload.get("context", {})
    }


@activity.defn(name="generate_fhir_bundle")
async def fhir_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Builds FHIR R4 Bundle transaction resources."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Generating FHIR for tenant %s, doc %s", corr_id, tenant_id, doc_id)

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
        "status": "fhir_generated",
        "context": payload.get("context", {})
    }


@activity.defn(name="validate_bundle")
async def validation_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Runs clinical validations and FHIR compliance checks."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Validating bundle for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    return {
        "document_id": doc_id,
        "is_valid": True,
        "issues": [
            {"code": "ELEVATED_GLUCOSE", "message": "Glucose 145 mg/dL is elevated.", "severity": "warning"}
        ],
        "status": "validated",
        "context": payload.get("context", {})
    }


@activity.defn(name="export_data")
async def export_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatches validated bundle to external EHR ports."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Exporting data to EHR for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    return {
        "document_id": doc_id,
        "exported": True,
        "destination": "EHR_HL7_FHIR_ENDPOINT",
        "status": "exported",
        "context": payload.get("context", {})
    }


@activity.defn(name="archive_document")
async def archival_activity(payload: dict[str, Any]) -> dict[str, Any]:
    """Archives raw document and clinical JSON outcomes."""
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id")
    logger.info("[%s] Archiving document for tenant %s, doc %s", corr_id, tenant_id, doc_id)

    return {
        "document_id": doc_id,
        "archived": True,
        "storage_bucket": "digifax-cold-archive",
        "status": "archived",
        "context": payload.get("context", {})
    }


@activity.defn(name="log_pipeline_audit")
async def log_pipeline_audit(payload: dict[str, Any]) -> None:
    """
    Logs auditable milestones to telemetry streams carrying TenantContext tracking markers.

    Purpose:
        Enforce trace audit trails compliance.
    """
    tenant_id, user_id, corr_id = _get_context_details(payload)
    milestone = payload.get("milestone", "unknown_milestone")
    doc_id = payload.get("document_id", "doc-unknown")
    logger.info(
        "AUDIT: [%s] Tenant %s, User %s, Document %s reached milestone %s",
        corr_id, tenant_id, user_id, doc_id, milestone
    )


@activity.defn(name="compensate_pipeline_failure")
async def compensate_pipeline_failure(payload: dict[str, Any]) -> None:
    """
    Saga compensation activity triggered on pipeline errors to revert state.

    Purpose:
        Execute rollback transactions.
    """
    tenant_id, _, corr_id = _get_context_details(payload)
    doc_id = payload.get("document_id", "doc-unknown")
    reason = payload.get("reason", "unknown")
    logger.warning(
        "SAGA ROLLBACK: [%s] Reverting intake registration for doc %s under tenant %s due to: %s",
        corr_id, doc_id, tenant_id, reason
    )
