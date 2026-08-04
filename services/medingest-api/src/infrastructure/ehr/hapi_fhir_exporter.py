import logging
from typing import Any, cast

import requests

from src.application.ports.iehr_exporter import IEhrExporter

logger = logging.getLogger(__name__)

class HapiFhirExporter(IEhrExporter):
    """Concrete adapter exporting FHIR resources to a standard HAPI FHIR server."""

    def __init__(self, base_url: str = "http://localhost:8080/fhir"):
        self.base_url = base_url
        self._processed_keys: set[str] = set()

    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        # Idempotency check
        if idempotency_key in self._processed_keys:
            logger.info(f"Duplicate export bypassed for HAPI FHIR. Key: {idempotency_key}")
            return {"document_id": bundle.get("id"), "status": "duplicate_bypassed"}

        logger.info(f"Exporting bundle to HAPI FHIR: {self.base_url}")

        # Exponential backoff retry loop
        max_attempts = 3
        backoff_sec = 1.0
        response = None

        headers = {
            "Content-Type": "application/fhir+json",
            "X-Idempotency-Key": idempotency_key
        }

        for attempt in range(max_attempts):
            try:
                response = requests.post(self.base_url, json=bundle, headers=headers, timeout=10)
                if response.status_code in (200, 201):
                    logger.info("Successfully exported to HAPI FHIR.")
                    self._processed_keys.add(idempotency_key)
                    return cast(dict[str, Any], response.json())

                # Retry on 5xx server issues
                if response.status_code < 500:
                    break
            except requests.RequestException as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")

            import time
            time.sleep(backoff_sec)
            backoff_sec *= 2.0

        # Return error report if failed
        status_code = response.status_code if response else 0
        return {"status": "failed", "http_status": status_code}
