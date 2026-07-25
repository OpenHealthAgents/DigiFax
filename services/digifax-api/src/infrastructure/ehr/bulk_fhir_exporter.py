import logging
from typing import Any, cast

import requests

logger = logging.getLogger(__name__)

class BulkFhirExporter:
    """Manages SMART on FHIR Bulk Data Export ($export) and NDJSON collection."""

    def initiate_export(self, export_url: str, token: str) -> str:
        """Starts the bulk export process by requesting async response."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async"
        }

        logger.info(f"Initiating SMART Bulk Data Export: {export_url}")
        res = requests.get(export_url, headers=headers, timeout=15)

        if res.status_code != 202:
            raise ValueError(f"Failed to initiate bulk export. Expected HTTP 202, got {res.status_code}: {res.text}")

        poll_url = res.headers.get("Content-Location")
        if not poll_url:
            raise ValueError("EHR server response missed mandatory Content-Location polling header.")

        return str(poll_url)

    def poll_export_status(self, poll_url: str, token: str) -> dict[str, Any] | None:
        """Polls the status URL. Returns JSON output manifest if complete, otherwise None."""
        headers = {
            "Authorization": f"Bearer {token}"
        }

        res = requests.get(poll_url, headers=headers, timeout=10)

        if res.status_code == 202:
            logger.info("Bulk export job is still running (HTTP 202)...")
            return None

        if res.status_code == 200:
            logger.info("Bulk export job complete (HTTP 200)!")
            return cast(dict[str, Any], res.json())

        raise ValueError(f"Unexpected status polling response. HTTP {res.status_code}: {res.text}")

    def download_file(self, file_url: str, token: str) -> str:
        """Downloads NDJSON content block from the output file URL."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+ndjson"
        }

        logger.info(f"Downloading bulk export file: {file_url}")
        res = requests.get(file_url, headers=headers, timeout=30)
        res.raise_for_status()
        return str(res.text)
