import logging
from typing import Any, cast

import requests

from src.application.ports.iehr_exporter import IEhrExporter

logger = logging.getLogger(__name__)

class MedplumExporter(IEhrExporter):
    """Concrete adapter connecting to Medplum FHIR platform using OAuth 2.0 auth flows."""

    def __init__(self, auth_url: str, fhir_url: str, client_id: str, client_secret: str):
        self.auth_url = auth_url
        self.fhir_url = fhir_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._processed_keys: set[str] = set()

    def _get_access_token(self) -> str:
        logger.info("Requesting OAuth token from Medplum...")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = requests.post(self.auth_url, data=data, timeout=10)
        res.raise_for_status()
        return str(res.json()["access_token"])

    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        if idempotency_key in self._processed_keys:
            logger.info(f"Duplicate export bypassed for Medplum. Key: {idempotency_key}")
            return {"document_id": bundle.get("id"), "status": "duplicate_bypassed"}

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/fhir+json",
                "X-Idempotency-Key": idempotency_key
            }

            logger.info("Posting transaction bundle to Medplum...")
            res = requests.post(self.fhir_url, json=bundle, headers=headers, timeout=15)

            if res.status_code in (200, 201):
                self._processed_keys.add(idempotency_key)
                return cast(dict[str, Any], res.json())

            return {"status": "failed", "http_status": res.status_code, "body": res.text}
        except Exception as e:
            logger.error(f"Failed to export to Medplum: {str(e)}")
            return {"status": "error", "message": str(e)}
