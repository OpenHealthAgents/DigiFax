"""
value_objects.py
Domain Value Objects representing FHIR Implementation Guides and validation outputs.
"""

from dataclasses import dataclass
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class FHIRImplementationGuide(ValueObject):
    """Represents a selectable FHIR Implementation Guide."""
    name: str
    url: str
    version: str
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Implementation Guide name cannot be empty")
        if not self.url.strip():
            raise ValueError("Implementation Guide URL cannot be empty")
        if not self.version.strip():
            raise ValueError("Implementation Guide version cannot be empty")


@dataclass(frozen=True)
class FHIRValidationResult(ValueObject):
    """Models structural validation outcomes of a FHIR resource."""
    valid: bool
    errors: list[str]
    profile_url: str | None = None
