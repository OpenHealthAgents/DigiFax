# Bounded Context: Medical Terminology

The Medical Terminology bounded context governs standard clinical codings, local concept translations, value set overrides, and mapping approval audits.

---

## Supported Code Systems

The domain manages standard identifiers mapping to the following FHIR CodeSystem URIs:
* **LOINC** (`http://loinc.org`): Logical Observation Identifiers Names and Codes.
* **SNOMED CT** (`http://snomed.info/sct`): Systematized Nomenclature of Medicine Clinical Terms.
* **UCUM** (`http://unitsofmeasure.org`): Unified Code for Units of Measure.
* **ICD-10** (`http://hl7.org/fhir/sid/icd-10`): International Classification of Diseases 10th Revision.
* **RxNorm** (`http://www.nlm.nih.gov/research/umls/rxnorm`): Clinical Drug terminology.

---

## Mapping Approval Workflow

Local terminology codes (e.g. lab code `BG_NORM`) must be mapped to standard targets (e.g. SNOMED `302226006`).

To prevent unverified mapping lookups:
1. Mappings are initially proposed with state **`PENDING_APPROVAL`**.
2. Translating local codes disregards any pending rules.
3. Once reviewed and approved by a clinical terminologist, the status transitions to **`APPROVED`** (bumping the mapping's version index and saving a historical checkpoint).

---

## Versioning & Rollback Strategy

* **Aggregate Versioning**: `TenantConceptMap` holds a version index and a `history` log copying full rules list checkpoints.
* **Rollback Functionality**: Reverting a map to target version $V$ loads the copy corresponding to $V$, replaces active rules, and trims the historical timeline back to $V$, appending a rollback log.

---

## Tactical DDD Artifacts

### 1. Value Objects
* **`FHIRCoding`**: Immutable container representing standard system URIs, codes, and displays.
* **`ConceptMapRule`**: Binds a source local system/code to standard target system/codes with active status and preferred displays.

### 2. Aggregate Roots
* **`TenantConceptMap`**: Scopes rules list, proposes, approves, and rolls back rules lists.
* **`TenantValueSetOverride`**: Provides tenant-specific display overrides for standard code definitions.

### 3. Outbound Port
* **`ITerminologyRepository`**: Decouples terminology state persistence layers.
