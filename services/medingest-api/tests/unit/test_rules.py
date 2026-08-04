from datetime import date, timedelta

from src.application.services.validation_engine import ValidationEngine
from src.domain.extraction.schemas import (
    ClinicalObservation,
    ExtractedField,
    PatientDemographics,
    StructuredClinicalReport,
)
from src.domain.ocr.value_objects import BoundingBox, OcrPage, OcrResult, OcrWord
from src.domain.validation.rules import (
    AiConfidenceRule,
    DateConsistencyRule,
    DuplicateReportRule,
    FhirComplianceRule,
    ImpossibleValuesRule,
    MissingFieldsRule,
    OcrConfidenceRule,
    TerminologyMappingRule,
    ValidationContext,
    ValidationSeverity,
)

# --- Mock Helpers ---

def get_base_report() -> StructuredClinicalReport:
    return StructuredClinicalReport(
        patient=PatientDemographics(
            name=ExtractedField(value="John Doe", evidence="Name: John Doe", confidence=0.95),
            dob=ExtractedField(value="1990-01-01", evidence="DOB: 1990-01-01", confidence=0.95),
            gender=None,
            mrn=None
        ),
        observations=[
            ClinicalObservation(
                analyte_name=ExtractedField(value="Glucose", evidence="Glucose", confidence=0.95),
                value=ExtractedField(value="95", evidence="95 mg/dL", confidence=0.95),
                unit=ExtractedField(value="mg/dL", evidence="mg/dL", confidence=0.95),
                reference_range=None
            )
        ],
        document_type=ExtractedField(value="Lab Report", evidence="Report Type", confidence=0.95)
    )

# --- 1. OCR Confidence Rule Tests ---

def test_ocr_confidence_rule() -> None:
    bbox = BoundingBox(0.0, 0.0, 1.0, 1.0)
    word_low = OcrWord("low_conf", bbox, 0.50)  # below 0.70 threshold
    word_high = OcrWord("high_conf", bbox, 0.95)

    page = OcrPage(1, [word_low, word_high], "low_conf high_conf", [], {})
    ocr_res = OcrResult("doc-123", [page], "tesseract", 0.0)

    context = ValidationContext(ocr_result=ocr_res)
    rule = OcrConfidenceRule(threshold=0.70)

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "LOW_OCR_CONFIDENCE"
    assert issues[0].severity == ValidationSeverity.WARNING
    assert issues[0].value == "low_conf"


# --- 2. AI Confidence Rule Tests ---

def test_ai_confidence_rule() -> None:
    report = get_base_report()
    report.patient.name.confidence = 0.50  # below 0.80 threshold

    context = ValidationContext(extracted_report=report)
    rule = AiConfidenceRule(threshold=0.80)

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "LOW_AI_CONFIDENCE"
    assert issues[0].field == "patient.name"


# --- 3. Terminology Mapping Rule Tests ---

def test_terminology_mapping_rule() -> None:
    report = get_base_report()
    report.document_type.value = "73999-5"  # fallback LOINC

    context = ValidationContext(extracted_report=report)
    rule = TerminologyMappingRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "FALLBACK_TERMINOLOGY"


# --- 4. Missing Fields Rule Tests ---

def test_missing_fields_rule() -> None:
    report = get_base_report()
    report.patient.name.value = ""  # blank mandatory field

    context = ValidationContext(extracted_report=report)
    rule = MissingFieldsRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "MISSING_MANDATORY_FIELD"
    assert issues[0].severity == ValidationSeverity.ERROR


# --- 5. Impossible Values Rule Tests ---

def test_impossible_values_rule() -> None:
    report = get_base_report()
    report.observations[0].value.value = "-10"  # impossible Glucose

    context = ValidationContext(extracted_report=report)
    rule = ImpossibleValuesRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "IMPOSSIBLE_PHYSIOLOGICAL_VALUE"
    assert issues[0].severity == ValidationSeverity.ERROR


# --- 6. Duplicate Report Rule Tests ---

def test_duplicate_report_rule() -> None:
    report = get_base_report()
    existing = [get_base_report()]

    context = ValidationContext(extracted_report=report, existing_reports=existing)
    rule = DuplicateReportRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "DUPLICATE_REPORT"
    assert issues[0].severity == ValidationSeverity.WARNING


# --- 7. Date Consistency Rule Tests ---

def test_date_consistency_rule() -> None:
    report = get_base_report()
    # Patient DOB in the future
    future_date = (date.today() + timedelta(days=10)).isoformat()
    assert report.patient.dob is not None
    report.patient.dob.value = future_date

    context = ValidationContext(extracted_report=report)
    rule = DateConsistencyRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "FUTURE_DATE"
    assert issues[0].severity == ValidationSeverity.ERROR


# --- 8. FHIR Compliance Rule Tests ---

def test_fhir_compliance_rule() -> None:
    outcome = {
        "valid": False,
        "issues": [
            {
                "severity": "error",
                "details": {"text": "Missing patient identifier system"},
                "expression": ["Patient.identifier[0]"]
            }
        ]
    }

    context = ValidationContext(fhir_validation_outcome=outcome)
    rule = FhirComplianceRule()

    issues = rule.validate(context)
    assert len(issues) == 1
    assert issues[0].code == "FHIR_COMPLIANCE_ERROR"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].message == "Missing patient identifier system"


# --- 9. Validation Engine Test ---

def test_validation_engine_aggregation() -> None:
    # Set up context with a mix of warning (duplicate) and error (missing name) issues
    report = get_base_report()
    report.document_type.value = ""  # Error: Missing Document Type
    existing = [get_base_report()]  # Warning: Duplicate

    context = ValidationContext(extracted_report=report, existing_reports=existing)
    engine = ValidationEngine()

    report_dict = engine.validate(context)

    assert report_dict["is_valid"] is False  # Because of the error
    assert report_dict["summary"]["errors"] == 1
    assert report_dict["summary"]["warnings"] == 1
    assert len(report_dict["issues"]) == 2
