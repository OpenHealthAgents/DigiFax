# medingest Digital Fax Ingestion System: DDD Domain Model Specification

This document defines the comprehensive Domain-Driven Design (DDD) domain model for **medingest**. It identifies the business subdomains, classifies them, outlines the Bounded Context mapping, and specifies the Aggregates, Entities, Value Objects, Repositories, and Domain Events for each of the 12 business subdomains.

---

## 1. Domain Categorization

To align engineering efforts with business value, the 12 domains are categorized into **Core**, **Supporting**, and **Generic** subdomains:

```mermaid
graph TD
    %% Subdomain Categorization
    subgraph "Core Subdomains (Differentiators)"
        Intake["Document Intake\n(Fax & Upload Ingestion)"]
        AIExtract["AI Extraction\n(Segmenting & Extraction)"]
        Match["Patient Matching\n(Demographics Resolving)"]
        Review["Human Review (HITL)\n(Manual Gating)"]
    end

    subgraph "Supporting Subdomains (Necessary helper logic)"
        Terminology["Medical Terminology\n(LOINC/SNOMED Mapping)"]
        FhirGen["FHIR Generation\n(R4 Serialization)"]
        Validation["Validation\n(Clinical Rules Checking)"]
        Export["Export / Delivery\n(EHR Transmission Gateways)"]
        Org["Organizations\n(Multi-tenant Context)"]
    end

    subgraph "Generic Subdomains (Standard off-the-shelf logic)"
        Ocr["OCR\n(Text Layout Processing)"]
        Auth["Authentication\n(RBAC & JWT Sessions)"]
        Audit["Audit\n(HIPAA Traceability Logs)"]
    end

    classDef core fill:#ffebeb,stroke:#cc0000,stroke-width:2px,color:#000;
    classDef support fill:#ebebff,stroke:#0000cc,stroke-width:1px,color:#000;
    classDef generic fill:#f2f2f2,stroke:#666666,stroke-dasharray: 5 5,color:#000;

    class Intake,AIExtract,Match,Review core;
    class Terminology,FhirGen,Validation,Export,Org support;
    class Ocr,Auth,Audit generic;
```

---

## 2. Bounded Context Map

The relationship and translation pathways between contexts are mapped using DDD strategic relationship patterns:

```mermaid
stateDiagram-v2
    IntakeContext: Document Intake Context
    OcrContext: OCR Context
    ExtractionContext: AI Extraction Context
    TerminologyContext: Medical Terminology Context
    FhirContext: FHIR Generation Context
    ValidationContext: Validation Context
    HitlContext: Human Review (HITL) Context
    ExportContext: Export Context
    AuditContext: Audit Context
    OrgContext: Organizations Context
    AuthContext: Authentication Context

    %% Relationships
    IntakeContext --> OcrContext : Customer-Supplier (Upstream: Intake)
    OcrContext --> ExtractionContext : Customer-Supplier (Upstream: OCR)
    ExtractionContext --> TerminologyContext : Shared Kernel (Common Schema Definitions)
    TerminologyContext --> FhirContext : Conformist
    FhirContext --> ValidationContext : Customer-Supplier (Upstream: FHIR)
    ValidationContext --> HitlContext : Customer-Supplier (Upstream: Validation)
    HitlContext --> ExportContext : Customer-Supplier (Upstream: HITL)

    OrgContext --> IntakeContext : Downstream Context injection
    AuthContext --> HitlContext : Downstream RBAC verification

    %% Audit receives events from all (Published Language / Event Sourced)
    IntakeContext --> AuditContext : Published Language
    ExtractionContext --> AuditContext : Published Language
    HitlContext --> AuditContext : Published Language
    ExportContext --> AuditContext : Published Language
```

- **Shared Kernel**: The `AI Extraction` and `Medical Terminology` contexts share the base clinical Pydantic schemas (`resources.py`) to map variables in-place.
- **Customer-Supplier**: `Document Intake` supplies raw files to `OCR`. `OCR` supplies page text layouts to `AI Extraction`. `Validation` supplies failed segments to the `Human Review (HITL)` context.
- **Conformist**: `FHIR Generation` conforms directly to the domain schemas defined by `Medical Terminology` and `AI Extraction` and transforms them to standard R4 protobufs.
- **Published Language**: The `Audit` context consumes domain events published in a public language format by all contexts to record compliance logs.

