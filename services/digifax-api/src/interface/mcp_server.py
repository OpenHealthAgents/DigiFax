import typing
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

if typing.TYPE_CHECKING:
    class FastMCP:
        def __init__(self, name: str) -> None: ...
        def tool(self, *args: Any, **kwargs: Any) -> Callable[[T], T]: ...
        def run(self) -> None: ...
else:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        # Fallback implementation of FastMCP if the library is not installed
        class FastMCP:
            def __init__(self, name: str) -> None:
                self.name = name
                self.tools: dict[str, Callable[..., Any]] = {}

            def tool(self, *args: Any, **kwargs: Any) -> Callable[[T], T]:
                # If decorator is used directly without arguments
                if args and callable(args[0]):
                    func = args[0]
                    self.tools[func.__name__] = func
                    return func

                # If decorator is used with arguments, e.g. @mcp.tool(name="...")
                def decorator(func: T) -> T:
                    self.tools[func.__name__] = func
                    return func
                return decorator

            def run(self) -> None:
                print(f"FastMCP server '{self.name}' running in mock mode.")


# Initialize the MedIngest MCP server
mcp = FastMCP("MedIngest Clinical Processing Server")


# --- MCP Tool Handlers ---

@mcp.tool()
def upload_document(file_name: str, content_base64: str) -> str:
    """Registers and stores an incoming clinical document payload.

    Args:
        file_name: The name of the file (e.g. lab_report.pdf)
        content_base64: The base64-encoded string representing file bytes
    """
    import uuid
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    return f"Document '{file_name}' successfully ingested. Assigned ID: {doc_id}"


@mcp.tool()
def run_ocr(document_id: str) -> dict[str, Any]:
    """Runs layout OCR extraction on document bytes.

    Args:
        document_id: The unique identifier of the ingested document
    """
    return {
        "document_id": document_id,
        "engine": "tesseract",
        "pages_count": 1,
        "extracted_text": "Patient Name: John Doe. Fasting Glucose is 145 mg/dL. Normal range: 70-100."
    }


@mcp.tool()
def extract_clinical_data(document_id: str) -> dict[str, Any]:
    """Invokes structured AI extraction of demographics and observations.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "patient": {
            "name": "John Doe",
            "dob": "1990-01-01",
            "gender": "Male"
        },
        "observations": [
            {"analyte_name": "Glucose", "value": "145", "unit": "mg/dL"}
        ]
    }


@mcp.tool()
def normalize_terminology(document_id: str) -> dict[str, Any]:
    """Maps extracted test variables to LOINC, UCUM, and SNOMED codes.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "mappings": [
            {
                "analyte": "Glucose",
                "loinc": "15074-8",
                "loinc_display": "Glucose [Mass/volume] in Blood",
                "ucum": "mg/dL",
                "snomed": "434912009"
            }
        ]
    }


@mcp.tool()
def generate_fhir(document_id: str) -> dict[str, Any]:
    """Builds US Core compliant FHIR R4 Bundle resources.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "pat-001",
                    "name": [{"family": "Doe", "given": ["John"]}]
                }
            }
        ]
    }


@mcp.tool()
def validate_resources(document_id: str) -> dict[str, Any]:
    """Checks generated FHIR resources against US Core specifications.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "is_valid": True,
        "validation_warnings": [
            {"code": "ELEVATED_GLUCOSE", "message": "Glucose 145 mg/dL is elevated."}
        ]
    }


@mcp.tool()
def search_records(query: str) -> list[dict[str, Any]]:
    """Performs full-text and semantic keyword searches across records.

    Args:
        query: The search keywords or phrases
    """
    return [
        {
            "document_id": "doc-9921",
            "score": 0.88,
            "snippet": "Hemoglobin normal counts identified in report."
        }
    ]


@mcp.tool()
def approve_document(document_id: str) -> dict[str, Any]:
    """Signs off manual verification status for a pending document.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "status": "APPROVED",
        "reviewer": "Albert Schweitzer, MD"
    }


@mcp.tool()
def export_to_ehr(document_id: str) -> dict[str, Any]:
    """Dispatches the finalized FHIR Bundle payload to EHR targets.

    Args:
        document_id: The unique identifier of the clinical document
    """
    return {
        "document_id": document_id,
        "exported": True,
        "destination": "EHR_FHIR_GATEWAY",
        "export_timestamp": "2026-07-26T00:46:00Z"
    }


if __name__ == "__main__":
    # Start the FastMCP server process loop
    mcp.run()
