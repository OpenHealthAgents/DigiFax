import logging

from src.application.workflows.activities import (
    archival_activity,
    export_activity,
    extraction_activity,
    fhir_activity,
    intake_activity,
    ocr_activity,
    parsing_activity,
    terminology_activity,
    validation_activity,
)
from src.application.workflows.document_pipeline import DocumentPipelineWorkflow

logger = logging.getLogger(__name__)

class TemporalWorkerManager:
    """Manages connection and launch of Temporal Workers executing the MedIngest pipeline."""

    def __init__(self, server_address: str = "localhost:7233", task_queue: str = "medingest-task-queue"):
        self.server_address = server_address
        self.task_queue = task_queue

    async def start_worker(self) -> None:
        """Connects client and runs the async Temporal worker loop."""
        try:
            from temporalio.client import Client
            from temporalio.worker import Worker

            logger.info(f"Connecting to Temporal Server at {self.server_address}...")
            client = await Client.connect(self.server_address)

            # Setup worker executing both pipeline workflow and its constituent activities
            worker = Worker(
                client,
                task_queue=self.task_queue,
                workflows=[DocumentPipelineWorkflow],
                activities=[
                    intake_activity,
                    ocr_activity,
                    parsing_activity,
                    extraction_activity,
                    terminology_activity,
                    fhir_activity,
                    validation_activity,
                    export_activity,
                    archival_activity
                ]
            )

            logger.info(f"Worker running successfully on queue '{self.task_queue}'...")
            await worker.run()

        except ImportError:
            logger.warning(
                "temporalio package is not installed in the current python context. "
                "Bypassing active worker launch."
            )
        except Exception as e:
            logger.error(f"Failed to execute Temporal worker loop: {str(e)}")
            raise e
