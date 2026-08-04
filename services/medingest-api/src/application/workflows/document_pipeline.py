"""
document_pipeline.py
Temporal workflow orchestrating the 10-stage clinical intake pipeline with TenantContext, retries, and Sagas.
"""

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

if TYPE_CHECKING:
    class MockWorkflow:
        def defn(self, *args: Any, **kwargs: Any) -> Any: ...
        def query(self, fn: Any) -> Any: ...
        def signal(self, fn: Any) -> Any: ...
        def run(self, fn: Any) -> Any: ...
        async def wait_condition(self, fn: Callable[[], bool]) -> None: ...
        async def execute_activity(self, activity: Any, *args: Any, **kwargs: Any) -> Any: ...
    class MockRetryPolicy:
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    workflow: MockWorkflow
    RetryPolicy: type[MockRetryPolicy]
else:
    try:
        from temporalio import workflow
        from temporalio.common import RetryPolicy
    except ImportError:
        # Fallback/mock decorators for testing environments without temporalio installed
        class MockWorkflow:  # type: ignore[no-redef]
            def defn(self, *args: Any, **kwargs: Any) -> Any:
                if args and callable(args[0]):
                    return args[0]
                return lambda f: f
            def query(self, fn: Any) -> Any:
                return fn
            def signal(self, fn: Any) -> Any:
                return fn
            def run(self, fn: Any) -> Any:
                return fn
            async def wait_condition(self, fn: Callable[[], bool]) -> None:
                import asyncio
                while not fn():
                    await asyncio.sleep(0.001)
            async def execute_activity(self, activity: Any, *args: Any, **kwargs: Any) -> Any:
                # If we mock execution, return a dummy status dict
                if activity == "intake_document":
                    return {"document_id": args[0].get("document_id"), "status": "ingested", "context": args[0].get("context")}
                if activity == "perform_ocr":
                    return {"document_id": args[0].get("document_id"), "status": "ocr_completed", "context": args[0].get("context")}
                if activity == "parse_layout":
                    return {"document_id": args[0].get("document_id"), "status": "layout_parsed", "context": args[0].get("context")}
                if activity == "extract_clinical_data":
                    # Fail simulation for saga test verification
                    if args[0].get("simulate_fail") == "extract":
                        raise ValueError("Simulated Extraction Failure")
                    return {"document_id": args[0].get("document_id"), "status": "extracted", "context": args[0].get("context")}
                if activity == "resolve_terminology":
                    return {"document_id": args[0].get("document_id"), "status": "terminology_resolved", "context": args[0].get("context")}
                if activity == "generate_fhir_bundle":
                    return {"document_id": args[0].get("document_id"), "fhir_bundle": {}, "status": "fhir_generated", "context": args[0].get("context")}
                if activity == "validate_bundle":
                    return {"document_id": args[0].get("document_id"), "is_valid": True, "status": "validated", "context": args[0].get("context")}
                if activity == "export_data":
                    return {"document_id": args[0].get("document_id"), "status": "exported", "context": args[0].get("context")}
                if activity == "archive_document":
                    return {"document_id": args[0].get("document_id"), "storage_bucket": "medingest-cold-archive", "status": "archived", "context": args[0].get("context")}
                return {}
        class MockRetryPolicy:  # type: ignore[no-redef]
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass
        workflow = MockWorkflow()  # type: ignore[assignment]
        RetryPolicy = MockRetryPolicy  # type: ignore[assignment]


