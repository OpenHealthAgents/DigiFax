import abc
from typing import Any


class IFhirValidator(abc.ABC):
    """Outbound port interface defining FHIR R4 and US Core validation services."""

    @abc.abstractmethod
    def validate_resource(self, resource_json: dict[str, Any]) -> dict[str, Any]:
        """Validates a FHIR resource or Bundle against standard schemas and profiles.

        Args:
            resource_json: The dictionary representing the FHIR resource to validate.

        Returns:
            A validation outcome report dictionary with keys:
            - 'valid': bool indicating compliance.
            - 'issues': List[dict] listing any warning/error details.
        """
        pass
