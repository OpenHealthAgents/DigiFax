# Domain Guide: Compliance & Privacy Policies

The **Compliance** Bounded Context enforces privacy regulations (HIPAA, GDPR, PIPEDA, Australian Privacy Act), consent opt-in scopes, retention rules schedules, legal hold account locks, and immutable access audit log timelines.

---

## Context Architecture Map

```mermaid
graph TD
    User([System Officers]) -->|API Actions| API[Compliance API Router]
    API -->|Purge Request| DeletionUseCase[RequestDataDeletionUseCase]
    DeletionUseCase -->|Check Active Lock| Consent[PatientConsent Aggregate Root]
    Consent -->|legal_hold active| Block([Block Purge: Conflict])
    Consent -->|legal_hold inactive| Purge([Execute Purge])
    API -->|Log Access| AuditUseCase[RecordAuditLogUseCase]
    AuditUseCase -->|append| Audit[(Audit Trail Registry)]
```

---

## Domain Elements

### 1. Value Objects
* **`ComplianceRegulation`**: Details name (HIPAA, GDPR, etc.), description, and enforcement region.
* **`ConsentPolicy`**: Patient's opt-in/opt-out status, scope, and signature timestamp.
* **`RetentionRule`**: Resource retention duration (days) and expiration action (Purge or Archive).
* **`AuditLogEntry`**: Access trail auditing tracking justification, user, action, and timestamp.

### 2. Aggregate Roots
* **`TenantComplianceConfiguration`**: Manages enabled regulations and retention rules.
* **`PatientConsent`**: Holds patient consent list records and toggles `legal_hold` active flags.

---

## Right to Deletion Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    Officer->>API: POST /api/compliance/delete (patient_id, justification)
    API->>UseCase: execute(tenant_id, patient_id, justification)
    UseCase->>Repo: get_consent(tenant_id, patient_id)
    Repo-->>UseCase: PatientConsent
    alt legal_hold is True
        UseCase-->>API: raise LegalHoldException
        API-->>Officer: HTTP 409 Conflict (Legal hold active)
    else legal_hold is False
        UseCase->>Repo: save_audit_entry(PURGE log)
        UseCase-->>API: Deletion Confirmed
        API-->>Officer: HTTP 200 OK (Patient records purged)
    end
```
