# DigiFax Platform: Comprehensive Operations & Development Guide

This guide compiles developer onboarding tutorials, administrative configuration policies, production deployment architectures, migration strategies, and security profiles.

---

## 1. Developer Onboarding Guide

### Project Setup
The DigiFax platform uses a monorepo workspace structure powered by `pnpm` (Next.js/React frontend) and Python `uv` (FastAPI backend).

1. **Install Frontend Dependencies**:
   ```powershell
   pnpm install
   ```
2. **Setup Backend Virtual Environment**:
   ```powershell
   cd services/digifax-api
   uv venv
   .venv\Scripts\activate
   uv sync
   ```

### Adding a New API Endpoint
1. **Define Schema**: Create a request validation model using Pydantic.
2. **Implement Guard**: Wrap route definitions inside the required permission checks dependency:
   ```python
   from src.infrastructure.controllers.api_guard import require_permissions

   @router.post("/new-feature")
   def execute_action(context=Depends(require_permissions("feature:write"))):
       # Safe scoped execution
       ...
   ```

---

## 2. Tenant Management Guide

Clinical operators are segmented into discrete Tenant boundary parameters.

### Creating a Tenant
Use the Tenant administration panel (`/admin` path on React frontend) or programmatic payloads to write to `ITenantRepository`:
* **ID**: String format, e.g. `tenant-hospital-net`.
* **Configuration**: Set MIME types (`application/pdf`), maximum daily upload caps, and feature flags.
* **Feature Toggles**: Custom configurations can lock or unlock beta modules (e.g. `ai_summarization`).

### Subscription Quotas
Administrators track metrics in real time against three tiers:
1. **Free**: 500 MB storage, 100 OCR pages, 1,000 monthly API calls.
2. **Professional**: 10 GB storage, 2,000 OCR pages, 50,000 API calls.
3. **Enterprise**: Custom contract quotas with access to `advanced_analytics` reports.

---

## 3. Production Deployment Guide

### Infrastructure Architecture
The service deploys as standard Docker containers orchestrated using Kubernetes or ECS.
* **REST API**: Serves FastAPIs using `uvicorn` runners.
* **Temporal Cluster**: Manages async worker orchestration task queues.
* **OpenSearch**: Keyword indexing cluster requiring tenant term filters.

### Core Environment Variables
Configure the backend server using the following keys:
* `ENV`: `"production"` or `"development"`.
* `TEMPORAL_HOST`: Address of the orchestration cluster (e.g., `localhost:7233`).
* `OPENSEARCH_HOST`: Search database connection.
* `ENCRYPTION_SECRET`: Master key for SSE-C simulations.

---

## 4. Database Migration & Rollback Guide

Transitioning legacy single-tenant tables requires execution of the `MigrationUtility` controller.

### Executing Migrations
Run the migration script to:
1. Initialize the `tenant-default` aggregate configuration.
2. Map unassigned user memberships.
3. Apply `tenant_id` namespaces to legacy document sessions.
4. Scope current running workflow states.

```python
from src.infrastructure.persistence.migration_utility import MigrationUtility

utility = MigrationUtility(tenant_repo, intake_repo, auth_service, workflows)
report = utility.execute_migration(default_tenant_id="tenant-default")
print(f"Migration completed: {report}")
```

### Rollback Strategy
If errors occur during execution:
```python
utility.rollback()
# Restores all repositories to exact pre-migration state snapshots.
```

---

## 5. Troubleshooting Guide

### Common Exceptions & Errors
* **`ConcurrencyException`**: Mismatch in optimistic version indices during record updates. Retry the transaction after re-fetching the updated object version.
* **`PermissionError`**: Attempted cross-tenant data access, incorrect SSE-C decryption keys, or locked file updates under active retention holds.
* **`DomainException (FILE_NOT_FOUND)`**: Target document path does not exist inside the current tenant workspace folder.

---

## 6. Security & Cryptographic Guide

### Authentication Verification
Session authorization tokens are validated at route execution times. Production environments must map authentications to signed JSON Web Tokens (RS256 JWT) containing user permissions, tenant keys, and expirations.

### SSE-C Encryption at Rest
Files are stored securely under `tenants/{tenant_id}/{document_id}`:
* Uploads encrypt byte streams if customer keys are provided.
* Retrieval requests are rejected if key signatures mismatch or are omitted.

---

## 7. Testing Guide

### Python pytest Suite
Execute backend tests including isolation boundaries checks:
```powershell
uv run python -m pytest tests/unit/
```

### UI E2E Playwright Stories
Execute Storybook vitest play functions (using Chromium headless instances):
```powershell
pnpm --filter design-system vitest run
```

---

## 8. Operations & Monitoring Guide

### Telemetry Monitoring
SaaS pipelines expose metrics via OpenTelemetry endpoints:
* **`document_ingested_total`**: Increment counter grouped by `tenant_id` and status.
* **`ocr_processing_duration_seconds`**: Histogram tracking document processing speeds.
* **`api_call_quota_consumption`**: Track API usages against monthly limits.
