# DigiFax: Clinical Document Intake & Normalization Pipeline

DigiFax is a production-grade, event-driven medical document intake pipeline that ingests raw fax pages (PDFs/Images), performs OCR and layout parsing, extracts structured clinical data using LLMs, maps medical terminology, validates clinical resources against US Core profiles, orchestrates workflow states, exposes Model Context Protocol (MCP) tools, and exports clinical records to outbound EHR repositories (Epic, Cerner, Athena, Medplum).

---

## 🚀 Key Features

* **10-Stage Processing Pipeline**: Sequential intake, OCR, parsing, terminology mapping, FHIR generation, validation, review, and archival.
* **Clinical Rule Engine**: High-throughput rule engine checking OCR/AI confidence, physiological limits, duplicates, and FHIR compliance.
* **Human-in-the-Loop Workspace**: Reviewer dashboard with PDF evidence highlighting, data editing, and audit trails.
* **Workflow Orchestration**: Persistent workflows managed via Temporal for reliable state retries.
* **OpenSearch Hybrid Retrieval**: Vector k-NN semantic search fused with keyword BM25 retrieval using Reciprocal Rank Fusion (RRF).
* **Model Context Protocol (MCP)**: Server exposing clinical intake, extraction, normalizations, and FHIR validation tools.
* **EHR Integration Adapters**: Custom REST / Bulk FHIR adapters supporting HAPI FHIR, Medplum, Epic, Cerner, and Athenahealth.
* **OpenTelemetry Observability**: Telemetry tracing, Prometheus metric collection, Loki logs, and customized Grafana dashboards.
* **Production Infrastructure**: Kubernetes manifests, Helm charts, Docker Compose configurations, and automated backup scripts.

---

## 📁 Architecture Directory Layout

```
DigiFax/
├── .github/workflows/          # GitHub Actions CI/CD workflows
├── services/
│   └── digifax-api/
│       ├── deploy/             # Deployment configurations (Docker Compose, Kubernetes, Helm)
│       ├── src/
│       │   ├── application/    # Ports, services (Search, Validation), use cases, workflows
│       │   ├── domain/         # Core entities, value objects, builders (FHIR R4), validation rules
│       │   ├── infrastructure/ # Adapters (OpenSearch, LiteLLM, Terminology, EHR Exporters, Telemetry)
│       │   ├── interface/      # FastAPI handlers and Model Context Protocol (MCP) server
│       │   └── main.py         # Entrypoint
│       └── tests/              # Multi-tier testing suite (Unit, Integration, Contract, Performance, Security)
└── README.md
```

---

## 🛠️ Getting Started & Setup

### Prerequisites
* Python 3.12+
* `uv` Package Manager
* Docker & Docker Compose

### 1. Installation & Dependency Setup
Clone the repository and install dependencies using `uv`:
```bash
cd services/digifax-api
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Multi-Container Infrastructure
Spin up databases, Temporal workers, NATS, Redis, MinIO, OpenSearch, and metrics collectors:
```bash
docker compose -f deploy/docker-compose.yml up -d
```

### 3. Running the API Server
Start the FastAPI server:
```bash
uv run python src/main.py
```

### 4. Running the Temporal Worker
Launch the worker processing the asynchronous intake pipeline tasks:
```bash
uv run python src/infrastructure/workflows/temporal_worker.py
```

---

## 🧪 Comprehensive Testing Suite

DigiFax maintains a multi-layer test suite to verify every Clean Architecture boundary.

Run the test suite using `pytest`:
```bash
uv run python -m pytest
```

Our testing strategy contains:
* **Unit Tests (`tests/unit/`)**: Verifies builders, adapters, repositories, and use case layers independently.
* **Integration Tests (`tests/integration/`)**: Simulates the 10-stage end-to-end pipeline using the synthetic document generator.
* **Contract Tests (`tests/contract/`)**: Validates MCP tool parameter schema signatures to prevent interface drift.
* **Performance Benchmarks (`tests/performance/`)**: Measures rules engine validation and RRF rank fusion latency.
* **Security & Exception Boundary Tests (`tests/security/`)**: Validates malformed base64 parameter exceptions, SQL injection queries, and missing fields.

---

## 📊 Observability & Dashboards

Every service is fully instrumented using OpenTelemetry:
* **Metrics**: Scraped by Prometheus, visualizing latency, terminology accuracy, and EHR export success.
* **Traces**: Exported to Grafana Tempo, correlating intake transactions across workers.
* **Logs**: Aggregated by Loki.
* **Dashboards**: Grafana dashboard file is configured at `services/digifax-api/monitoring/grafana/dashboards/digifax_dashboard.json`.

---

## ☸️ Production Deployment & DR

* **Kubernetes Deployments**: Configured with Horizontal Pod Autoscaling (HPA) targeting CPU (75%) and memory (80%) thresholds.
* **Helm Chart**: Dynamic multi-environment chart located under `services/digifax-api/deploy/helm/digifax/`.
* **Backup script**: Automated database pg_dump and MinIO object store replication script available at `services/digifax-api/deploy/backup/backup.sh`.
