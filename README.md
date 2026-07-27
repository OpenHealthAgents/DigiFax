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
* **Next.js Design System Showcase**: Consolidated Tailwind CSS v4 design tokens, WCAG AA touch-targets, responsive grid layouts, and comprehensive Storybook documentation.

---

## 📁 Architecture Directory Layout

```
DigiFax/
├── .github/workflows/          # GitHub Actions CI/CD workflows
├── apps/
│   └── design-system/          # Next.js & Tailwind CSS v4 component showcase portal
│       ├── public/             # Static public assets (e.g. sw.js for offline support)
│       └── src/
│           ├── app/            # Next.js App Router (Dashboard, Intake, Review, Admin, Settings, etc.)
│           ├── components/     # UI primitives and application layout shells
│           └── stories/        # Storybook story integrations
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
* Node.js v20+ & `pnpm` Package Manager
* Docker & Docker Compose

### 1. Ingestion Backend Setup
Clone the repository and install dependencies using `uv`:
```bash
cd services/digifax-api
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 1.5 Environment Configurations
Copy the environment variables template to `.env` in the project root directory and fill in your keys (e.g. Google Gemini and OpenAI keys):
```bash
cp .env.example .env
```

Start API:
```bash
uv run python src/main.py
```

### 2. Next.js Design System Portal Setup
Compile layout routes and Storybook registries:
```bash
cd apps/design-system
pnpm install
pnpm build
```

To run the development server locally:
```bash
pnpm dev
# Note: Next.js dev server will automatically proxy /api requests to the backend at http://localhost:8000 using next.config.ts rewrites.
```

To run Storybook locally:
```bash
pnpm storybook
```

---

## 🖥️ Next.js Application Route Map

* **Clinical Dashboard (`/`)**: Main hub tracking active intakes, validation alerts, and historical volume trends.
* **Document Intake (`/intake`)**: Drag-and-drop ingestion drops, queue loaders, duplicate detections, and target EHR selectors.
* **Clinical Review Workspace (`/review`)**: High-resolution split-screen PDF evidence highlighter and editable US Core observation records.
* **Document Repository (`/documents`)**: Dense records table with sort, density filters, and bulk operation actions.
* **Patient Chart (`/patient`)**: Patient demographics, glucose trend line plots, duplicates candidates, and timeline logs.
* **FHIR Explorer (`/fhir`)**: Syntax-highlighted FHIR Bundle structure trees, JSON editors, and conform checks.
* **Workflow Monitor (`/workflow`)**: Interconnected Temporal orchestrator activity flows, retry logs, and restart controls.
* **Observability Analytics (`/analytics`)**: KPI summaries (OCR accuracy, AI confidence), SVG line trends, reviewer productivity comparisons.
* **Administration Console (`/admin`)**: Configurations for users/roles, LLM models, OCR engines, active database heartbeats, and cluster usage metrics.
* **System Settings (`/settings`)**: Settings panel for branding custom primary colors, session timeout intervals, and S3 storage pathways.
* **Notification Center (`/notifications`)**: Inbox logs for mentions, review assignments, and simulated real-time toast alerts.
* **Primitives Gallery (`/design-system`)**: Live interactive showcase demonstrating Tailwind CSS v4 color tokens and Radix UI primitives.

---

## ⚙️ Mobile & Tablet Optimizations

* **Collapsible Layout Shell**: Automatically collapses navigation panels on screen resolutions under `1024px` to provide max workspace boundaries.
* **Extended Touch targets**: Enforces vertical link paddings (`py-3`) satisfying WCAG AA touch coordinates specifications (min `44x44px`).
* **Offline Cache Caching (`public/sw.js`)**: Service worker script caching app layouts and stylesheet variables to ensure offline availability.

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
