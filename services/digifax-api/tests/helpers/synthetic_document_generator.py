import uuid
from typing import Any


def generate_synthetic_ocr_text(patient_name: str, glucose_val: float) -> str:
    """Generates synthetic medical report raw text mimicking OCR outputs."""
    return f"""
    CLINICAL PATHOLOGY LABORATORY REPORT
    ------------------------------------
    Patient Name: {patient_name}
    Accession ID: {uuid.uuid4().hex[:8].upper()}
    Report Date: 2026-07-26

    TEST NAME          RESULT       UNIT       NORMAL RANGE
    Fasting Glucose    {glucose_val}        mg/dL      70 - 100
    ------------------------------------
    """

def generate_synthetic_extraction_data(patient_name: str, glucose_val: float, cholesterol_val: float) -> dict[str, Any]:
    """Generates structured clinical report dictionary payload matching AI extractor format."""
    return {
        "document_id": f"doc-{uuid.uuid4().hex[:8]}",
        "patient": {
            "name": patient_name,
            "dob": "1988-05-12",
            "gender": "Female"
        },
        "observations": [
            {
                "analyte_name": "Glucose",
                "value": str(glucose_val),
                "unit": "mg/dL"
            },
            {
                "analyte_name": "Cholesterol",
                "value": str(cholesterol_val),
                "unit": "mg/dL"
            }
        ]
    }
