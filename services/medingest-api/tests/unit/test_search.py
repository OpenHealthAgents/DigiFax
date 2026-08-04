"""
test_search.py
Unit and integration tests verifying OpenSearch tenant isolation, filters, and hybrid search.
"""

import pytest

from src.application.services.search_orchestrator import SearchOrchestrator
from src.domain.search.models import SearchDocument
from src.infrastructure.search.litellm_embedding_generator import LiteLlmEmbeddingGenerator
from src.infrastructure.search.opensearch_adapter import OpenSearchAdapter


# --- 1. Embedding Generator Tests ---

def test_litellm_embedding_generator() -> None:
    generator = LiteLlmEmbeddingGenerator()
    vector = generator.generate_embedding("Fasting Glucose blood report")
    assert len(vector) == 1536
    # Assert deterministic float generation from characters
    assert vector[0] == float(ord("F")) / 256.0


# --- 2. OpenSearch Adapter Tests ---

def test_opensearch_adapter_indexing_and_search() -> None:
    adapter = OpenSearchAdapter()

    doc1 = SearchDocument(
        document_id="doc-001",
        tenant_id="tenant-123",
        ocr_text="Patient name is John Doe. Fasting Glucose is 145 mg/dL.",
        entities={"patient": "John Doe"},
        fhir_resources=[],
        audit_logs=["Document uploaded"],
        embedding=[0.1] * 1536
    )
    doc2 = SearchDocument(
        document_id="doc-002",
        tenant_id="tenant-123",
        ocr_text="Total Cholesterol is 240 mg/dL for patient Jane Smith.",
        entities={"patient": "Jane Smith"},
        fhir_resources=[],
        audit_logs=["Ingested"],
        embedding=[0.2] * 1536
    )
    doc3 = SearchDocument(
        document_id="doc-003",
        tenant_id="tenant-456",
        ocr_text="Glucose level of 105 mg/dL for patient on tenant-456.",
        entities={"patient": "Jane Smith"},
        fhir_resources=[],
        audit_logs=["Ingested"],
        embedding=[0.1] * 1536
    )

    adapter.index_document(doc1)
    adapter.index_document(doc2)
    adapter.index_document(doc3)

    # Test Keyword Search under tenant-123 (should only match doc1, NOT doc3 despite containing 'Glucose')
    results_kw = adapter.keyword_search("Glucose", tenant_id="tenant-123")
    assert len(results_kw) == 1
    assert results_kw[0].document_id == "doc-001"
    assert "glucose" in results_kw[0].highlights["ocr_text"][0].lower()

    # Test Keyword Search under tenant-456
    results_kw_other = adapter.keyword_search("Glucose", tenant_id="tenant-456")
    assert len(results_kw_other) == 1
    assert results_kw_other[0].document_id == "doc-003"

    # Test Vector Search (verify tenant filtering prevents cross-tenant vector matches)
    query_vector = [0.12] * 1536
    results_vec = adapter.vector_search(query_vector, tenant_id="tenant-123")

    assert len(results_vec) == 2
    # doc1 should rank higher due to closer vector match and doc3 should be omitted entirely
    assert results_vec[0].document_id == "doc-001"
    assert "doc-003" not in [r.document_id for r in results_vec]

    # Test parameter validation
    with pytest.raises(ValueError):
        adapter.keyword_search("Glucose", tenant_id="")
    with pytest.raises(ValueError):
        adapter.vector_search(query_vector, tenant_id="   ")


# --- 3. Hybrid Search Orchestrator Tests ---

def test_search_orchestrator_hybrid_rrf() -> None:
    adapter = OpenSearchAdapter()
    generator = LiteLlmEmbeddingGenerator()
    orchestrator = SearchOrchestrator(adapter, generator)

    # Index documents using orchestrator
    orchestrator.index(
        doc_id="doc-001",
        tenant_id="tenant-123",
        ocr_text="Hematology Panel. Hemoglobin count is normal.",
        entities={"analyte": "Hemoglobin"},
        fhir_resources=[],
        audit_logs=["Reviewed"]
    )
    orchestrator.index(
        doc_id="doc-002",
        tenant_id="tenant-123",
        ocr_text="Chemistry Panel. Blood Urea Nitrogen level is high.",
        entities={"analyte": "BUN"},
        fhir_resources=[],
        audit_logs=["Reviewed"]
    )
    orchestrator.index(
        doc_id="doc-003",
        tenant_id="tenant-456",
        ocr_text="Hematology Panel. Hemoglobin count is normal on other tenant.",
        entities={"analyte": "Hemoglobin"},
        fhir_resources=[],
        audit_logs=["Reviewed"]
    )

    # Execute hybrid search query matching both keyword and semantic bounds
    results = orchestrator.hybrid_search("Hemoglobin Normal count", tenant_id="tenant-123", limit=2)

    assert len(results) >= 1
    # doc-001 contains "Hemoglobin" and "normal" and matches tenant-123
    assert results[0]["document_id"] == "doc-001"
    assert "doc-003" not in [r["document_id"] for r in results]
    assert results[0]["rrf_score"] > 0.0
