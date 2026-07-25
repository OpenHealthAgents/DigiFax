import logging
from typing import Any, cast

import requests

from src.application.ports.iehr_exporter import IEhrExporter

logger = logging.getLogger(__name__)

class CernerExporter(IEhrExporter):
    """Concrete adapter connecting to Oracle Health (Cerner) Millenium FHIR services."""

    def __init__(self, fhir_url: str, auth_header: str):
        self.fhir_url = fhir_url
        self.auth_header = auth_header
        self._processed_keys: set[str] = set()

    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        if idempotency_key in self._processed_keys:
            logger.info(f"Duplicate export bypassed for Cerner. Key: {idempotency_key}")
            return {"document_id": bundle.get("id"), "status": "duplicate_bypassed"}

        try:
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/fhir+json",
                "X-Idempotency-Key": idempotency_key
            }

            logger.info(f"Posting clinical bundle to Oracle Health (Cerner): {self.fhir_url}")
            res = requests.post(self.fhir_url, json=bundle, headers=headers, timeout=15)

            if res.status_code in (200, 201):
                self._processed_keys.add(idempotency_key)
                return cast(dict[str, Any], res.json())

            return {"status": "failed", "http_status": res.status_code, "body": res.text}
        except Exception as e:
            logger.error(f"Failed to export to Cerner: {str(e)}")
            return {"status": "error", "message": str(e)}
