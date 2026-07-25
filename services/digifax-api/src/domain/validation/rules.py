import abc
from datetime import date
from enum import StrEnum
from typing import Any

from src.domain.common.value_object import ValueObject
from src.domain.extraction.layout import NormalizedLayoutDocument
from src.domain.extraction.schemas import StructuredClinicalReport
from src.domain.ocr.value_objects import OcrResult


class ValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(ValueObject):
    """Details a validation issue, its severity, and targets."""

    def __init__(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity,
        field: str | None = None,
        value: str | None = None
    ):
        self.code = code
        self.message = message
        self.severity = severity
        self.field = field
        self.value = value


class ValidationContext(ValueObject):
    """Aggregates all components required to run validation rules."""

    def __init__(
        self,
        ocr_result: OcrResult | None = None,
        layout_document: NormalizedLayoutDocument | None = None,
        extracted_report: StructuredClinicalReport | None = None,
        fhir_bundle: dict[str, Any] | None = None,
        fhir_validation_outcome: dict[str, Any] | None = None,
        existing_reports: list[StructuredClinicalReport] | None = None
    ):
        self.ocr_result = ocr_result
        self.layout_document = layout_document
        self.extracted_report = extracted_report
        self.fhir_bundle = fhir_bundle
        self.fhir_validation_outcome = fhir_validation_outcome
        self.existing_reports = existing_reports or []


class IValidationRule(abc.ABC):
    """Abstract interface defining the rule execution contract."""

    @abc.abstractmethod
    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        """Runs the validation checks and returns issues if found."""
        pass


# --- 1. OCR Confidence Rule ---

class OcrConfidenceRule(IValidationRule):
    """Checks for low confidence scores in OCR text extraction.

    This rule inspects each individual word returned by the OCR engine. If any
    word falls below the threshold (default: 70%), we flag it as a warning, which
    alerts clinical reviewers to double-check spelling, names, or values in that area.
    """

    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not context.ocr_result:
            return issues

        # Loop through pages and words to check OCR engine confidence ratings
        for page in context.ocr_result.pages:
            for word in page.words:
                if word.confidence < self.threshold:
                    issues.append(
                        ValidationIssue(
                            code="LOW_OCR_CONFIDENCE",
                            message=f"OCR word '{word.text}' confidence {word.confidence:.2f} is below threshold {self.threshold:.2f}.",
                            severity=ValidationSeverity.WARNING,
                            field=f"page_{page.page_number}.word",
                            value=word.text
                        )
                    )
        return issues


# --- 2. AI Confidence Rule ---

class AiConfidenceRule(IValidationRule):
    """Checks for low confidence scores in AI extracted variables.

    Inspects structured fields (demographics, observations) extracted by LLMs/AI.
    If the AI model's confidence rating falls below the threshold (default: 80%),
    we trigger a warning.
    """

    def __init__(self, threshold: float = 0.80):
        self.threshold = threshold

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        report = context.extracted_report
        if not report:
            return issues

        # Check demographics name field confidence
        p = report.patient
        if p.name.confidence < self.threshold:
            issues.append(
                ValidationIssue(
                    code="LOW_AI_CONFIDENCE",
                    message=f"Patient name confidence {p.name.confidence:.2f} below threshold {self.threshold:.2f}.",
                    severity=ValidationSeverity.WARNING,
                    field="patient.name",
                    value=p.name.value
                )
            )
        if p.dob and p.dob.confidence < self.threshold:
            issues.append(
                ValidationIssue(
                    code="LOW_AI_CONFIDENCE",
                    message=f"Patient DOB confidence {p.dob.confidence:.2f} below threshold {self.threshold:.2f}.",
                    severity=ValidationSeverity.WARNING,
                    field="patient.dob",
                    value=p.dob.value
                )
            )

        # Check observations
        for idx, obs in enumerate(report.observations):
            if obs.value.confidence < self.threshold:
                issues.append(
                    ValidationIssue(
                        code="LOW_AI_CONFIDENCE",
                        message=f"Observation value confidence {obs.value.confidence:.2f} below threshold {self.threshold:.2f}.",
                        severity=ValidationSeverity.WARNING,
                        field=f"observations[{idx}].value",
                        value=obs.value.value
                    )
                )
        return issues


# --- 3. Terminology Mapping Rule ---

