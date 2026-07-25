import logging
from typing import Any, cast

import requests

from src.application.ports.iehr_exporter import IEhrExporter

logger = logging.getLogger(__name__)

class AthenaExporter(IEhrExporter):
    """Concrete adapter connecting to athenahealth clinical REST APIs."""

    def __init__(self, auth_url: str, api_url: str, key: str, secret: str):
        self.auth_url = auth_url
        self.api_url = api_url
        self.key = key
        self.secret = secret
        self._processed_keys: set[str] = set()

    def _get_access_token(self) -> str:
        logger.info("Requesting access token from athenahealth...")
        # Athena OAuth uses basic authentication (key:secret) to request a token
        res = requests.post(
            self.auth_url,
            auth=(self.key, self.secret),
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        res.raise_for_status()
        return str(res.json()["access_token"])

    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        if idempotency_key in self._processed_keys:
            logger.info(f"Duplicate export bypassed for athenahealth. Key: {idempotency_key}")
            return {"document_id": bundle.get("id"), "status": "duplicate_bypassed"}

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": idempotency_key
            }

            logger.info("Exporting clinical data to athenahealth...")
            # Athena REST API uses clinical endpoints (e.g. POST /patients/{id}/clinicalnotes)
            res = requests.post(self.api_url, json=bundle, headers=headers, timeout=15)

            if res.status_code in (200, 201):
                self._processed_keys.add(idempotency_key)
                return cast(dict[str, Any], res.json())

            return {"status": "failed", "http_status": res.status_code, "body": res.text}
        except Exception as e:
            logger.error(f"Failed to export to athenahealth: {str(e)}")
            return {"status": "error", "message": str(e)}