---

## 3. Detailed Subdomain Specifications

### 1. Document Intake Subdomain (Core)

- **Responsibility**: Ingests raw faxes (PSTN/FoIP) and manual file uploads, performs file size/integrity checks, generates a unique `FaxId`, and writes bytes to S3 object storage.

```mermaid
classDiagram
    class InboundFax {
        <<Aggregate Root>>
        +FaxId id
        +FaxMetadata metadata
        +FaxStatus status
        +Attachment rawDocument
        +receive()
        +registerAttachment(path, hash)
        +fail(reason)
    }
    class Attachment {
        <<Entity>>
        +AttachmentId id
        +string filePath
        +string fileHash
        +string mimeType
        +long sizeBytes
    }
    class FaxMetadata {
        <<Value Object>>
        +string senderNumber
        +string receiverNumber
        +datetime receivedAt
        +int pageCount
        +string gatewayCallId
    }
    InboundFax "1" *-- "1" Attachment
    InboundFax "1" *-- "1" FaxMetadata
```

- **Domain Events**:
  - `FaxReceivedEvent`: Fired when a fax is successfully registered and written to storage.
  - `IntakeFailedEvent`: Fired if files are corrupted or page boundaries cannot be read.
- **Repository Interface**:
  ```python
  class IInboundFaxRepository(abc.ABC):
      def save(self, fax: InboundFax) -> None: ...
      def get_by_id(self, id: FaxId) -> InboundFax | None: ...
  ```

---

### 2. OCR Subdomain (Generic)

- **Responsibility**: Coordinates with OCR engines (Tesseract, Cloud Document AI, etc.) to extract raw text content, word coordinates, and structural layouts from rendered page images.

```mermaid
classDiagram
    class OcrSession {
        <<Aggregate Root>>
        +OcrSessionId id
        +FaxId faxId
        +OcrStatus status
        +OcrPage[] pages
        +startOcr()
        +recordResults(OcrPage[] pages)
        +fail(reason)
    }
    class OcrPage {
        <<Entity>>
        +int pageNumber
        +OcrWord[] words
        +string fullText
    }
    class OcrWord {
        <<Value Object>>
        +string text
        +BoundingBox boundingBox
        +float confidence
    }
    class BoundingBox {
        <<Value Object>>
        +float xMin
        +float yMin
        +float xMax
        +float yMax
    }
    OcrSession "1" *-- "many" OcrPage
    OcrPage "1" *-- "many" OcrWord
    OcrWord "1" *-- "1" BoundingBox
```

- **Domain Events**:
  - `OcrCompletedEvent`: Fired when all pages are parsed and transcribed.
  - `OcrFailedEvent`: Fired if the layout translation crashes or returns empty responses.
- **Repository Interface**:
  ```python
  class IOcrSessionRepository(abc.ABC):
      def save(self, session: OcrSession) -> None: ...
      def get_by_fax_id(self, fax_id: FaxId) -> OcrSession | None: ...
  ```

---

### 3. AI Extraction Subdomain (Core)

- **Responsibility**: Invokes LLMs to partition a multi-page document into segments, classify their document types (e.g. Lab Report vs. Prescription), and extract structured clinical fields into target Pydantic schemas.

```mermaid
classDiagram
    class ExtractionJob {
        <<Aggregate Root>>
        +JobId id
        +FaxId faxId
        +ExtractionStatus status
        +ExtractedSegment[] segments
        +startJob()
        +addSegment(segment)
        +complete()
    }
    class ExtractedSegment {
        <<Entity>>
        +SegmentId id
        +MedicalDocumentType documentType
        +PageRange pageRange
        +string rawPayloadJson
        +float confidenceScore
    }
    class PageRange {
        <<Value Object>>
        +int startPage
        +int endPage
    }
    ExtractionJob "1" *-- "many" ExtractedSegment
    ExtractedSegment "1" *-- "1" PageRange
```

- **Domain Events**:
  - `DocumentSegmentedEvent`: Fired when document boundaries and types are classified.
  - `ExtractionCompletedEvent`: Fired when structured JSON schemas are generated.
  - `ExtractionFailedEvent`: Fired when the model returns unparseable outputs or times out.
