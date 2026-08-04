import uuid
from typing import Any


class PatientBuilder:
    """Fluent builder for US Core Patient resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._identifier: list[dict[str, Any]] = []
        self._name: list[dict[str, Any]] = []
        self._gender: str | None = None
        self._birth_date: str | None = None

    def with_id(self, patient_id: str) -> "PatientBuilder":
        self._id = patient_id
        return self

    def with_mrn(self, mrn: str) -> "PatientBuilder":
        self._identifier.append({
            "system": "http://hl7.org/fhir/sid/us-medicaid",
            "value": mrn
        })
        return self

    def with_name(self, given: str, family: str) -> "PatientBuilder":
        self._name.append({
            "use": "official",
            "family": family,
            "given": [given]
        })
        return self

    def with_gender(self, gender: str) -> "PatientBuilder":
        self._gender = gender.lower()
        return self

    def with_birth_date(self, dob: str) -> "PatientBuilder":
        self._birth_date = dob
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Patient",
            "id": self._id,
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
            },
            "active": True
        }
        if self._identifier:
            resource["identifier"] = self._identifier
        if self._name:
            resource["name"] = self._name
        if self._gender:
            resource["gender"] = self._gender
        if self._birth_date:
            resource["birthDate"] = self._birth_date
        return resource


class PractitionerBuilder:
    """Fluent builder for US Core Practitioner resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._npi: str | None = None
        self._name: dict[str, Any] | None = None

    def with_id(self, practitioner_id: str) -> "PractitionerBuilder":
        self._id = practitioner_id
        return self

    def with_npi(self, npi: str) -> "PractitionerBuilder":
        self._npi = npi
        return self

    def with_name(self, given: str, family: str) -> "PractitionerBuilder":
        self._name = {
            "use": "official",
            "family": family,
            "given": [given]
        }
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Practitioner",
            "id": self._id,
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner"]
            }
        }
        if self._npi:
            resource["identifier"] = [{
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": self._npi
            }]
        if self._name:
            resource["name"] = [self._name]
        return resource


class OrganizationBuilder:
    """Fluent builder for US Core Organization resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._npi: str | None = None
        self._name: str | None = None

    def with_id(self, organization_id: str) -> "OrganizationBuilder":
        self._id = organization_id
        return self

    def with_npi(self, npi: str) -> "OrganizationBuilder":
        self._npi = npi
        return self

    def with_name(self, name: str) -> "OrganizationBuilder":
        self._name = name
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Organization",
            "id": self._id,
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"]
            },
            "active": True
        }
        if self._npi:
            resource["identifier"] = [{
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": self._npi
            }]
        if self._name:
            resource["name"] = self._name
        return resource


class SpecimenBuilder:
    """Fluent builder for core R4 Specimen resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._type_code: str | None = None
        self._type_display: str | None = None
        self._subject_id: str | None = None

    def with_id(self, specimen_id: str) -> "SpecimenBuilder":
        self._id = specimen_id
        return self

    def with_type(self, code: str, display: str) -> "SpecimenBuilder":
        self._type_code = code
        self._type_display = display
        return self

    def with_subject(self, patient_id: str) -> "SpecimenBuilder":
        self._subject_id = patient_id
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Specimen",
            "id": self._id
        }
        if self._type_code:
            resource["type"] = {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": self._type_code,
                    "display": self._type_display
                }]
            }
        if self._subject_id:
            resource["subject"] = {
                "reference": f"Patient/{self._subject_id}"
            }
        return resource


