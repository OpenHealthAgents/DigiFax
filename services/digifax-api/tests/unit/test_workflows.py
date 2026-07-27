"""
test_workflows.py
Unit tests verifying Temporal workflows orchestration, retries, Saga compensations, and audit logs.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.application.workflows.activities import (
    intake_activity,
    ocr_activity,
    validation_activity,
    log_pipeline_audit,
    compensate_pipeline_failure,
)
from src.application.workflows.document_pipeline import DocumentPipelineWorkflow
from src.infrastructure.workflows.temporal_worker import TemporalWorkerManager


# --- 1. Activities Tests ---

@pytest.mark.anyio
async def test_intake_activity() -> None:
    payload = {
        "document_id": "doc-555",
        "content": b"PDF_BYTES",
        "context": {"tenant_id": "tenant-123", "user_id": "usr-1", "correlation_id": "corr-1"}
    }
    res = await intake_activity(payload)
    assert res["document_id"] == "doc-555"
    assert res["status"] == "ingested"


@pytest.mark.anyio
async def test_ocr_activity() -> None:
    payload = {
        "document_id": "doc-555",
        "context": {"tenant_id": "tenant-123"}
    }
    res = await ocr_activity(payload)
    assert res["status"] == "ocr_completed"
    assert len(res["pages"]) == 1


@pytest.mark.anyio
async def test_validation_activity() -> None:
    payload = {
        "document_id": "doc-555",
        "context": {"tenant_id": "tenant-123"}
    }
    res = await validation_activity(payload)
    assert res["is_valid"] is True
    assert res["issues"][0]["code"] == "ELEVATED_GLUCOSE"


@pytest.mark.anyio
async def test_audit_and_compensation_activities() -> None:
    payload = {
        "document_id": "doc-555",
        "context": {"tenant_id": "tenant-123"},
        "milestone": "COMPLETED",
        "reason": "Simulated error"
    }
    # These return None/run logging output without crashing
    await log_pipeline_audit(payload)
    await compensate_pipeline_failure(payload)


# --- 2. Workflow Orchestration State & Logic Tests ---

@pytest.mark.anyio
@patch("src.application.workflows.document_pipeline.workflow.execute_activity")
async def test_workflow_orchestration_approval(mock_execute: MagicMock) -> None:
    # Setup mock sequence of execute_activity calls
    mock_execute.side_effect = [
        None,                                                    # Audit: STARTED
        {"document_id": "doc-999", "status": "ingested"},        # Intake
        {"document_id": "doc-999", "status": "ocr_completed"},   # OCR
        {"document_id": "doc-999", "status": "layout_parsed"},   # Parsing
        {"document_id": "doc-999", "status": "extracted"},       # AI Extraction
        {"document_id": "doc-999", "status": "terminology_resolved"}, # Terminology
        {"document_id": "doc-999", "fhir_bundle": {"resourceType": "Bundle"}}, # FHIR Gen
        {"document_id": "doc-999", "is_valid": True},            # Validation
        None,                                                    # Audit: AWAITING_HUMAN_REVIEW
        None,                                                    # Audit: REVIEW_APPROVED
        {"document_id": "doc-999", "exported": True},            # Export
        {"document_id": "doc-999", "storage_bucket": "test-bucket"}, # Archival
        None                                                     # Audit: COMPLETED
    ]

    wf = DocumentPipelineWorkflow()

    # Run the workflow in the background because it waits on human review
    payload = {
        "document_id": "doc-999",
        "context": {"tenant_id": "tenant-123", "user_id": "usr-1", "correlation_id": "corr-1"}
    }
    run_task = asyncio.create_task(wf.run(payload))

    # Let it run up to the wait condition
    await asyncio.sleep(0.01)

    # Query intermediate status
    status_report = wf.get_status()
    assert status_report["document_id"] == "doc-999"
    assert status_report["status"] == "awaiting_human_review"
    assert status_report["progress_percent"] == 70.0

    # Send Approve signal
    wf.approve_review()

    # Await completion
    result = await run_task
    assert result["status"] == "completed"
    assert result["progress_percent"] == 100.0
    assert result["archive_bucket"] == "test-bucket"


@pytest.mark.anyio
@patch("src.application.workflows.document_pipeline.workflow.execute_activity")
async def test_workflow_orchestration_rejection(mock_execute: MagicMock) -> None:
    mock_execute.side_effect = [
        None,  # Audit: STARTED
        {"document_id": "doc-999"},  # Intake
        {"document_id": "doc-999"},  # OCR
        {"document_id": "doc-999"},  # Parsing
        {"document_id": "doc-999"},  # Extraction
        {"document_id": "doc-999"},  # Terminology
        {"document_id": "doc-999", "fhir_bundle": {"resourceType": "Bundle"}},  # FHIR Gen
        {"document_id": "doc-999"},  # Validation
        None,  # Audit: AWAITING_HUMAN_REVIEW
        None   # Audit: REJECTED_BY_REVIEWER
    ]

    wf = DocumentPipelineWorkflow()
    payload = {
        "document_id": "doc-999",
        "context": {"tenant_id": "tenant-123"}
    }

    run_task = asyncio.create_task(wf.run(payload))
    await asyncio.sleep(0.01)

    # Send Reject signal
    wf.reject_review()

    result = await run_task
    assert result["status"] == "rejected"
    assert result["progress_percent"] == 100.0


@pytest.mark.anyio
@patch("src.application.workflows.document_pipeline.workflow.execute_activity")
async def test_workflow_saga_compensation(mock_execute: MagicMock) -> None:
    # Fail at extraction step
    mock_execute.side_effect = [
        None,                                                    # Audit: STARTED
        {"document_id": "doc-999", "status": "ingested"},        # Intake
        {"document_id": "doc-999", "status": "ocr_completed"},   # OCR
        {"document_id": "doc-999", "status": "layout_parsed"},   # Parsing
        ValueError("Simulated Extraction Failure"),               # Extraction throws error
        None,                                                    # Compensation execution
        None                                                     # Audit: FAILED
    ]

    wf = DocumentPipelineWorkflow()
    payload = {
        "document_id": "doc-999",
        "context": {"tenant_id": "tenant-123"}
    }

    with pytest.raises(ValueError) as exc_info:
        await wf.run(payload)

    assert "Simulated Extraction Failure" in str(exc_info.value)
    assert wf.status == "failed"


# --- 3. Worker Launch Tests ---

@pytest.mark.anyio
async def test_worker_manager() -> None:
    # Verify manager connects and triggers run using inline sys.modules patch
    mock_client = MagicMock()
    mock_connect = AsyncMock(return_value=mock_client)

    mock_worker_inst = MagicMock()
    mock_worker_inst.run = AsyncMock()
    mock_worker_class = MagicMock(return_value=mock_worker_inst)

    mock_temporal_client = MagicMock()
    mock_temporal_client.Client.connect = mock_connect

    mock_temporal_worker = MagicMock()
    mock_temporal_worker.Worker = mock_worker_class

    modules_dict = {
        "temporalio": MagicMock(),
        "temporalio.client": mock_temporal_client,
        "temporalio.worker": mock_temporal_worker
    }

    with patch.dict("sys.modules", modules_dict):
        manager = TemporalWorkerManager(server_address="temporal-server:7233")
        await manager.start_worker()

        mock_connect.assert_called_once_with("temporal-server:7233")
        mock_worker_class.assert_called_once()
        mock_worker_inst.run.assert_called_once()
