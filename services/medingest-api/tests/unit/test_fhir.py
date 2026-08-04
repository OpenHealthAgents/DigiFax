from unittest.mock import MagicMock, patch

import requests

from src.domain.fhir.builders import (
    BundleBuilder,
    DiagnosticReportBuilder,
    ObservationBuilder,
    OrganizationBuilder,
    PatientBuilder,
    PractitionerBuilder,
    SpecimenBuilder,
)
from src.infrastructure.fhir.hapi_fhir_validator import HapiFhirValidator

# --- 1. Fluent Builders Tests ---

def test_patient_builder() -> None:
    patient = (
        PatientBuilder()
        .with_id("pat-456")
        .with_mrn("MRN998877")
        .with_name("Jane", "Doe")
        .with_gender("female")
        .with_birth_date("1985-05-15")
        .build()
    )

    assert patient["resourceType"] == "Patient"
    assert patient["id"] == "pat-456"
    assert "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient" in patient["meta"]["profile"]
    assert patient["gender"] == "female"
    assert patient["birthDate"] == "1985-05-15"
    assert patient["name"][0]["family"] == "Doe"
    assert "Jane" in patient["name"][0]["given"]
    assert patient["identifier"][0]["value"] == "MRN998877"


def test_practitioner_builder() -> None:
    prac = (
        PractitionerBuilder()
        .with_id("prac-789")
        .with_npi("1234567890")
        .with_name("Albert", "Schweitzer")
        .build()
    )

    assert prac["resourceType"] == "Practitioner"
    assert prac["id"] == "prac-789"
    assert "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner" in prac["meta"]["profile"]
    assert prac["identifier"][0]["value"] == "1234567890"
    assert prac["name"][0]["family"] == "Schweitzer"


def test_organization_builder() -> None:
    org = (
        OrganizationBuilder()
        .with_id("org-123")
        .with_npi("9876543210")
        .with_name("General Hospital")
        .build()
    )

    assert org["resourceType"] == "Organization"
    assert org["id"] == "org-123"
    assert "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization" in org["meta"]["profile"]
    assert org["name"] == "General Hospital"


def test_specimen_builder() -> None:
    spec = (
        SpecimenBuilder()
        .with_id("spec-001")
        .with_type("119364003", "Serum specimen")
        .with_subject("pat-456")
        .build()
    )

    assert spec["resourceType"] == "Specimen"
    assert spec["id"] == "spec-001"
    assert spec["subject"]["reference"] == "Patient/pat-456"
    assert spec["type"]["coding"][0]["code"] == "119364003"


def test_observation_builder() -> None:
    obs = (
        ObservationBuilder()
        .with_id("obs-002")
        .with_status("final")
        .with_loinc("15074-8", "Glucose [Mass/volume] in Blood")
        .with_subject("pat-456")
        .with_value(95.0, "mg/dL", "mg/dL")
        .with_specimen("spec-001")
        .build()
    )

    assert obs["resourceType"] == "Observation"
    assert obs["status"] == "final"
    assert obs["subject"]["reference"] == "Patient/pat-456"
    assert obs["specimen"]["reference"] == "Specimen/spec-001"
    assert obs["valueQuantity"]["value"] == 95.0
    assert obs["valueQuantity"]["code"] == "mg/dL"
    assert obs["code"]["coding"][0]["code"] == "15074-8"


def test_diagnostic_report_builder() -> None:
    report = (
        DiagnosticReportBuilder()
        .with_id("rep-003")
        .with_status("final")
        .with_loinc("11502-2", "Laboratory report")
        .with_subject("pat-456")
        .with_performer("org-123")
        .with_specimen("spec-001")
        .with_observation("obs-002")
        .build()
    )

    assert report["resourceType"] == "DiagnosticReport"
    assert report["subject"]["reference"] == "Patient/pat-456"
    assert report["performer"][0]["reference"] == "Organization/org-123"
    assert report["specimen"][0]["reference"] == "Specimen/spec-001"
    assert report["result"][0]["reference"] == "Observation/obs-002"


def test_bundle_builder() -> None:
    patient = PatientBuilder().with_id("pat-456").with_name("Jane", "Doe").build()
    obs = ObservationBuilder().with_id("obs-002").with_loinc("15074-8", "Glucose").build()

    bundle = (
        BundleBuilder()
        .with_id("bun-004")
        .with_type("transaction")
        .with_resource(patient)
        .with_resource(obs)
        .build()
    )

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "transaction"
    assert len(bundle["entry"]) == 2
    assert bundle["entry"][0]["resource"]["resourceType"] == "Patient"
    assert bundle["entry"][0]["request"]["method"] == "PUT"
    assert bundle["entry"][0]["request"]["url"] == "Patient/pat-456"


# --- 2. HAPI FHIR Validator Tests ---

@patch("requests.post")
def test_hapi_validator_success(mock_post: MagicMock) -> None:
    # Setup mock OperationOutcome indicating success (no errors/warnings)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "information",
                "code": "informational",
                "details": {"text": "Validation successful."}
            }
        ]
    }
    mock_post.return_value = mock_response

    validator = HapiFhirValidator()
    patient = PatientBuilder().with_id("pat-456").with_name("Jane", "Doe").build()
    outcome = validator.validate_resource(patient)

    assert outcome["valid"] is True
    assert len(outcome["issues"]) == 1


@patch("requests.post")
def test_hapi_validator_error(mock_post: MagicMock) -> None:
    # Setup mock OperationOutcome indicating validation error
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "invalid",
                "details": {"text": "Patient gender code 'female1' is not recognized."}
            }
        ]
    }
    mock_post.return_value = mock_response

    validator = HapiFhirValidator()
    patient = PatientBuilder().with_id("pat-456").with_name("Jane", "Doe").build()
    outcome = validator.validate_resource(patient)

    assert outcome["valid"] is False
    assert outcome["issues"][0]["severity"] == "error"


@patch("requests.post")
def test_hapi_validator_fallback_local(mock_post: MagicMock) -> None:
    # Simulate API offline connection error
    mock_post.side_effect = requests.exceptions.ConnectionError("API Offline")

    validator = HapiFhirValidator()

    # 1. Test validation passes on complete local resource
    patient_valid = (
        PatientBuilder()
        .with_id("pat-456")
        .with_mrn("MRN111")
        .with_name("Jane", "Doe")
        .build()
    )
    outcome_valid = validator.validate_resource(patient_valid)
    assert outcome_valid["valid"] is True

    # 2. Test validation fails on locally incomplete resource (missing name required by US Core Patient)
    patient_invalid = {
        "resourceType": "Patient",
        "id": "pat-456",
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        }
    }
    outcome_invalid = validator.validate_resource(patient_invalid)
    assert outcome_invalid["valid"] is False
    assert "name" in outcome_invalid["issues"][0]["details"]
