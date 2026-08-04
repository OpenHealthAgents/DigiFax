from src.interface.mcp_server import (
    approve_document,
    export_to_ehr,
    extract_clinical_data,
    generate_fhir,
    mcp,
    normalize_terminology,
    run_ocr,
    search_records,
    upload_document,
    validate_resources,
)

# --- 1. Registration Tests ---

def test_mcp_tool_registration() -> None:
    # Ensure all 9 tools are registered in the server
    # Compatible with both MockFastMCP (using dict) and real FastMCP (using get_tools)
    if hasattr(mcp, "tools"):
        registered_tools = list(mcp.tools.keys())
    else:
        # Fallback for real FastMCP library inspection
        registered_tools = [t.name for t in mcp.get_tools()]  # type: ignore[attr-defined]

    expected = [
        "upload_document",
        "run_ocr",
        "extract_clinical_data",
        "normalize_terminology",
        "generate_fhir",
        "validate_resources",
        "search_records",
        "approve_document",
        "export_to_ehr"
    ]
    for tool_name in expected:
        assert tool_name in registered_tools


# --- 2. Tool Logic Handlers Tests ---

def test_upload_document_tool() -> None:
    res = upload_document("report.pdf", "BASE64_PAYLOAD")
    assert "report.pdf" in res
    assert "Assigned ID" in res


def test_run_ocr_tool() -> None:
    res = run_ocr("doc-1234")
    assert res["document_id"] == "doc-1234"
    assert res["pages_count"] == 1
    assert "Glucose" in res["extracted_text"]


def test_extract_clinical_data_tool() -> None:
    res = extract_clinical_data("doc-1234")
    assert res["patient"]["name"] == "John Doe"
    assert res["observations"][0]["analyte_name"] == "Glucose"


def test_normalize_terminology_tool() -> None:
    res = normalize_terminology("doc-1234")
    assert res["mappings"][0]["loinc"] == "15074-8"
    assert res["mappings"][0]["ucum"] == "mg/dL"


def test_generate_fhir_tool() -> None:
    res = generate_fhir("doc-1234")
    assert res["resourceType"] == "Bundle"
    assert res["type"] == "transaction"


def test_validate_resources_tool() -> None:
    res = validate_resources("doc-1234")
    assert res["is_valid"] is True
    assert res["validation_warnings"][0]["code"] == "ELEVATED_GLUCOSE"


def test_search_records_tool() -> None:
    res = search_records("Glucose levels")
    assert len(res) == 1
    assert res[0]["document_id"] == "doc-9921"
    assert "normal" in res[0]["snippet"]


def test_approve_document_tool() -> None:
    res = approve_document("doc-1234")
    assert res["status"] == "APPROVED"
    assert "MD" in res["reviewer"]


def test_export_to_ehr_tool() -> None:
    res = export_to_ehr("doc-1234")
    assert res["exported"] is True
    assert res["destination"] == "EHR_FHIR_GATEWAY"