- **Repository Interface**:
  ```python
  class IExtractionJobRepository(abc.ABC):
      def save(self, job: ExtractionJob) -> None: ...
      def get_by_id(self, id: JobId) -> ExtractionJob | None: ...
  ```

---

### 4. Patient Matching Subdomain (Core)

- **Responsibility**: Compares extracted patient demographics against the local database or an external Master Patient Index (MPI) via FHIR queries to link the fax securely to a single patient identifier.

```mermaid
classDiagram
    class PatientMatchSession {
        <<Aggregate Root>>
        +SessionId id
        +SegmentId segmentId
        +MatchStatus status
        +PatientDemographics extractedDemographics
        +MatchCandidate[] candidates
        +resolvedPatientId MatchedPatientId
        +searchCandidates(IMpiGateway gateway)
        +resolve(MatchedPatientId patientId)
        +flagConflict()
    }
    class MatchCandidate {
        <<Entity>>
        +string externalPatientId
        +PatientDemographics demographics
        +float matchScore
    }
    class PatientDemographics {
        <<Value Object>>
        +string name
        +datetime dateOfBirth
        +string gender
        +string mrn
    }
    PatientMatchSession "1" *-- "many" MatchCandidate
    PatientMatchSession "1" *-- "1" PatientDemographics
    MatchCandidate "1" *-- "1" PatientDemographics
```

- **Domain Events**:
  - `PatientMatchedEvent`: Fired when a candidate matches above the threshold or is manually chosen.
  - `PatientMatchConflictDetectedEvent`: Fired when multiple candidates share similar scores, halting auto-ingestion.
  - `PatientNotFoundEvent`: Fired when no matching database record is resolved.
- **Repository Interface**:
  ```python
  class IPatientMatchSessionRepository(abc.ABC):
      def save(self, session: PatientMatchSession) -> None: ...
      def get_by_id(self, id: SessionId) -> PatientMatchSession | None: ...
  ```

---

### 5. Medical Terminology Subdomain (Supporting)

- **Responsibility**: Standardizes raw clinical values (analytes, units, specimens) into canonical codes (e.g. LOINC, SNOMED CT) using precomputed offline knowledge base indexes and string anagram matching.

```mermaid
classDiagram
    class TerminologySession {
        <<Aggregate Root>>
        +SessionId id
        +SegmentId segmentId
        +CodingStatus status
        +CodingEntry[] entries
        +mapCodes(ITerminologyIndex index)
    }
    class CodingEntry {
        <<Entity>>
        +EntryId id
        +string extractedValue
        +CodingSystem system
        +string matchedCode
        +string matchedDisplay
        +string matchStrategy
    }
    TerminologySession "1" *-- "many" CodingEntry
```

- **Domain Events**:
  - `TerminologyEnrichedEvent`: Fired when all extractable entities have standard code assignments.
  - `TerminologyResolutionFailedEvent`: Fired if critical values (like a high-risk lab analyte) cannot be resolved.
- **Repository Interface**:
  - Medical Terminology reads pre-loaded indexes (`loinc_analaytes_index_csv_path`) using read-only in-memory indices, hence a standard mutable repository is not required. Rather, it accesses an index service interface:
  ```python
  class ITerminologyIndex(abc.ABC):
      def search_analyte(self, query: str) -> list[LoincCandidate]: ...
  ```

---

### 6. FHIR Generation Subdomain (Supporting)

- **Responsibility**: Translates validated Pydantic domain models into official HL7 FHIR R4 JSON structures (such as DiagnosticReport, Observation, and DocumentReference) using strict schema specifications.

```mermaid
classDiagram
    class FhirJob {
        <<Aggregate Root>>
        +JobId id
        +SegmentId segmentId
        +FhirStatus status
        +SerializedBundle payload
        +generate(IFhirConverter converter)
        +fail(reason)
    }
    class SerializedBundle {
        <<Value Object>>
        +string jsonContent
        +string fhirProfileUri
        +string checksum
    }
    FhirJob "1" *-- "1" SerializedBundle
```

- **Domain Events**:
  - `FhirBundleGeneratedEvent`: Fired when a bundle matches profile requirements.
  - `FhirGenerationFailedEvent`: Fired if serialization errors occur.
- **Repository Interface**:
  ```python
  class IFhirJobRepository(abc.ABC):
      def save(self, job: FhirJob) -> None: ...
      def get_by_segment_id(self, segment_id: SegmentId) -> FhirJob | None: ...
  ```

