from typing import Any

from src.domain.validation.rules import (
    AiConfidenceRule,
    DateConsistencyRule,
    DuplicateReportRule,
    FhirComplianceRule,
    ImpossibleValuesRule,
    IValidationRule,
    MissingFieldsRule,
    OcrConfidenceRule,
    TerminologyMappingRule,
    ValidationContext,
    ValidationIssue,
    ValidationSeverity,
)


class ValidationEngine:
    """Orchestrates custom clinical validation checks and registers rules."""

    def __init__(self, rules: list[IValidationRule] | None = None):
        if rules is not None:
            self.rules = rules
        else:
            # Register the 8 standard validation rules by default
            self.rules = [
                OcrConfidenceRule(),
                AiConfidenceRule(),
                TerminologyMappingRule(),
                MissingFieldsRule(),
                ImpossibleValuesRule(),
                DuplicateReportRule(),
                DateConsistencyRule(),
                FhirComplianceRule()
            ]

    def validate(self, context: ValidationContext) -> dict[str, Any]:
        """Runs all registered rules against the context and summarizes issues."""
        all_issues: list[ValidationIssue] = []
        for rule in self.rules:
            issues = rule.validate(context)
            all_issues.extend(issues)

        errors = [iss for iss in all_issues if iss.severity == ValidationSeverity.ERROR]
        warnings = [iss for iss in all_issues if iss.severity == ValidationSeverity.WARNING]
        infos = [iss for iss in all_issues if iss.severity == ValidationSeverity.INFO]

        # Payload is invalid if any rule returns an ERROR
        is_valid = len(errors) == 0

        # Serialize issues to dicts for simple structured transmission
        serialized_issues = [
            {
                "code": iss.code,
                "message": iss.message,
                "severity": iss.severity.value,
                "field": iss.field,
                "value": iss.value
            }
            for iss in all_issues
        ]

        return {
            "is_valid": is_valid,
            "issues": serialized_issues,
            "summary": {
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(infos)
            }
        }
