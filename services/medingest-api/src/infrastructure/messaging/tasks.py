"""
tasks.py
Celery background worker task definitions.
"""

import json
from src.infrastructure.messaging.celery_app import app


@app.task(name="src.infrastructure.messaging.tasks.process_domain_event_task")
def process_domain_event_task(event_json: str) -> str:
    """
    Consumes a serialized domain event and performs asynchronous downstream tasks.
    """
    event_data = json.loads(event_json)
    event_type = event_data.get("event_type")
    tenant_id = event_data.get("tenant_id")
    aggregate_id = event_data.get("aggregate_id")

    log_message = f"[Celery Worker] Received {event_type} for tenant {tenant_id}, document {aggregate_id}"
    print(log_message)

    # 1. Coordinate specific handlers based on event types
    if event_type == "DocumentIngestedEvent":
        payload = event_data.get("payload", {})
        filename = payload.get("filename")
        storage_path = payload.get("storage_path")

        # In production, this task would trigger:
        # - OCR extraction stage (Google DocAI / ClamAV scan)
        # - LLM clinical concept extraction
        # - FHIR converter/validator export pipelines
        print(
            f"[Celery Worker] Downstream process starting: OCR & clinical indexing on {filename} at {storage_path}..."
        )

    elif event_type == "DocumentIntakeFailedEvent":
        payload = event_data.get("payload", {})
        reason = payload.get("reason")
        print(f"[Celery Worker] Intake failure alerts dispatched to system logs. Reason: {reason}")

    return f"Processed {event_type} successfully."