class TerminologyMappingRule(IValidationRule):
    """Flags missing or default fallback LOINC coding mappings."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        # Checks can analyze mappings added to observations (e.g. from terminology adapter outcomes)
        # For simplicity, if report document type resolved to default fallback LOINC "73999-5":
        report = context.extracted_report
        if not report:
            return issues

        if report.document_type.value == "73999-5" or "73999-5" in report.document_type.evidence:
            issues.append(
                ValidationIssue(
                    code="FALLBACK_TERMINOLOGY",
                    message="Document type was resolved to default fallback LOINC code 73999-5.",
                    severity=ValidationSeverity.WARNING,
                    field="document_type",
                    value="73999-5"
                )
            )
        return issues


# --- 4. Missing Fields Rule ---

class MissingFieldsRule(IValidationRule):
    """Ensures mandatory fields (e.g., patient name, document type) are populated."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        report = context.extracted_report
        if not report:
            return issues

        if not report.patient.name.value.strip():
            issues.append(
                ValidationIssue(
                    code="MISSING_MANDATORY_FIELD",
                    message="Patient name is missing or blank.",
                    severity=ValidationSeverity.ERROR,
                    field="patient.name"
                )
            )
        if not report.document_type.value.strip():
            issues.append(
                ValidationIssue(
                    code="MISSING_MANDATORY_FIELD",
                    message="Document type classification is missing or blank.",
                    severity=ValidationSeverity.ERROR,
                    field="document_type"
                )
            )
        return issues


# --- 5. Impossible Values Rule ---

class ImpossibleValuesRule(IValidationRule):
    """Checks extracted observations against physiological bounds."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        report = context.extracted_report
        if not report:
            return issues

        for idx, obs in enumerate(report.observations):
            name = obs.analyte_name.value.lower()
            val_str = obs.value.value

            # Check glucose physiological ranges
            if "glucose" in name:
                try:
                    val = float(val_str)
                    if val <= 0 or val > 1000:
                        issues.append(
                            ValidationIssue(
                                code="IMPOSSIBLE_PHYSIOLOGICAL_VALUE",
                                message=f"Glucose value {val:.1f} mg/dL is physiologically impossible or life-threatening.",
                                severity=ValidationSeverity.ERROR,
                                field=f"observations[{idx}].value",
                                value=val_str
                            )
                        )
                except ValueError:
                    pass
        return issues


# --- 6. Duplicate Report Rule ---

class DuplicateReportRule(IValidationRule):
    """Flags potential duplicate reports based on matching patient details and observations."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        report = context.extracted_report
        if not report or not context.existing_reports:
            return issues

        pat_name = report.patient.name.value.strip().lower()

        for ext in context.existing_reports:
            ext_name = ext.patient.name.value.strip().lower()
            if pat_name == ext_name:
                # Compare observation values to confirm duplicate
                matching_obs = 0
                for obs in report.observations:
                    for e_obs in ext.observations:
                        if (obs.analyte_name.value.lower() == e_obs.analyte_name.value.lower()
                                and obs.value.value == e_obs.value.value):
                            matching_obs += 1

                if matching_obs > 0 and matching_obs == len(report.observations):
                    issues.append(
                        ValidationIssue(
                            code="DUPLICATE_REPORT",
                            message=f"Duplicate clinical report identified for patient '{report.patient.name.value}'.",
                            severity=ValidationSeverity.WARNING,
                            field="patient.name",
                            value=report.patient.name.value
                        )
                    )
                    break
        return issues


# --- 7. Date Consistency Rule ---

class DateConsistencyRule(IValidationRule):
    """Verifies that patient and report dates are consistent and logical."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        report = context.extracted_report
        if not report:
            return issues

        today = date.today()
        p = report.patient
        if p.dob and p.dob.value:
            try:
                dob = date.fromisoformat(p.dob.value)
                if dob > today:
                    issues.append(
                        ValidationIssue(
                            code="FUTURE_DATE",
                            message=f"Patient Date of Birth '{p.dob.value}' is in the future.",
                            severity=ValidationSeverity.ERROR,
                            field="patient.dob",
                            value=p.dob.value
                        )
                    )
            except ValueError:
                pass
        return issues


# --- 8. FHIR Compliance Rule ---

class FhirComplianceRule(IValidationRule):
    """Maps remote HAPI FHIR validations directly to standard validation issues."""

    def validate(self, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        outcome = context.fhir_validation_outcome
        if not outcome or outcome.get("valid") is True:
            return issues

        # Parse outcome issues
        raw_issues = outcome.get("issues", [])
        for raw in raw_issues:
            severity_str = raw.get("severity", "error")
            severity = ValidationSeverity.ERROR if severity_str in ("error", "fatal") else ValidationSeverity.WARNING

            issues.append(
                ValidationIssue(
                    code="FHIR_COMPLIANCE_ERROR",
                    message=raw.get("details", {}).get("text", "FHIR validation warning"),
                    severity=severity,
                    field=raw.get("expression", [None])[0]
                )
            )
        return issues
