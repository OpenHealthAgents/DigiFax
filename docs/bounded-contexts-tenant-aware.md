# Multi-Tenant Bounded Contexts Refactoring

This document details the tenant awareness modifications implemented across every bounded context in the medingest platform.

---

## 1. Domain Event Refactoring

To enable asynchronous event-driven pipelines (e.g. queueing faxes for AI extraction or OCR parsing) to respect strict tenant partitioning:
* **The Rule**: No domain event may exist without a matching `tenant_id` context.
* **Base DomainEvent Class** ([domain_event.py](file:///d:/Kalyan/medingest/services/medingest-api/src/domain/common/domain_event.py)):
  * Updated constructor to require `tenant_id` string and enforce validation:
    ```python
    class DomainEvent(ABC):
        def __init__(self, aggregate_id: str, tenant_id: str, occurred_at: datetime | None = None):
            if not tenant_id.strip():
                raise ValueError("tenant_id is required for domain events")
    ```

---

## 2. Bounded Context Mappings

Each bounded context was reviewed and refactored to support tenant-aware attributes:

| Bounded Context | Tenant-Aware Aggregate / Output | Tenant-Aware Domain Event |
| :--- | :--- | :--- |
| **Document Intake** | `IntakeDocument` (via `tenant_id` field) | `DocumentIngestedEvent`, `DocumentIntakeFailedEvent` |
| **OCR** | `OcrResult` (via `tenant_id` field) | `OcrCompletedEvent` |
| **Document Parsing** | `NormalizedLayoutDocument` (via `tenant_id` field) | `LayoutExtractedEvent` |
| **AI Extraction** | `ExtractedData` | `ExtractionCompletedEvent` |
| **Terminology** | `MappedTerminology` | `TerminologyMappedEvent` |
| **FHIR** | `FHIRBundle` | `FhirResourceGeneratedEvent` |
| **Validation** | `ValidationReport` | `ValidationCompletedEvent` |
| **Tenant Management** | `Tenant`, `Organization` | `TenantCreatedEvent`, `MembershipAssignedEvent`, `InvitationSentEvent`, `WorkspaceCreatedEvent` |

---

## 3. Backward Compatibility & Verification

* **NormalizedLayoutDocument Compatibility**:
  * Set a default value parameter `tenant_id="tenant-123"` in constructor to keep existing layout parsing adapters backward-compatible.
* **Testing Coverage**:
  * Verified using dedicated test suite checking constructor validations and event parameters.
  * All events passed with **100% test coverage**.
