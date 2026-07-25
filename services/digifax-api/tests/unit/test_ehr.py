from unittest.mock import MagicMock, patch

from src.infrastructure.ehr.athena_exporter import AthenaExporter
from src.infrastructure.ehr.bulk_fhir_exporter import BulkFhirExporter
from src.infrastructure.ehr.cerner_exporter import CernerExporter
from src.infrastructure.ehr.epic_exporter import EpicExporter
from src.infrastructure.ehr.hapi_fhir_exporter import HapiFhirExporter
from src.infrastructure.ehr.medplum_exporter import MedplumExporter
from src.infrastructure.ehr.smart_launch import SmartLaunchManager

# --- 1. HAPI FHIR Exporter Tests ---

@patch("requests.post")
def test_hapi_fhir_exporter_success(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "bundle-01", "resourceType": "Bundle"}
    mock_post.return_value = mock_response

    exporter = HapiFhirExporter(base_url="https://hapi.local/fhir")
    bundle = {"resourceType": "Bundle", "id": "bundle-01"}

    res = exporter.export_bundle(bundle, "key-123")
    assert res["id"] == "bundle-01"

    # Test idempotency key bypass
    res_dup = exporter.export_bundle(bundle, "key-123")
    assert res_dup["status"] == "duplicate_bypassed"


# --- 2. Medplum Exporter Tests ---

@patch("requests.post")
def test_medplum_exporter_auth_and_post(mock_post: MagicMock) -> None:
    # 1st call for token exchange, 2nd call for fhir post
    mock_token_res = MagicMock()
    mock_token_res.json.return_value = {"access_token": "medplum-token"}

    mock_fhir_res = MagicMock()
    mock_fhir_res.status_code = 200
    mock_fhir_res.json.return_value = {"resourceType": "Bundle", "id": "bundle-medplum"}

    mock_post.side_effect = [mock_token_res, mock_fhir_res]

    exporter = MedplumExporter(
        auth_url="https://medplum.auth",
        fhir_url="https://medplum.fhir",
        client_id="id-1",
        client_secret="sec-1"
    )

    res = exporter.export_bundle({"resourceType": "Bundle"}, "key-456")
    assert res["id"] == "bundle-medplum"


# --- 3. Epic Exporter Tests ---

@patch("requests.post")
def test_epic_exporter_auth_assertion(mock_post: MagicMock) -> None:
    mock_token_res = MagicMock()
    mock_token_res.json.return_value = {"access_token": "epic-token"}

    mock_fhir_res = MagicMock()
    mock_fhir_res.status_code = 201
    mock_fhir_res.json.return_value = {"id": "bundle-epic"}

    mock_post.side_effect = [mock_token_res, mock_fhir_res]

    exporter = EpicExporter(
        token_url="https://epic.token",
        fhir_url="https://epic.fhir",
        client_id="client-epic"
    )

    res = exporter.export_bundle({"resourceType": "Bundle"}, "key-789")
    assert res["id"] == "bundle-epic"


# --- 4. Cerner Exporter Tests ---

@patch("requests.post")
def test_cerner_exporter(mock_post: MagicMock) -> None:
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {"id": "bundle-cerner"}
    mock_post.return_value = mock_res

    exporter = CernerExporter(fhir_url="https://cerner.fhir", auth_header="Bearer cerner-key")
    res = exporter.export_bundle({"resourceType": "Bundle"}, "key-abc")
    assert res["id"] == "bundle-cerner"


# --- 5. Athena Exporter Tests ---

@patch("requests.post")
def test_athena_exporter(mock_post: MagicMock) -> None:
    mock_token_res = MagicMock()
    mock_token_res.json.return_value = {"access_token": "athena-token"}

    mock_api_res = MagicMock()
    mock_api_res.status_code = 201
    mock_api_res.json.return_value = {"id": "athena-note-1"}

    mock_post.side_effect = [mock_token_res, mock_api_res]

    exporter = AthenaExporter(
        auth_url="https://athena.auth",
        api_url="https://athena.api",
        key="athena-key",
        secret="athena-secret"
    )

    res = exporter.export_bundle({"id": "note"}, "key-xyz")
    assert res["id"] == "athena-note-1"


# --- 6. SMART on FHIR Launch Flow Tests ---

@patch("requests.get")
@patch("requests.post")
def test_smart_launch_discovery_and_exchange(mock_post: MagicMock, mock_get: MagicMock) -> None:
    # 1. Discover Endpoints Mock
    mock_config_res = MagicMock()
    mock_config_res.status_code = 200
    mock_config_res.json.return_value = {
        "authorization_endpoint": "https://ehr.auth/authorize",
        "token_endpoint": "https://ehr.auth/token"
    }
    mock_get.return_value = mock_config_res

    manager = SmartLaunchManager()
    endpoints = manager.discover_endpoints("https://ehr.iss/fhir")
    assert endpoints["authorization_endpoint"] == "https://ehr.auth/authorize"

    # 2. Exchange Auth Code Mock
    mock_token_res = MagicMock()
    mock_token_res.json.return_value = {
        "access_token": "smart-token-99",
        "patient": "pat-smart-11",
        "encounter": "enc-smart-22"
    }
    mock_post.return_value = mock_token_res

    context = manager.exchange_authorization_code(
        token_url="https://ehr.auth/token",
        code="auth-code-123",
        redirect_uri="https://app.local/redirect",
        client_id="app-client"
    )

    assert context["access_token"] == "smart-token-99"
    assert context["patient_id"] == "pat-smart-11"


# --- 7. Bulk FHIR Export Tests ---

@patch("requests.get")
def test_bulk_fhir_export_flow(mock_get: MagicMock) -> None:
    # Mock initiate returning polling header Content-Location
    mock_init_res = MagicMock()
    mock_init_res.status_code = 202
    mock_init_res.headers = {"Content-Location": "https://bulk.local/poll-job-1"}

    # Mock polling status calls (1st is 202 Accepted, 2nd is 200 OK with NDJSON manifest)
    mock_poll_202 = MagicMock()
    mock_poll_202.status_code = 202

    mock_poll_200 = MagicMock()
    mock_poll_200.status_code = 200
    mock_poll_200.json.return_value = {
        "output": [{"type": "Patient", "url": "https://bulk.local/patient.ndjson"}]
    }

    # Mock download NDJSON file call
    mock_download_res = MagicMock()
    mock_download_res.status_code = 200
    mock_download_res.text = '{"resourceType":"Patient","id":"1"}\n{"resourceType":"Patient","id":"2"}\n'

    mock_get.side_effect = [mock_init_res, mock_poll_202, mock_poll_200, mock_download_res]

    bulk = BulkFhirExporter()
    poll_url = bulk.initiate_export("https://bulk.local/Patient/$export", "token-abc")
    assert poll_url == "https://bulk.local/poll-job-1"

    # Poll 1: still running
    status_1 = bulk.poll_export_status(poll_url, "token-abc")
    assert status_1 is None

    # Poll 2: completed
    status_2 = bulk.poll_export_status(poll_url, "token-abc")
    assert status_2 is not None
    assert status_2["output"][0]["url"] == "https://bulk.local/patient.ndjson"

    # Download NDJSON
    file_content = bulk.download_file(status_2["output"][0]["url"], "token-abc")
    assert "Patient" in file_content
