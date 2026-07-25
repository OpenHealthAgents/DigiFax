import logging
import time
import typing
import uuid
from typing import Any, cast

import requests

from src.application.ports.iehr_exporter import IEhrExporter

if typing.TYPE_CHECKING:
    jwt: Any
    HAS_JWT: bool
else:
    try:
        import jwt
        HAS_JWT = True
    except ImportError:
        jwt = object
        HAS_JWT = False

logger = logging.getLogger(__name__)

class EpicExporter(IEhrExporter):
    """Concrete adapter connecting to Epic systems using JWT Client Assertion OAuth flows."""

    def __init__(self, token_url: str, fhir_url: str, client_id: str, private_key_pem: str | None = None):
        self.token_url = token_url
        self.fhir_url = fhir_url
        self.client_id = client_id
        self.private_key_pem = private_key_pem
        self._processed_keys: set[str] = set()

    def _generate_jwt_assertion(self) -> str:
        payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.token_url,
            "jti": str(uuid.uuid4()),
            "exp": int(time.time()) + 300
        }

        if HAS_JWT and self.private_key_pem:
            try:
                return cast(str, jwt.encode(payload, self.private_key_pem, algorithm="RS384"))
            except Exception as e:
                logger.warning(f"Failed to sign JWT with private key: {str(e)}")

        # Fallback dummy assertion string during mocks/offline
        return "epic-assertion-dummy-jwt"

    def _get_access_token(self) -> str:
        assertion = self._generate_jwt_assertion()
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion
        }

        logger.info("Requesting Epic access token using signed JWT assertion...")
        res = requests.post(self.token_url, data=data, timeout=10)
        res.raise_for_status()
        return str(res.json()["access_token"])

    def export_bundle(self, bundle: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        if idempotency_key in self._processed_keys:
            logger.info(f"Duplicate export bypassed for Epic. Key: {idempotency_key}")
            return {"document_id": bundle.get("id"), "status": "duplicate_bypassed"}

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/fhir+json",
                "X-Idempotency-Key": idempotency_key
            }

            logger.info(f"Posting clinical bundle to Epic endpoint: {self.fhir_url}")
            res = requests.post(self.fhir_url, json=bundle, headers=headers, timeout=15)

            if res.status_code in (200, 201):
                self._processed_keys.add(idempotency_key)
                return cast(dict[str, Any], res.json())

            return {"status": "failed", "http_status": res.status_code, "body": res.text}
        except Exception as e:
            logger.error(f"Failed to export to Epic: {str(e)}")
            return {"status": "error", "message": str(e)}
