import inspect

from src.interface.mcp_server import (
    approve_document,
    export_to_ehr,
    extract_clinical_data,
    generate_fhir,
    normalize_terminology,
    run_ocr,
    search_records,
    upload_document,
    validate_resources,
)


def test_mcp_tool_parameter_contracts() -> None:
    # Verify parameter contracts using python signature inspection

    # 1. upload_document contract
    sig_upload = inspect.signature(upload_document)
    assert "file_name" in sig_upload.parameters
    assert "content_base64" in sig_upload.parameters
    assert sig_upload.parameters["file_name"].annotation is str
    assert sig_upload.parameters["content_base64"].annotation is str

    # 2. run_ocr contract
    sig_ocr = inspect.signature(run_ocr)
    assert "document_id" in sig_ocr.parameters
    assert sig_ocr.parameters["document_id"].annotation is str

    # 3. extract_clinical_data contract
    sig_extract = inspect.signature(extract_clinical_data)
    assert "document_id" in sig_extract.parameters
    assert sig_extract.parameters["document_id"].annotation is str

    # 4. normalize_terminology contract
    sig_normalize = inspect.signature(normalize_terminology)
    assert "document_id" in sig_normalize.parameters
    assert sig_normalize.parameters["document_id"].annotation is str

    # 5. generate_fhir contract
    sig_fhir = inspect.signature(generate_fhir)
    assert "document_id" in sig_fhir.parameters
    assert sig_fhir.parameters["document_id"].annotation is str

    # 6. validate_resources contract
    sig_validate = inspect.signature(validate_resources)
    assert "document_id" in sig_validate.parameters
    assert sig_validate.parameters["document_id"].annotation is str

    # 7. search_records contract
    sig_search = inspect.signature(search_records)
    assert "query" in sig_search.parameters
    assert sig_search.parameters["query"].annotation is str

    # 8. approve_document contract
    sig_approve = inspect.signature(approve_document)
    assert "document_id" in sig_approve.parameters
    assert sig_approve.parameters["document_id"].annotation is str

    # 9. export_to_ehr contract
    sig_export = inspect.signature(export_to_ehr)
    assert "document_id" in sig_export.parameters
    assert sig_export.parameters["document_id"].annotation is str
