
from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    """Encapsulates a clinical property, its matching source evidence, and confidence."""

    value: str = Field(description="The extracted value of the field.")
    evidence: str = Field(description="The exact text substring or phrase from the document serving as evidence.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")


class PatientDemographics(BaseModel):
    """Patient demographics details extracted from the clinical report."""

    name: ExtractedField = Field(description="Patient's full name.")
    dob: ExtractedField | None = Field(None, description="Patient's Date of Birth.")
    gender: ExtractedField | None = Field(None, description="Patient's biological gender.")
    mrn: ExtractedField | None = Field(None, description="Medical Record Number (MRN).")


class ClinicalObservation(BaseModel):
    """Single clinical observation / test result item."""

    analyte_name: ExtractedField = Field(description="Name of the test or analyte.")
    value: ExtractedField = Field(description="Numerical or textual result value.")
    unit: ExtractedField | None = Field(None, description="Measurement unit (e.g. mg/dL, mmol/L).")
    reference_range: ExtractedField | None = Field(None, description="Normal reference range intervals (e.g. 70-100).")


class StructuredClinicalReport(BaseModel):
    """The root schema aggregating patient info, observations, and type classification."""

    patient: PatientDemographics = Field(description="Patient demographic details.")
    observations: list[ClinicalObservation] = Field(description="List of clinical observations/test results.")
    document_type: ExtractedField = Field(description="Classified document type (e.g. Lab Report, Referral).")
