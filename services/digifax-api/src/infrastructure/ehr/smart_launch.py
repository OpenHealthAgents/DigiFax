import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

class SmartLaunchManager:
    """Manages SMART on FHIR authorization flows and launch context discovery."""

    def discover_endpoints(self, iss_url: str) -> dict[str, str]:
        """Queries the SMART configuration or conformance metadata of the EHR server."""
        well_known_url = f"{iss_url.rstrip('/')}/.well-known/smart-configuration"
        logger.info(f"Discovering SMART configuration: {well_known_url}")

        try:
            res = requests.get(well_known_url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return {
                    "authorization_endpoint": data["authorization_endpoint"],
                    "token_endpoint": data["token_endpoint"]
                }
        except Exception as e:
            logger.warning(f"Failed to query .well-known smart configuration: {str(e)}. Falling back to CapabilityStatement...")

        # Fallback to CapabilityStatement discovery
        metadata_url = f"{iss_url.rstrip('/')}/metadata"
        res = requests.get(metadata_url, headers={"Accept": "application/fhir+json"}, timeout=10)
        res.raise_for_status()

        # Parse endpoints from rest.security.extension
        statement = res.json()
        auth_url = ""
        token_url = ""

        for rest in statement.get("rest", []):
            security = rest.get("security", {})
            for ext in security.get("extension", []):
                if ext.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                    for sub_ext in ext.get("extension", []):
                        if sub_ext.get("url") == "authorize":
                            auth_url = str(sub_ext.get("valueUri", ""))
                        elif sub_ext.get("url") == "token":
                            token_url = str(sub_ext.get("valueUri", ""))

        if not auth_url or not token_url:
            raise ValueError("Failed to discover SMART OAuth endpoints from server metadata.")

        return {
            "authorization_endpoint": auth_url,
            "token_endpoint": token_url
        }

    def exchange_authorization_code(
        self,
        token_url: str,
        code: str,
        redirect_uri: str,
        client_id: str,
        client_secret: str | None = None
    ) -> dict[str, Any]:
        """Exchanges redirect authorization code for access token and launch context details."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id
        }

        if client_secret:
            data["client_secret"] = client_secret

        logger.info(f"Exchanging auth code at: {token_url}")
        res = requests.post(token_url, data=data, timeout=10)
        res.raise_for_status()

        token_data = res.json()
        return {
            "access_token": token_data["access_token"],
            "patient_id": token_data.get("patient"),
            "encounter_id": token_data.get("encounter"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope")
        }
