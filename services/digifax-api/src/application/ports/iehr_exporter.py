import abc
from typing import Any


class IEhrExporter(abc.ABC):
    """Abstract outbound port representing EHR/FHIR target dispatchers."""

    @abc.abstractmethod
    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        """Dispatches a completed transaction bundle payload to target EHR systems.

        Args:
            bundle: The FHIR R4 Bundle JSON payload
            idempotency_key: A unique UUID to ensure once-only delivery semantics
        """
        pass