---

### 7. Validation Subdomain (Supporting)

- **Responsibility**: Validates clinical safety rules (e.g., matching reference range logic, validating past dates, flagging out-of-bound values) before transmission.

```mermaid
classDiagram
    class ValidationSession {
        <<Aggregate Root>>
        +SessionId id
        +SegmentId segmentId
        +ValidationStatus status
        +RuleResult[] ruleResults
        +evaluateRules(IValidationRegistry registry)
    }
    class RuleResult {
        <<Value Object>>
        +string ruleName
        +bool isPassed
        +string errorMessage
        +SeverityLevel severity
    }
    ValidationSession "1" *-- "many" RuleResult
```

- **Domain Events**:
  - `ValidationPassedEvent`: Fired when all critical clinical constraints pass.
  - `ValidationFailedEvent`: Fired if validation rules fail, gating subsequent transmission steps.
- **Repository Interface**:
  ```python
  class IValidationSessionRepository(abc.ABC):
      def save(self, session: ValidationSession) -> None: ...
  ```

---

### 8. Human Review / HITL Subdomain (Core)

- **Responsibility**: Manages human-in-the-loop task queues for manual data correction, conflict resolutions, and handwriting transcription.

```mermaid
classDiagram
    class ReviewTask {
        <<Aggregate Root>>
        +TaskId id
        +SegmentId segmentId
        +ReviewerId assignedReviewerId
        +ReviewStatus status
        +string originalDataJson
        +string correctedDataJson
        +TaskType taskType
        +assign(ReviewerId reviewerId)
        +submitCorrections(string correctedJson)
        +complete()
    }
    class TaskType {
        <<Value Object>>
        +string name
        +string validationReason
    }
    ReviewTask "1" *-- "1" TaskType
```

- **Domain Events**:
  - `ReviewTaskCreatedEvent`: Fired when validation or patient matching raises a manual review flag.
  - `ReviewTaskAssignedEvent`: Fired when a clinical reviewer claims the task.
  - `ReviewTaskCompletedEvent`: Fired when manual corrections are submitted and validated.
- **Repository Interface**:
  ```python
  class IReviewTaskRepository(abc.ABC):
      def save(self, task: ReviewTask) -> None: ...
      def get_by_id(self, id: TaskId) -> ReviewTask | None: ...
      def get_pending_tasks() -> list[ReviewTask]: ...
  ```

---

### 9. Export / Delivery Subdomain (Supporting)

- **Responsibility**: Handles transmitting validated FHIR bundles to external EHR destinations over secure channels (HTTPS, MLLP, SFTP), handling HTTP response parsing and retry policies.

```mermaid
classDiagram
    class ExportJob {
        <<Aggregate Root>>
        +ExportJobId id
        +FaxId faxId
        +ExportStatus status
        +ExportAttempt[] attempts
        +startAttempt(TargetDestination dest)
        +recordSuccess(string ackPayload)
        +recordFailure(string errorLog)
    }
    class ExportAttempt {
        <<Entity>>
        +AttemptId id
        +datetime attemptedAt
        +string responsePayload
        +bool isSuccess
    }
    class TargetDestination {
        <<Value Object>>
        +string urlEndpoint
        +string protocol
        +string credentialSecretName
    }
    ExportJob "1" *-- "many" ExportAttempt
    ExportJob "1" *-- "1" TargetDestination
```

- **Domain Events**:
  - `ExportSucceededEvent`: Fired when external EHR returns positive delivery acknowledgement.
  - `ExportFailedEvent`: Fired if max retries are exceeded.
  - `ExportRetryingEvent`: Fired when transient network errors trigger a retry schedule.
- **Repository Interface**:
  ```python
  class IExportJobRepository(abc.ABC):
      def save(self, job: ExportJob) -> None: ...
      def get_by_id(self, id: ExportJobId) -> ExportJob | None: ...
  ```

---

### 10. Audit Subdomain (Generic)

- **Responsibility**: Immutable event-sourcing and audit log recorder capturing every state change, user interaction, and database mutation for HIPAA security compliance.

