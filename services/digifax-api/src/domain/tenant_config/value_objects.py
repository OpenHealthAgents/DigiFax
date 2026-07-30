"""
value_objects.py
Domain Value Objects representing Tenant settings and formatting constraints.
"""

from dataclasses import dataclass
from typing import Any
import re
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class LocaleSettings(ValueObject):
    """Immutable locale formatting rules."""
    date_format: str
    time_format: str
    timezone: str
    language: str
    currency: str
    locale: str
    number_format: str

    def __post_init__(self) -> None:
        # Simple syntax format assertions
        if not self.date_format.strip():
            raise ValueError("Date format cannot be empty")
        if not self.time_format.strip():
            raise ValueError("Time format cannot be empty")
        if not self.timezone.strip():
            raise ValueError("Timezone cannot be empty")
        if not self.locale.strip() or "_" not in self.locale and "-" not in self.locale:
            raise ValueError("Locale must be valid language tag (e.g. en_US)")


@dataclass(frozen=True)
class ClinicalFormats(ValueObject):
    """Immutable regex layout schemas mapping patient ids, MRNs, and document numbers."""
    patient_id_format: str
    medical_record_format: str
    document_number_format: str

    def __post_init__(self) -> None:
        # Validate that compile formats are legal regex
        try:
            re.compile(self.patient_id_format)
            re.compile(self.medical_record_format)
            re.compile(self.document_number_format)
        except re.error as e:
            raise ValueError(f"Invalid regex schema configuration: {str(e)}")


@dataclass(frozen=True)
class RetentionSettings(ValueObject):
    """Immutable documents lifecycle parameters."""
    default_retention_days: int

    def __post_init__(self) -> None:
        if self.default_retention_days < 1:
            raise ValueError("Retention duration must be at least 1 day")