@workflow.defn(name="DocumentPipelineWorkflow")
class DocumentPipelineWorkflow:
    """
    Temporal workflow orchestrating the 10-stage clinical intake pipeline with TenantContext bounds.

    Purpose:
        Coordinate asynchronous ingestion stages securely using Sagas rollback compensation.
    Business Reasoning:
        Clinical document lifecycles require trace validations, retry backups, and transactional safety.
    """

    def __init__(self) -> None:
        self.document_id: str = ""
        self.status: str = "initialized"
        self.progress_percent: float = 0.0
        self.fhir_bundle: dict[str, Any] | None = None
        self.review_approved: bool | None = None

    @workflow.query
    def get_status(self) -> dict[str, Any]:
        """Query handler exposing the current pipeline status."""
        return {
            "document_id": self.document_id,
            "status": self.status,
            "progress_percent": self.progress_percent
        }

    @workflow.query
    def get_bundle(self) -> dict[str, Any] | None:
        """Query handler exposing the compiled FHIR R4 Bundle."""
        return self.fhir_bundle

    @workflow.signal
    def approve_review(self) -> None:
        """Signal handler sent when a reviewer approves the extraction."""
        self.review_approved = True

    @workflow.signal
    def reject_review(self) -> None:
        """Signal handler sent when a reviewer rejects the extraction."""
        self.review_approved = False

    @workflow.run
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Runs the 10-stage document ingestion workflow under TenantContext scopes.
        """
        self.document_id = payload.get("document_id", "doc-default")
        self.status = "starting_pipeline"
        self.progress_percent = 5.0

        # Configure exponential backoff retry policy for all transient activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_attempts=3
        )

        context_header = {"context": payload.get("context", {})}

        try:
            # Audit log: STARTED
            await workflow.execute_activity(
                "log_pipeline_audit",
                {"context": payload.get("context"), "document_id": self.document_id, "milestone": "STARTED"},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )

            # 1. Document Intake
            self.status = "ingesting"
            intake_res = await workflow.execute_activity(
                "intake_document",
                payload,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.progress_percent = 10.0

            # 2. OCR Execution
            self.status = "running_ocr"
            ocr_res = await workflow.execute_activity(
                "perform_ocr",
                intake_res,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy
            )
            self.progress_percent = 20.0

            # 3. Document Parsing
            self.status = "parsing_layout"
            parse_res = await workflow.execute_activity(
                "parse_layout",
                ocr_res,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.progress_percent = 30.0

            # 4. AI Variable Extraction
            self.status = "extracting_ai"
            extraction_res = await workflow.execute_activity(
                "extract_clinical_data",
                parse_res,
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=retry_policy
            )
            self.progress_percent = 40.0

            # 5. Terminology Mapping
            self.status = "resolving_terminology"
            term_res = await workflow.execute_activity(
                "resolve_terminology",
                extraction_res,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.progress_percent = 50.0

            # 6. FHIR Generation
            self.status = "generating_fhir"
            fhir_res = await workflow.execute_activity(
                "generate_fhir_bundle",
                term_res,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.fhir_bundle = fhir_res.get("fhir_bundle")
            self.progress_percent = 60.0

            # 7. FHIR/Clinical Validation
            self.status = "validating"
            await workflow.execute_activity(
                "validate_bundle",
                fhir_res,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.progress_percent = 70.0

            # 8. Human-in-the-Loop Review Wait State
            self.status = "awaiting_human_review"
            await workflow.execute_activity(
                "log_pipeline_audit",
                {"context": payload.get("context"), "document_id": self.document_id, "milestone": "AWAITING_HUMAN_REVIEW"},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )
            
            # Wait for approval or rejection signal from the Review Portal
            await workflow.wait_condition(lambda: self.review_approved is not None)

            if self.review_approved is False:
                self.status = "rejected_by_reviewer"
                await workflow.execute_activity(
                    "log_pipeline_audit",
                    {"context": payload.get("context"), "document_id": self.document_id, "milestone": "REJECTED_BY_REVIEWER"},
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=retry_policy
                )
                return {
                    "document_id": self.document_id,
                    "status": "rejected",
                    "progress_percent": 100.0
                }

            self.status = "review_approved"
            self.progress_percent = 80.0
            await workflow.execute_activity(
                "log_pipeline_audit",
                {"context": payload.get("context"), "document_id": self.document_id, "milestone": "REVIEW_APPROVED"},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )

            # 9. Export Data to EHR
            self.status = "exporting"
            export_res = await workflow.execute_activity(
                "export_data",
                {"context": payload.get("context"), "document_id": self.document_id, "fhir_bundle": self.fhir_bundle},
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy
            )
            self.progress_percent = 90.0

            # 10. Cold Storage Archival
            self.status = "archiving"
            archive_res = await workflow.execute_activity(
                "archive_document",
                export_res,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy
            )

            self.status = "completed"
            self.progress_percent = 100.0

            # Audit log: COMPLETED
            await workflow.execute_activity(
                "log_pipeline_audit",
                {"context": payload.get("context"), "document_id": self.document_id, "milestone": "COMPLETED"},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )

            return {
                "document_id": self.document_id,
                "status": "completed",
                "progress_percent": 100.0,
                "archive_bucket": archive_res.get("storage_bucket")
            }

        except Exception as e:
            # Saga pattern compensation rollback trigger
            self.status = "failed"
            await workflow.execute_activity(
                "compensate_pipeline_failure",
                {"context": payload.get("context"), "document_id": self.document_id, "reason": str(e)},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )
            await workflow.execute_activity(
                "log_pipeline_audit",
                {"context": payload.get("context"), "document_id": self.document_id, "milestone": "FAILED"},
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )
            raise e
