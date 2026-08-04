import logging
from typing import Any

import requests

from src.application.ports.ifhir_validator import IFhirValidator

logger = logging.getLogger(__name__)

class HapiFhirValidator(IFhirValidator):
    """Validator adapter calling HAPI FHIR server or falling back to local structural checks."""

    def __init__(self, validator_url: str | None = None):
        # Default to public HL7 validator or local service
        self.validator_url = validator_url or "https://validator.fhir.org/validate"

    def validate_resource(self, resource_json: dict[str, Any]) -> dict[str, Any]:
        try:
            logger.info(f"FHIR Validation: Sending resource to HAPI FHIR Validator at {self.validator_url}")
            response = requests.post(
                url=self.validator_url,
                json=resource_json,
                headers={"Content-Type": "application/fhir+json"},
                timeout=5.0
            )

            if response.status_code == 200:
                outcome = response.json()
                issues = outcome.get("issue", [])

                # Check for errors in OperationOutcome
                errors = [iss for iss in issues if iss.get("severity") in ("error", "fatal")]
                if errors:
                    return {
                        "valid": False,
                        "issues": issues
                    }
                return {
                    "valid": True,
                    "issues": issues
                }

        except Exception as e:
            logger.warning(
                f"HAPI FHIR Validation connection failed: {str(e)}. "
                "Executing local US Core structural validations instead."
            )

        # Local Fallback validation check
        return self._local_structural_validation(resource_json)

    def _local_structural_validation(self, resource: dict[str, Any]) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        res_type = resource.get("resourceType")

        if not res_type:
            issues.append({
                "severity": "error",
                "details": "Missing mandatory 'resourceType' attribute."
            })
            return {"valid": False, "issues": issues}

        # Validate resource specifics
        if res_type == "Patient":
            self._validate_patient(resource, issues)
        elif res_type == "Observation":
            self._validate_observation(resource, issues)
        elif res_type == "DiagnosticReport":
            self._validate_diagnostic_report(resource, issues)
        elif res_type == "Bundle":
            self._validate_bundle(resource, issues)

        errors = [iss for iss in issues if iss.get("severity") == "error"]
        return {
            "valid": len(errors) == 0,
            "issues": issues if issues else [{"severity": "information", "details": "Local validation passed."}]
        }

    def _validate_patient(self, resource: dict[str, Any], issues: list[dict[str, Any]]) -> None:
        profile = resource.get("meta", {}).get("profile", [])
        if "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient" not in profile:
            issues.append({
                "severity": "error",
                "details": "US Core Patient resource must state profile meta."
            })
        if not resource.get("name"):
            issues.append({
                "severity": "error",
                "details": "US Core Patient requires family name and given names."
            })

    def _validate_observation(self, resource: dict[str, Any], issues: list[dict[str, Any]]) -> None:
        profile = resource.get("meta", {}).get("profile", [])
        if "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab" not in profile:
            issues.append({
                "severity": "error",
                "details": "US Core Lab Observation resource must state profile meta."
            })
        if not resource.get("status"):
            issues.append({
                "severity": "error",
                "details": "Observation missing mandatory 'status' attribute."
            })
        if not resource.get("code"):
            issues.append({
                "severity": "error",
                "details": "Observation missing LOINC code."
            })

    def _validate_diagnostic_report(self, resource: dict[str, Any], issues: list[dict[str, Any]]) -> None:
        profile = resource.get("meta", {}).get("profile", [])
        if "http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab" not in profile:
            issues.append({
                "severity": "error",
                "details": "US Core DiagnosticReport resource must state profile meta."
            })
        if not resource.get("status"):
            issues.append({
                "severity": "error",
                "details": "DiagnosticReport missing mandatory 'status' attribute."
            })

    def _validate_bundle(self, resource: dict[str, Any], issues: list[dict[str, Any]]) -> None:
        if not resource.get("type"):
            issues.append({
                "severity": "error",
                "details": "Bundle resource missing mandatory 'type' attribute."
            })
        for entry in resource.get("entry", []):
            entry_res = entry.get("resource")
            if entry_res:
                nested = self._local_structural_validation(entry_res)
                if not nested["valid"]:
                    issues.extend(nested["issues"])
