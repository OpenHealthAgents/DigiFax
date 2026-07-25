from unittest.mock import MagicMock

from src.application.services.validation_engine import ValidationEngine
from src.domain.extraction.schemas import (
    ClinicalObservation,
    ExtractedField,
    PatientDemographics,
    StructuredClinicalReport,
)
from src.domain.fhir.builders import BundleBuilder, ObservationBuilder, PatientBuilder
from src.domain.ocr.value_objects import BoundingBox, OcrPage, OcrResult, OcrWord
from src.domain.validation.rules import ValidationContext
from tests.helpers.synthetic_document_generator import generate_synthetic_extraction_data


def test_full_e2e_integration_pipeline() -> None:
    # 1. Synthesize extraction data
    data = generate_synthetic_extraction_data(
        patient_name="Elizabeth Blackwell",
        glucose_val=145.0,
        cholesterol_val=210.0
    )

    # 2. Build FHIR Bundle
    pat = PatientBuilder().with_id("pat-01").with_name("Elizabeth", "Blackwell").build()
    obs1 = ObservationBuilder().with_id("obs-01").with_subject("pat-01").with_loinc("15074-8", "Glucose").with_value(145.0, "mg/dL", "mg/dL").build()
    obs2 = ObservationBuilder().with_id("obs-02").with_subject("pat-01").with_loinc("2093-3", "Cholesterol").with_value(210.0, "mg/dL", "mg/dL").build()

    bundle = BundleBuilder().with_id(data["document_id"]).with_resource(pat).with_resource(obs1).with_resource(obs2).build()

    assert bundle["resourceType"] == "Bundle"
    assert len(bundle["entry"]) == 3

    # 3. Create real ValidationContext domain objects
    bbox = BoundingBox(0, 0, 1, 1)
    word = OcrWord("Glucose", bbox, 0.95)
    page = OcrPage(1, [word], "Glucose test report", [], {})
    ocr_res = OcrResult(data["document_id"], [page], "tesseract", 0.5)

    field_name = ExtractedField(value="Elizabeth Blackwell", evidence="Elizabeth", confidence=0.88)
    field_dob = ExtractedField(value="1988-05-12", evidence="dob", confidence=0.9)
    field_gender = ExtractedField(value="Female", evidence="gender", confidence=0.9)
    demographics = PatientDemographics(name=field_name, dob=field_dob, gender=field_gender, mrn=None)

    field_anal1 = ExtractedField(value="Glucose", evidence="glucose", confidence=0.95)
    field_val1 = ExtractedField(value="145.0", evidence="145", confidence=0.95)
    field_unit1 = ExtractedField(value="mg/dL", evidence="mg/dL", confidence=0.95)
    observation1 = ClinicalObservation(analyte_name=field_anal1, value=field_val1, unit=field_unit1, reference_range=None)

    field_type = ExtractedField(value="Lab Report", evidence="report", confidence=0.95)
    extracted_rep = StructuredClinicalReport(patient=demographics, observations=[observation1], document_type=field_type)

    ctx = ValidationContext(
        ocr_result=ocr_res,
        extracted_report=extracted_rep,
        fhir_bundle=bundle
    )

    engine = ValidationEngine()
    report = engine.validate(ctx)

    assert report["is_valid"] is True
    assert len(report["issues"]) == 0

    # 4. Dispatch using mock EHR exporter port
    mock_exporter = MagicMock()
    mock_exporter.export_bundle.return_value = {"status": "success", "id": data["document_id"]}

    dispatch_res = mock_exporter.export_bundle(bundle, "idempotency-key-099")
    assert dispatch_res["status"] == "success"
    mock_exporter.export_bundle.assert_called_once_with(bundle, "idempotency-key-099")
