# DigiFax Backend REST API

Clean Hexagonal Architecture backend for ingestion, OCR, parsing, and clinical EHR delivery.

## Structure
* **`src/domain/`**: Pure enterprise business rules and aggregates (Tenant, IntakeDocument, custom roles, feature flags, subscriptions).
* **`src/application/`**: Use cases and outbound ports (interfaces for billing, EHR delivery, OpenSearch keyword indexing).
* **`src/infrastructure/`**: Concrete adapters (FastAPI controllers, base repository implementations, in-memory databases, LiteLLM extractors).

## Setup
Using Python `uv` tool:
```powershell
uv venv
.venv\Scripts\activate
uv sync
```

## Running Tests
To run all verification suites:
```powershell
uv run python -m pytest tests/unit/
```
