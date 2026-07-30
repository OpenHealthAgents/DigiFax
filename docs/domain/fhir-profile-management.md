# Domain Guide: FHIR Profile Management

The **FHIR Profile Management** Bounded Context enables tenants to select active standard FHIR Implementation Guides (such as US Core and International Patient Summary) and upload custom profiles (`StructureDefinition` resources) to run validation pipelines over resource JSON payloads.

---

## Architecture Context Map

```mermaid
graph TD
    User([Clinical Systems]) -->|POST Validate Resource| API[FHIR Profile REST API]
    API -->|validate_resource| Pipeline[FHIRProfileValidationPipeline]
    Pipeline -->|get_configuration| Repo[IFHIRProfileRepository]
    Pipeline -->|get_structure_definitions| Repo
    Repo -->|read / write| DB[(InMemory Persistence Store)]
```

---

## Domain Elements

### 1. Value Objects
* **`FHIRImplementationGuide`**: Represents an enabled Implementation Guide, defining the name, canonical URI, and version identifier.
* **`FHIRValidationResult`**: The result structure containing a boolean conformity status, list of errors/warnings, and the validated profile URL.

### 2. Entities & Aggregate Roots
* **`TenantFHIRProfileConfiguration` (Aggregate Root)**: Tracks tenant settings and active IGs.
* **`FHIRStructureDefinition`**: Represents a profile constraint set mapped to a FHIR resource type containing nested validation paths.

---

## Validation Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    Client->>API: POST /api/fhir/profile/validate
    API->>UseCase: execute(tenant_id, resource)
    UseCase->>Repo: get_configuration(tenant_id)
    Repo-->>UseCase: TenantFHIRProfileConfiguration (active_igs)
    UseCase->>Repo: get_structure_definitions(tenant_id)
    Repo-->>UseCase: list[FHIRStructureDefinition]
    UseCase->>Pipeline: validate_resource(resource, active_igs, structure_definitions)
    Pipeline->>Pipeline: Check profile matches active IGs
    Pipeline->>Pipeline: Evaluate path constraint elements
    Pipeline-->>UseCase: FHIRValidationResult
    UseCase-->>API: ValidationResponse
    API-->>Client: HTTP 200 OK (valid: true/false)
```
