"""
test_fhir_profile_provider.py
Unit and controller integration tests verifying FHIR Profile configurations and validation pipelines.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.fhir_profile.value_objects import FHIRImplementationGuide
from src.domain.fhir_profile.entities import TenantFHIRProfileConfiguration, FHIRStructureDefinition
from src.application.use_cases.fhir_profile.configure_active_igs import ConfigureActiveIGsUseCase
from src.application.use_cases.fhir_profile.upload_structure_definition import UploadStructureDefinitionUseCase
from src.application.use_cases.fhir_profile.validate_fhir_resource import ValidateFHIRResourceUseCase
from src.infrastructure.persistence.in_memory_fhir_profile_repository import InMemoryFHIRProfileRepository
from src.main import app


def test_fhir_ig_validations() -> None:
    # Valid
    ig = FHIRImplementationGuide("US Core", "http://hl7.org/fhir/us/core", "v3.1.1")
    assert ig.version == "v3.1.1"

    # Empty URL
    with pytest.raises(ValueError):
        FHIRImplementationGuide("US Core", " ", "v3.1.1")

    # Empty Name
    with pytest.raises(ValueError):
        FHIRImplementationGuide("", "http://hl7.org/fhir/us/core", "v3.1.1")


def test_fhir_validation_pipeline_lifecycle() -> None:
    repo = InMemoryFHIRProfileRepository()
    config_use_case = ConfigureActiveIGsUseCase(repo)
    validate_use_case = ValidateFHIRResourceUseCase(repo)

    # 1. Config active IGs for tenant-alpha (US Core active)
    config_use_case.execute(
        tenant_id="tenant-alpha",
        active_igs=["http://hl7.org/fhir/us/core"]
    )

    # 2. Validate patient - fails if required fields missing (name, identifier, gender)
    invalid_patient = {
        "resourceType": "Patient",
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        },
        "identifier": [{"value": "123"}]
        # name and gender missing
    }

    res_invalid = validate_use_case.execute(tenant_id="tenant-alpha", resource=invalid_patient)
    assert not res_invalid.valid
    assert any("name" in err for err in res_invalid.errors)
    assert any("gender" in err for err in res_invalid.errors)

    # 3. Validate patient - succeeds when fields are present
    valid_patient = {
        "resourceType": "Patient",
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        },
        "identifier": [{"value": "123"}],
        "name": [{"family": "Smith", "given": ["John"]}],
        "gender": "male"
    }

    res_valid = validate_use_case.execute(tenant_id="tenant-alpha", resource=valid_patient)
    assert res_valid.valid
    assert len(res_valid.errors) == 0


def test_validate_profile_not_active() -> None:
    repo = InMemoryFHIRProfileRepository()
    config_use_case = ConfigureActiveIGsUseCase(repo)
    validate_use_case = ValidateFHIRResourceUseCase(repo)

    # Config tenant-beta to ONLY support International Patient Summary (IPS)
    config_use_case.execute(
        tenant_id="tenant-beta",
        active_igs=["http://hl7.org/fhir/uv/ips"]
    )

    # Patient using US Core Patient profile
    patient_resource = {
        "resourceType": "Patient",
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        },
        "identifier": [{"value": "123"}],
        "name": [{"family": "Smith"}],
        "gender": "male"
    }

    # Should fail because US Core is not in active_igs
    res = validate_use_case.execute(tenant_id="tenant-beta", resource=patient_resource)
    assert not res.valid
    assert "Implementation Guide containing profile" in res.errors[0]


def test_custom_structure_definitions() -> None:
    repo = InMemoryFHIRProfileRepository()
    config_use_case = ConfigureActiveIGsUseCase(repo)
    upload_use_case = UploadStructureDefinitionUseCase(repo)
    validate_use_case = ValidateFHIRResourceUseCase(repo)

    # Register active configuration
    config_use_case.execute(tenant_id="tenant-gamma", active_igs=[])

    # Upload custom patient profile requiring birthDate
    custom_profile_url = "http://myclinic.org/fhir/StructureDefinition/my-patient"
    upload_use_case.execute(
        tenant_id="tenant-gamma",
        url=custom_profile_url,
        resource_type="Patient",
        required_paths=["name", "birthDate"]
    )

    # Validate resource missing birthDate
    resource_invalid = {
        "resourceType": "Patient",
        "meta": {
            "profile": [custom_profile_url]
        },
        "name": [{"family": "Jones"}]
    }

    res_invalid = validate_use_case.execute(tenant_id="tenant-gamma", resource=resource_invalid)
    assert not res_invalid.valid
    assert "birthDate" in res_invalid.errors[0]

    # Validate resource with birthDate
    resource_valid = {
        "resourceType": "Patient",
        "meta": {
            "profile": [custom_profile_url]
        },
        "name": [{"family": "Jones"}],
        "birthDate": "1990-01-01"
    }
    res_valid = validate_use_case.execute(tenant_id="tenant-gamma", resource=resource_valid)
    assert res_valid.valid


def test_fhir_profile_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Post config (enable US Core)
    config_res = client.post(
        "/api/fhir/profile/config",
        headers={"X-Tenant-Id": "tenant-http"},
        json={"active_igs": ["http://hl7.org/fhir/us/core"]}
    )
    assert config_res.status_code == 200
    assert "http://hl7.org/fhir/us/core" in config_res.json()["active_igs"]

    # 2. Upload custom profile StructureDefinition
    upload_res = client.post(
        "/api/fhir/profile/structure-definition",
        headers={"X-Tenant-Id": "tenant-http"},
        json={
            "url": "http://myclinic.org/fhir/StructureDefinition/vital-signs",
            "resource_type": "Observation",
            "required_paths": ["status", "code", "valueQuantity"]
        }
    )
    assert upload_res.status_code == 201
    assert upload_res.json()["resource_type"] == "Observation"

    # 3. Validate matching payload - fails on missing valueQuantity
    validate_res = client.post(
        "/api/fhir/profile/validate",
        headers={"X-Tenant-Id": "tenant-http"},
        json={
            "resourceType": "Observation",
            "meta": {
                "profile": ["http://myclinic.org/fhir/StructureDefinition/vital-signs"]
            },
            "status": "final",
            "code": {"text": "Heart Rate"}
        }
    )
    assert validate_res.status_code == 200
    assert not validate_res.json()["valid"]
    assert "valueQuantity" in validate_res.json()["errors"][0]
