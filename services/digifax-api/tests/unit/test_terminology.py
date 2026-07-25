import sys
from unittest.mock import MagicMock

# --- Pre-emptively mock MDT resources for testing environment isolation ---
mock_mdt_resources = MagicMock()
sys.modules["src.document_to_fhir"] = MagicMock()
sys.modules["src.document_to_fhir.common"] = MagicMock()
sys.modules["src.document_to_fhir.common.schema"] = MagicMock()
sys.modules["src.document_to_fhir.common.schema.resources"] = mock_mdt_resources

from src.domain.terminology.value_objects import TerminologyMapResult
from src.infrastructure.terminology.mdt_terminology_adapter import MdtTerminologyAdapter

# --- 1. Local High-Fidelity DB Lookup Tests ---

def test_local_glucose_lookup() -> None:
    adapter = MdtTerminologyAdapter()
    result = adapter.resolve_code("Fasting Blood Glucose", unit="mg/dL")

    assert isinstance(result, TerminologyMapResult)
    # Check primary LOINC mapping
    assert result.primary_mapping.code == "15074-8"
    assert result.primary_mapping.system == "LOINC"
    assert result.primary_mapping.confidence_score > 0.8

    # Check alternative mappings: UCUM, SNOMED, ICD-10
    alternatives = result.alternative_mappings
    systems = [alt.system for alt in alternatives]
    codes = [alt.code for alt in alternatives]

    assert "UCUM" in systems
    assert "mg/dL" in codes
    assert "SNOMED_CT" in systems
    assert "434912009" in codes
    assert "ICD_10" in systems
    assert "E11.9" in codes


def test_local_drug_assay_lookup() -> None:
    adapter = MdtTerminologyAdapter()
    result = adapter.resolve_code("Serum Digoxin Level")

    assert result.primary_mapping.code == "3558-4"

    # Check RXNORM mapping exists in alternatives
    alternatives = result.alternative_mappings
    rxnorm_maps = [alt for alt in alternatives if alt.system == "RXNORM"]
    assert len(rxnorm_maps) == 1
    assert rxnorm_maps[0].code == "3407"
    assert rxnorm_maps[0].display == "Digoxin"


def test_unknown_analyte_fallback() -> None:
    adapter = MdtTerminologyAdapter()
    result = adapter.resolve_code("Rare unknown chemical analyte")

    assert result.primary_mapping.code == "73999-5"
    assert result.primary_mapping.confidence_score == 0.1
    assert len(result.alternative_mappings) == 0


# --- 2. Injected Google Health MDT Query Engine Test ---

def test_injected_mdt_query_engine() -> None:
    # Setup mock LabTest class in mock_mdt_resources
    mock_labtest_class = MagicMock()
    mock_mdt_resources.LabTest = mock_labtest_class

    # Mock LoincRow returned by MDT query engine
    mock_row1 = MagicMock()
    mock_row1.loinc_num = "12345-6"
    mock_row1.long_common_name = "Mocked TSH common name"

    mock_row2 = MagicMock()
    mock_row2.loinc_num = "98765-4"
    mock_row2.long_common_name = "Alternative TSH common name"

    mock_engine = MagicMock()
    mock_engine.query.return_value = [mock_row1, mock_row2]

    adapter = MdtTerminologyAdapter(loinc_query_engine=mock_engine)
    result = adapter.resolve_code("Thyroid Stimulating Hormone", specimen="Blood", unit="uIU/mL")

    # Verify MDT query was triggered
    mock_engine.query.assert_called_once()

    # Verify mapping parses MDT rows correctly
    assert result.primary_mapping.code == "12345-6"
    assert result.primary_mapping.display == "Mocked TSH common name"
    assert result.primary_mapping.system == "LOINC"

    # Second row should end up in alternatives
    alternatives = result.alternative_mappings
    loinc_alts = [alt for alt in alternatives if alt.system == "LOINC"]
    assert len(loinc_alts) == 1
    assert loinc_alts[0].code == "98765-4"
    assert loinc_alts[0].display == "Alternative TSH common name"

    # UCUM, SNOMED, and ICD-10 should also be resolved for TSH
    systems = [alt.system for alt in alternatives]
    assert "UCUM" in systems
    assert "SNOMED_CT" in systems
    assert "ICD_10" in systems
