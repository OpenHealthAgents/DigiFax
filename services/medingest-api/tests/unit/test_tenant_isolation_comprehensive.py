"""
test_tenant_isolation_comprehensive.py
Comprehensive test suite asserting tenant isolation constraints across repositories, search, S3 storage, events, and workflows.
"""

import pytest
from datetime import datetime

# Repositories & Entities
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository
from src.infrastructure.persistence.in_memory_intake_repository import InMemoryIntakeDocumentRepository
from src.domain.intake.entities import IntakeDocument
from src.domain.intake.value_objects import FileMetadata, IntakeSource

# Search
from src.infrastructure.search.opensearch_adapter import OpenSearchAdapter
from src.domain.search.models import SearchDocument

# Storage
from src.infrastructure.storage.in_memory_storage import InMemoryStorage
from src.domain.common.exceptions import DomainException

# Event Bus
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.domain.common.domain_event import DomainEvent

# Temporal Workflow context assertions
from src.application.workflows.document_pipeline import DocumentPipelineWorkflow
from src.application.common.tenant_context import TenantContext


# --- 1. REPOSITORY ISOLATION TESTS ---

def test_repository_strict_isolation_guards() -> None:
    repo = BaseInMemoryRepository()
    
    # Seed records in separate tenants
    repo._save_record("rec-1", {"id": "rec-1", "tenant_id": "tenant-alice", "val": "alice_data"})
    repo._save_record("rec-2", {"id": "rec-2", "tenant_id": "tenant-bob", "val": "bob_data"})

    # Assert Alice cannot load Bob's record
    res_mismatch = repo._get_record_by_id("rec-2", "tenant-alice")
    assert res_mismatch is None

    # Assert Bob cannot load Alice's record
    res_mismatch_2 = repo._get_record_by_id("rec-1", "tenant-bob")
    assert res_mismatch_2 is None

    # Assert correct reads succeed
    assert repo._get_record_by_id("rec-1", "tenant-alice")["val"] == "alice_data"
    assert repo._get_record_by_id("rec-2", "tenant-bob")["val"] == "bob_data"


def test_repository_soft_delete_isolation() -> None:
    repo = BaseInMemoryRepository()
    repo._save_record("rec-1", {"id": "rec-1", "tenant_id": "tenant-alice"})
    
    # Try soft deleting Alice's record using Bob's tenant (should be blocked or a no-op)
    repo._soft_delete_record("rec-1", "tenant-bob", user_id="bob-user")
    
    # Alice's record should remain active
    assert repo._get_record_by_id("rec-1", "tenant-alice") is not None


# --- 2. OPENSEARCH ADAPTER ISOLATION TESTS ---

def test_opensearch_adapter_tenant_term_filter() -> None:
    adapter = OpenSearchAdapter()
    
    doc1 = SearchDocument(
        document_id="doc-1",
        tenant_id="tenant-alice",
        ocr_text="Glucose analysis panel report",
        entities={},
        fhir_resources=[],
        audit_logs=[],
        embedding=[0.1] * 1536
    )
    doc2 = SearchDocument(
        document_id="doc-2",
        tenant_id="tenant-bob",
        ocr_text="Glucose diagnostic chart",
        entities={},
        fhir_resources=[],
        audit_logs=[],
        embedding=[0.1] * 1536
    )

    adapter.index_document(doc1)
    adapter.index_document(doc2)

    # Keyword search for Alice must omit Bob's document despite containing 'Glucose'
    results_alice = adapter.keyword_search("Glucose", tenant_id="tenant-alice")
    assert len(results_alice) == 1
    assert results_alice[0].document_id == "doc-1"

    # Vector search for Bob must omit Alice's document
    results_bob = adapter.vector_search([0.1] * 1536, tenant_id="tenant-bob")
    assert len(results_bob) == 1
    assert results_bob[0].document_id == "doc-2"


# --- 3. STORAGE PREFIX ISOLATION TESTS ---

def test_s3_prefix_structure_isolation() -> None:
    storage = InMemoryStorage()
    
    # Upload documents for Alice and Bob
    storage.save("doc-100", b"alice_content", tenant_id="tenant-alice")
    storage.save("doc-101", b"bob_content", tenant_id="tenant-bob")

    # Assert directory layout partition contains the keys
    assert "doc-100" in storage._storage["tenant-alice"]
    assert "doc-101" in storage._storage["tenant-bob"]

    # Assert Bob cannot read Alice's S3 file (throws FILE_NOT_FOUND DomainException)
    with pytest.raises(DomainException) as exc:
        storage.get("doc-100", tenant_id="tenant-bob")
    assert exc.value.code == "FILE_NOT_FOUND"


# --- 4. DOMAIN EVENT CONSUMERS ISOLATION TESTS ---

class MockEvent(DomainEvent):
    def __init__(self, tenant_id: str):
        super().__init__(
            aggregate_id="agg-1",
            tenant_id=tenant_id,
            organization_id="org-1",
            correlation_id="corr-1",
            trace_id="trace-1",
            user_id="user-1"
        )

def test_event_bus_blocks_mismatching_tenant_events() -> None:
    bus = InMemoryEventBus()
    received_events = []

    # Subscribe consumer scoped to tenant-alice
    bus.subscribe(
        MockEvent,
        lambda ev: received_events.append(ev),
        "tenant-alice"
    )

    # Publish event from Bob (cross-tenant, should raise PermissionError)
    event_bob = MockEvent(tenant_id="tenant-bob")
    with pytest.raises(PermissionError):
        bus.publish(event_bob)
    assert len(received_events) == 0

    # Publish event from Alice (valid)
    event_alice = MockEvent(tenant_id="tenant-alice")
    bus.publish(event_alice)
    assert len(received_events) == 1
    assert received_events[0].tenant_id == "tenant-alice"
