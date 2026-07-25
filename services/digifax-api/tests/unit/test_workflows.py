import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.workflows.activities import (
    intake_activity,
    ocr_activity,
    validation_activity,
)
from src.application.workflows.document_pipeline import DocumentPipelineWorkflow
from src.infrastructure.workflows.temporal_worker import TemporalWorkerManager

# --- 1. Activities Tests ---

@pytest.mark.anyio
async def test_intake_activity() -> None:
    res = await intake_activity({"document_id": "doc-555", "content": b"PDF_BYTES"})
    assert res["document_id"] == "doc-555"
    assert res["status"] == "ingested"


@pytest.mark.anyio
async def test_ocr_activity() -> None:
    res = await ocr_activity({"document_id": "doc-555"})
    assert res["status"] == "ocr_completed"
    assert len(res["pages"]) == 1


@pytest.mark.anyio
async def test_validation_activity() -> None:
    res = await validation_activity({"document_id": "doc-555"})
    assert res["is_valid"] is True
    assert res["issues"][0]["code"] == "ELEVATED_GLUCOSE"


# --- 2. Workflow Orchestration State & Logic Tests ---

@pytest.mark.anyio
@patch("src.application.workflows.document_pipeline.workflow.execute_activity")
async def test_workflow_orchestration_approval(mock_execute: MagicMock) -> None:
    # Setup mock sequence of execute_activity calls
    mock_execute.side_effect = [
        {"document_id": "doc-999", "status": "ingested"},        # Intake
        {"document_id": "doc-999", "status": "ocr_completed"},   # OCR
        {"document_id": "doc-999", "status": "layout_parsed"},   # Parsing
        {"document_id": "doc-999", "status": "extracted"},       # AI Extraction
        {"document_id": "doc-999", "status": "terminology_resolved"}, # Terminology
        {"document_id": "doc-999", "fhir_bundle": {"resourceType": "Bundle"}}, # FHIR Gen
        {"document_id": "doc-999", "is_valid": True},            # Validation
        {"document_id": "doc-999", "exported": True},            # Export
        {"document_id": "doc-999", "storage_bucket": "test-bucket"} # Archival
    ]

    wf = DocumentPipelineWorkflow()

    # Run the workflow in the background because it waits on human review
    payload = {"document_id": "doc-999"}
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
        {"document_id": "doc-999"},  # Intake
        {"document_id": "doc-999"},  # OCR
        {"document_id": "doc-999"},  # Parsing
        {"document_id": "doc-999"},  # Extraction
        {"document_id": "doc-999"},  # Terminology
        {"document_id": "doc-999", "fhir_bundle": {"resourceType": "Bundle"}},  # FHIR Gen
        {"document_id": "doc-999"}   # Validation
    ]

    wf = DocumentPipelineWorkflow()
    payload = {"document_id": "doc-999"}

    run_task = asyncio.create_task(wf.run(payload))
    await asyncio.sleep(0.01)

    # Send Reject signal
    wf.reject_review()

    result = await run_task
    assert result["status"] == "rejected"
    assert result["progress_percent"] == 100.0


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