class ObservationBuilder:
    """Fluent builder for US Core Laboratory Observation resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._status = "final"
        self._code_loinc: str | None = None
        self._code_display: str | None = None
        self._subject_id: str | None = None
        self._value_num: float | None = None
        self._unit: str | None = None
        self._ucum_code: str | None = None
        self._specimen_id: str | None = None

    def with_id(self, observation_id: str) -> "ObservationBuilder":
        self._id = observation_id
        return self

    def with_status(self, status: str) -> "ObservationBuilder":
        self._status = status
        return self

    def with_loinc(self, code: str, display: str) -> "ObservationBuilder":
        self._code_loinc = code
        self._code_display = display
        return self

    def with_subject(self, patient_id: str) -> "ObservationBuilder":
        self._subject_id = patient_id
        return self

    def with_value(self, value: float, unit: str, ucum_code: str) -> "ObservationBuilder":
        self._value_num = value
        self._unit = unit
        self._ucum_code = ucum_code
        return self

    def with_specimen(self, specimen_id: str) -> "ObservationBuilder":
        self._specimen_id = specimen_id
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Observation",
            "id": self._id,
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"]
            },
            "status": self._status,
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }]
        }
        if self._code_loinc:
            resource["code"] = {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": self._code_loinc,
                    "display": self._code_display
                }]
            }
        if self._subject_id:
            resource["subject"] = {
                "reference": f"Patient/{self._subject_id}"
            }
        if self._value_num is not None:
            resource["valueQuantity"] = {
                "value": self._value_num,
                "unit": self._unit,
                "system": "http://unitsofmeasure.org",
                "code": self._ucum_code
            }
        if self._specimen_id:
            resource["specimen"] = {
                "reference": f"Specimen/{self._specimen_id}"
            }
        return resource


class DiagnosticReportBuilder:
    """Fluent builder for US Core Laboratory DiagnosticReport resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._status = "final"
        self._code_loinc: str | None = None
        self._code_display: str | None = None
        self._subject_id: str | None = None
        self._performer_id: str | None = None
        self._specimen_ids: list[str] = []
        self._result_ids: list[str] = []

    def with_id(self, report_id: str) -> "DiagnosticReportBuilder":
        self._id = report_id
        return self

    def with_status(self, status: str) -> "DiagnosticReportBuilder":
        self._status = status
        return self

    def with_loinc(self, code: str, display: str) -> "DiagnosticReportBuilder":
        self._code_loinc = code
        self._code_display = display
        return self

    def with_subject(self, patient_id: str) -> "DiagnosticReportBuilder":
        self._subject_id = patient_id
        return self

    def with_performer(self, organization_id: str) -> "DiagnosticReportBuilder":
        self._performer_id = organization_id
        return self

    def with_specimen(self, specimen_id: str) -> "DiagnosticReportBuilder":
        self._specimen_ids.append(specimen_id)
        return self

    def with_observation(self, observation_id: str) -> "DiagnosticReportBuilder":
        self._result_ids.append(observation_id)
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": self._id,
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab"]
            },
            "status": self._status,
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                    "code": "LAB",
                    "display": "Laboratory"
                }]
            }]
        }
        if self._code_loinc:
            resource["code"] = {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": self._code_loinc,
                    "display": self._code_display
                }]
            }
        if self._subject_id:
            resource["subject"] = {
                "reference": f"Patient/{self._subject_id}"
            }
        if self._performer_id:
            resource["performer"] = [{
                "reference": f"Organization/{self._performer_id}"
            }]
        if self._specimen_ids:
            resource["specimen"] = [
                {"reference": f"Specimen/{sid}"} for sid in self._specimen_ids
            ]
        if self._result_ids:
            resource["result"] = [
                {"reference": f"Observation/{oid}"} for oid in self._result_ids
            ]
        return resource


class BundleBuilder:
    """Fluent builder for FHIR R4 Bundle transaction resources."""

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._type = "transaction"
        self._entries: list[dict[str, Any]] = []

    def with_id(self, bundle_id: str) -> "BundleBuilder":
        self._id = bundle_id
        return self

    def with_type(self, bundle_type: str) -> "BundleBuilder":
        self._type = bundle_type
        return self

    def with_resource(self, resource: dict[str, Any]) -> "BundleBuilder":
        # Add to entries with matching transaction request details
        res_type = resource["resourceType"]
        res_id = resource["id"]

        entry = {
            "fullUrl": f"urn:uuid:{res_id}" if not res_id else f"{res_type}/{res_id}",
            "resource": resource
        }

        if self._type == "transaction":
            entry["request"] = {
                "method": "POST" if not res_id else "PUT",
                "url": res_type if not res_id else f"{res_type}/{res_id}"
            }

        self._entries.append(entry)
        return self

    def build(self) -> dict[str, Any]:
        resource: dict[str, Any] = {
            "resourceType": "Bundle",
            "id": self._id,
            "type": self._type
        }
        if self._entries:
            resource["entry"] = self._entries
        return resource
