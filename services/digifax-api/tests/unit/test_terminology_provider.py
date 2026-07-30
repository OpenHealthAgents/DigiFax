"""
test_terminology_provider.py
Unit and controller integration tests verifying Terminology translations, approvals, and rollbacks.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.terminology.value_objects import FHIRCoding, ConceptMapRule
from src.domain.terminology.entities import TenantConceptMap, TenantValueSetOverride
from src.application.use_cases.terminology.propose_local_mapping import ProposeLocalMappingUseCase
from src.application.use_cases.terminology.approve_concept_mapping import ApproveConceptMappingUseCase
from src.application.use_cases.terminology.rollback_concept_map import RollbackConceptMapUseCase
from src.application.use_cases.terminology.get_concept_mapping import GetConceptMappingUseCase
from src.infrastructure.persistence.in_memory_terminology_repository import InMemoryTerminologyRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.main import app


def test_fhir_coding_validations() -> None:
    # 1. Valid params
    coding = FHIRCoding("http://loinc.org", "883-9", "ABO+Rh blood group")
    assert coding.code == "883-9"

    # 2. Empty system
    with pytest.raises(ValueError):
        FHIRCoding("", "883-9", "ABO+Rh blood group")

    # 3. Empty code
    with pytest.raises(ValueError):
        FHIRCoding("http://loinc.org", " ", "ABO+Rh blood group")


def test_mapping_approval_and_translation_lifecycle() -> None:
    repo = InMemoryTerminologyRepository()
    propose_use_case = ProposeLocalMappingUseCase(repo)
    approve_use_case = ApproveConceptMappingUseCase(repo)
    translate_use_case = GetConceptMappingUseCase(repo)

    # 1. Propose mapping
    propose_use_case.execute(
        tenant_id="tenant-charlie",
        mapping_key="lab_codes",
        source_system="local_lab",
        source_code="WBC_COUNT",
        target_system="http://loinc.org",
        target_code="26464-8",
        preferred_display="White Blood Cell Count"
    )

    # 2. Try translate before approval - must return None (ignored pending rule)
    res_pending = translate_use_case.execute(
        tenant_id="tenant-charlie",
        mapping_key="lab_codes",
        source_system="local_lab",
        source_code="WBC_COUNT"
    )
    assert res_pending is None

    # 3. Approve mapping
    approve_use_case.execute(
        tenant_id="tenant-charlie",
        mapping_key="lab_codes",
        source_system="local_lab",
        source_code="WBC_COUNT",
        target_system="http://loinc.org",
        target_code="26464-8"
    )

    # 4. Translate again - must succeed
    res_approved = translate_use_case.execute(
        tenant_id="tenant-charlie",
        mapping_key="lab_codes",
        source_system="local_lab",
        source_code="WBC_COUNT"
    )
    assert res_approved is not None
    assert res_approved.system == "http://loinc.org"
    assert res_approved.code == "26464-8"
    assert res_approved.display == "White Blood Cell Count"


def test_valueset_display_overrides() -> None:
    repo = InMemoryTerminologyRepository()
    translate_use_case = GetConceptMappingUseCase(repo)

    # Seed approved map
    concept_map = TenantConceptMap("tenant-delta", "med_codes")
    concept_map.propose_rule("local_rx", "MET", "http://www.nlm.nih.gov/research/umls/rxnorm", "866418", "Metformin")
    concept_map.approve_rule("local_rx", "MET", "http://www.nlm.nih.gov/research/umls/rxnorm", "866418")
    repo.save_concept_map(concept_map)

    # Resolve default display
    res_default = translate_use_case.execute(
        tenant_id="tenant-delta",
        mapping_key="med_codes",
        source_system="local_rx",
        source_code="MET"
    )
    assert res_default.display == "Metformin"

    # Seed Custom ValueSet Display Override
    override = TenantValueSetOverride("tenant-delta", "http://www.nlm.nih.gov/research/umls/rxnorm")
    override.set_override("866418", "Metformin HCl 500mg tab (Customized)")
    repo.save_valueset_override(override)

    # Translate should apply override
    res_overridden = translate_use_case.execute(
        tenant_id="tenant-delta",
        mapping_key="med_codes",
        source_system="local_rx",
        source_code="MET"
    )
    assert res_overridden.display == "Metformin HCl 500mg tab (Customized)"


def test_concept_map_rollback_history() -> None:
    repo = InMemoryTerminologyRepository()
    concept_map = TenantConceptMap("tenant-echo", "icd_codes")
    repo.save_concept_map(concept_map)
    assert concept_map.version == 1

    # v2: Propose Rule 1
    concept_map.propose_rule("local_dx", "DIA", "http://hl7.org/fhir/sid/icd-10", "E11.9", "Diabetes")
    repo.save_concept_map(concept_map)
    assert concept_map.version == 2

    # v3: Propose Rule 2
    concept_map.propose_rule("local_dx", "HYP", "http://hl7.org/fhir/sid/icd-10", "I10", "Hypertension")
    repo.save_concept_map(concept_map)
    assert concept_map.version == 3

    assert len(concept_map.rules) == 2

    # Rollback back to v2 (which only has Rule 1)
    concept_map.rollback_to_version(2)
    assert concept_map.version == 2
    assert len(concept_map.rules) == 1
    assert concept_map.rules[0].source_code == "DIA"


def test_terminology_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Propose local mapping rule
    propose_res = client.post(
        "/api/terminology/mapping/propose",
        headers={"X-Tenant-Id": "tenant-fastapi"},
        json={
            "mapping_key": "lab_codes",
            "source_system": "local_lab",
            "source_code": "GLU",
            "target_system": "http://loinc.org",
            "target_code": "15074-8",
            "preferred_display": "Glucose"
        }
    )
    assert propose_res.status_code == 201
    assert propose_res.json()["rules_count"] == 1

    # 2. Try translate (fails with 404 because not approved yet)
    trans_pending = client.get(
        "/api/terminology/translate",
        headers={"X-Tenant-Id": "tenant-fastapi"},
        params={
            "mapping_key": "lab_codes",
            "source_system": "local_lab",
            "source_code": "GLU"
        }
    )
    assert trans_pending.status_code == 404

    # 3. Approve local mapping
    approve_res = client.post(
        "/api/terminology/mapping/approve",
        headers={"X-Tenant-Id": "tenant-fastapi"},
        json={
            "mapping_key": "lab_codes",
            "source_system": "local_lab",
            "source_code": "GLU",
            "target_system": "http://loinc.org",
            "target_code": "15074-8"
        }
    )
    assert approve_res.status_code == 200

    # 4. Try translate again (succeeds!)
    trans_approved = client.get(
        "/api/terminology/translate",
        headers={"X-Tenant-Id": "tenant-fastapi"},
        params={
            "mapping_key": "lab_codes",
            "source_system": "local_lab",
            "source_code": "GLU"
        }
    )
    assert trans_approved.status_code == 200
    assert trans_approved.json()["code"] == "15074-8"
    assert trans_approved.json()["display"] == "Glucose"
