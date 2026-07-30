"""
domain_services.py
Domain Service for validating clinical numbering and identifiers.
"""

import re
from src.domain.tenant_config.value_objects import ClinicalFormats


class ClinicalNumberingService:
    """
    Domain Service validating identifiers against tenant-configured regex structures.
    """

    @staticmethod
    def validate_patient_id(patient_id: str, formats: ClinicalFormats) -> bool:
        """Validates patient ID matches layout template regex."""
        pattern = re.compile(formats.patient_id_format)
        return bool(pattern.match(patient_id))

    @staticmethod
    def validate_mrn(mrn: str, formats: ClinicalFormats) -> bool:
        """Validates MRN matches layout template regex."""
        pattern = re.compile(formats.medical_record_format)
        return bool(pattern.match(mrn))

    @staticmethod
    def validate_document_number(doc_num: str, formats: ClinicalFormats) -> bool:
        """Validates document number matches layout template regex."""
        pattern = re.compile(formats.document_number_format)
        return bool(pattern.match(doc_num))