```mermaid
classDiagram
    class AuditRecord {
        <<Aggregate Root>>
        +AuditRecordId id
        +datetime timestamp
        +UserContext userContext
        +string actionName
        +string entityType
        +string entityId
        +string beforeStateJson
        +string afterStateJson
    }
    class UserContext {
        <<Value Object>>
        +string userId
        +string ipAddress
        +string userAgent
    }
    AuditRecord "1" *-- "1" UserContext
```

- **Domain Events**:
  - Audit is a write-only sink. It consumes events from other domains to write audit trails. It does not dispatch domain events to trigger secondary business actions.
- **Repository Interface**:
  ```python
  class IAuditRepository(abc.ABC):
      def write(self, record: AuditRecord) -> None: ...
  ```

---

### 11. Organizations Subdomain (Supporting)

- **Responsibility**: Manages clinics, physical facilities, routing targets, and tenant settings in a multi-tenant hierarchy.

```mermaid
classDiagram
    class Organization {
        <<Aggregate Root>>
        +OrgId id
        +string name
        +OrgStatus status
        +RoutingRule[] routingRules
        +addRoutingRule(rule)
        +updateSettings(settings)
    }
    class RoutingRule {
        <<Value Object>>
        +MedicalDocumentType docType
        +string destinationUrl
        +bool requiresManualApproval
    }
    Organization "1" *-- "many" RoutingRule
```

- **Domain Events**:
  - `OrganizationCreatedEvent`: Fired when a new tenant clinic is registered.
  - `OrganizationRoutingUpdatedEvent`: Fired when delivery endpoints are modified.
- **Repository Interface**:
  ```python
  class IOrganizationRepository(abc.ABC):
      def save(self, org: Organization) -> None: ...
      def get_by_id(self, id: OrgId) -> Organization | None: ...
  ```

---

### 12. Authentication Subdomain (Generic)

- **Responsibility**: Validates user logins, session tokens, JWT signatures, and provides Role-Based Access Control (RBAC) permissions.

```mermaid
classDiagram
    class UserAccount {
        <<Aggregate Root>>
        +UserAccountId id
        +string email
        +UserRole role
        +AccountStatus status
        +UserSession[] sessions
        +login(string passwordHash)
        +logout(SessionId sessionId)
    }
    class UserSession {
        <<Entity>>
        +SessionId id
        +datetime expiresAt
        +string ipAddress
    }
    UserAccount "1" *-- "many" UserSession
```

- **Domain Events**:
  - `UserAuthenticatedEvent`: Fired upon successful verification.
  - `AuthenticationFailedEvent`: Fired when login credentials reject.
- **Repository Interface**:
  ```python
  class IUserAccountRepository(abc.ABC):
      def save(self, account: UserAccount) -> None: ...
      def get_by_email(self, email: str) -> UserAccount | None: ...
  ```

---

## 4. Domain Event Choreography Flow

The diagram below traces how domain events coordinate asynchronously to transition faxes from raw receipt to EHR ingestion:

