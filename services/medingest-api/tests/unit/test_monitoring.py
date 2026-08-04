from src.infrastructure.monitoring.telemetry import MOCK_METER, TelemetryService


def test_telemetry_service_mock_instrumentation() -> None:
    service = TelemetryService(service_name="test-api")

    # 1. Test Spans
    with service.start_span("test_span_op"):
        # Code execution block inside span context
        pass

    # 2. Test Histograms Latency
    service.record_stage_duration("ocr_processing", 1.45)
    hist_latency = MOCK_METER.histograms["pipeline_stage_duration_seconds"]
    assert 1.45 in hist_latency.values
    assert hist_latency.labels_list[-1]["stage"] == "ocr_processing"

    # 3. Test OCR Confidence
    service.record_ocr_confidence(0.95, "tesseract")
    hist_ocr = MOCK_METER.histograms["ocr_confidence_score"]
    assert 0.95 in hist_ocr.values
    assert hist_ocr.labels_list[-1]["engine"] == "tesseract"

    # 4. Test AI Confidence
    service.record_ai_confidence(0.88, "llama-3")
    hist_ai = MOCK_METER.histograms["ai_confidence_score"]
    assert 0.88 in hist_ai.values
    assert hist_ai.labels_list[-1]["model"] == "llama-3"

    # 5. Test Terminology Counter
    service.record_terminology_resolution("mapped", "loinc")
    counter_term = MOCK_METER.counters["terminology_resolution_total"]
    assert counter_term.value == 1.0
    assert counter_term.labels_list[-1]["status"] == "mapped"
    assert counter_term.labels_list[-1]["code_system"] == "loinc"

    # 6. Test Export Counter
    service.record_export_status("epic_ehr", "success")
    counter_export = MOCK_METER.counters["export_status_total"]
    assert counter_export.value == 1.0
    assert counter_export.labels_list[-1]["destination"] == "epic_ehr"
    assert counter_export.labels_list[-1]["status"] == "success"


def test_health_check_status() -> None:
    service = TelemetryService()
    health = service.get_health_status()
    assert health["status"] == "healthy"
    assert health["services"]["database"] == "up"
    assert health["services"]["ocr_engines"] == "up"
    assert health["services"]["fhir_validator"] == "up"