```mermaid
sequenceDiagram
    autonumber
    participant Ingestion as Document Intake
    participant OCR as OCR Domain
    participant AI as AI Extraction
    participant Term as Terminology
    participant Match as Patient Matching
    participant Fhir as FHIR Generation
    participant Valid as Validation
    participant HITL as Human Review
    participant Exp as Export / Delivery
    participant Audit as Audit Logger

    %% Step 1: Intake
    Ingestion->>Ingestion: Ingest raw PDF file bytes
    Note over Ingestion: Dispatches FaxReceivedEvent
    Ingestion->>OCR: FaxReceivedEvent (FaxId, FilePath)
    Ingestion->>Audit: FaxReceivedEvent (Records intake action)

    %% Step 2: OCR
    OCR->>OCR: Execute page OCR parsing
    Note over OCR: Dispatches OcrCompletedEvent
    OCR->>AI: OcrCompletedEvent (FaxId, PagesText)
    OCR->>Audit: OcrCompletedEvent

    %% Step 3: AI Extract
    AI->>AI: Segment pages & extract JSON variables
    Note over AI: Dispatches ExtractionCompletedEvent
    AI->>Term: ExtractionCompletedEvent (SegmentId, ExtractedJson)
    AI->>Match: ExtractionCompletedEvent (SegmentId, Demographics)
    AI->>Audit: ExtractionCompletedEvent

    %% Step 4: Terminology & Patient Matching
    Term->>Term: Resolve LOINC codes
    Note over Term: Dispatches TerminologyEnrichedEvent
    Match->>Match: Search MPI registry candidates
    Note over Match: Dispatches PatientMatchedEvent

    Term->>Fhir: TerminologyEnrichedEvent
    Match->>Fhir: PatientMatchedEvent (MatchedPatientId)

    %% Step 5: FHIR Gen
    Fhir->>Fhir: Compile FHIR R4 Bundle
    Note over Fhir: Dispatches FhirBundleGeneratedEvent
    Fhir->>Valid: FhirBundleGeneratedEvent (BundleJson)
    Fhir->>Audit: FhirBundleGeneratedEvent

    %% Step 6: Validation & Gating
    Valid->>Valid: Evaluate clinical rules
    alt Validation Fails (Requires Review)
        Note over Valid: Dispatches ValidationFailedEvent
        Valid->>HITL: ValidationFailedEvent (SegmentId, RuleViolations)
        Valid->>Audit: ValidationFailedEvent

        HITL->>HITL: Create ReviewTask & wait for reviewer correction
        Note over HITL: Dispatches SegmentValidatedEvent
        HITL->>Exp: SegmentValidatedEvent (CorrectedBundleJson)
        HITL->>Audit: SegmentValidatedEvent
    else Validation Passes
        Note over Valid: Dispatches ValidationPassedEvent
        Valid->>Exp: ValidationPassedEvent (BundleJson)
        Valid->>Audit: ValidationPassedEvent
    end

    %% Step 7: Export
    Exp->>Exp: Deliver FHIR to Epic/Cerner Gateway
    Note over Exp: Dispatches ExportSucceededEvent
    Exp->>Audit: ExportSucceededEvent
```

---

## 5. Code Directory Mapping

In our Clean Architecture directory structure, these domain components are organized within `src/domain/`:

```directory
src/domain/
├── common/                         # Domain building blocks
│   ├── entity.py                   # Base class with structural ID equality
│   ├── value_object.py             # Base class implementing immutability
│   └── domain_event.py             # Event structures holding occurrences timestamp
├── intake/                         # Document Intake Context
│   ├── entities.py                 # InboundFax, Attachment
│   ├── value_objects.py            # FaxMetadata
│   └── events.py                   # FaxReceivedEvent
├── ocr/                            # OCR Context
│   ├── entities.py                 # OcrSession, OcrPage
│   ├── value_objects.py            # OcrWord, BoundingBox
│   └── events.py                   # OcrCompletedEvent
├── extraction/                     # AI Extraction Context
│   ├── entities.py                 # ExtractionJob, ExtractedSegment
│   ├── value_objects.py            # PageRange
│   └── events.py                   # ExtractionCompletedEvent
├── matching/                       # Patient Matching Context
│   ├── entities.py                 # PatientMatchSession, MatchCandidate
│   ├── value_objects.py            # PatientDemographics
│   └── events.py                   # PatientMatchedEvent
├── terminology/                    # Terminology Context
│   ├── entities.py                 # TerminologySession, MappedCodeEntry
│   └── events.py                   # TerminologyEnrichedEvent
├── fhir/                           # FHIR Generation Context
│   ├── entities.py                 # FhirJob
│   ├── value_objects.py            # SerializedBundle
│   └── events.py                   # FhirBundleGeneratedEvent
├── validation/                     # Validation Context
│   ├── entities.py                 # ValidationSession
│   ├── value_objects.py            # RuleResult
│   └── events.py                   # ValidationPassedEvent
├── review/                         # Human Review Context
│   ├── entities.py                 # ReviewTask
│   ├── value_objects.py            # TaskType
│   └── events.py                   # ReviewTaskCompletedEvent
├── export/                         # Export Context
│   ├── entities.py                 # ExportJob, ExportAttempt
│   ├── value_objects.py            # TargetDestination
│   └── events.py                   # ExportSucceededEvent
├── audit/                          # Audit Context
│   ├── entities.py                 # AuditRecord (Aggregate Root)
│   └── value_objects.py            # UserContext
├── organizations/                  # Organizations Context
│   ├── entities.py                 # Organization
│   ├── value_objects.py            # RoutingRule
│   └── events.py                   # OrganizationCreatedEvent
└── auth/                           # Authentication Context
    ├── entities.py                 # UserAccount, UserSession
    └── events.py                   # UserAuthenticatedEvent
```
