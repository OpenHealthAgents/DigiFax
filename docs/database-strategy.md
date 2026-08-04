# Multi-Tenant Database Strategy

This document compares database isolation architectures and defines the strategy implemented for medingest.

---

## 1. Architectural Comparison

| Criteria | Shared Database, Shared Schema | Shared Database, Separate Schema | Separate Database per Tenant |
| :--- | :--- | :--- | :--- |
| **Isolation Strength** | Medium-High (Logical RLS) | High (Logical Schema) | Maximum (Physical) |
| **Cost Efficiency** | Maximum (High density) | Medium-High | Minimum (Low density) |
| **Maintenance / Migrations**| Extremely Simple (1 DDL run) | Complex (Loop schemas) | Extremely Complex |
| **Scalability Limit** | Database size limits | Catalog limit lookup | Instance limits |
| **Compliance (HIPAA)** | Compliant (Requires RLS) | Compliant | Compliant (Easiest auditing) |

### 1.1 Shared Database, Shared Schema (Row-Level Isolation)
Every table includes a `tenant_id` column. Tenant separation is enforced either programmatically in repository classes (e.g. `WHERE tenant_id = ?`) or natively by the database using PostgreSQL Row-Level Security (RLS).
* **Why it fits medingest**: medingest processes clinical fax document pipelines which have high metadata volatility but are logically simple. Enforcing RLS prevents cross-tenant leaks natively at the engine level while allowing us to deploy updates instantly to a single database schema.

### 1.2 Shared Database, Separate Schema (Schema Isolation)
Under a single database cluster, a schema is created per tenant (e.g., `schema tenant_123`).
* **Why it was rejected**: Upgrading schemas for hundreds of clinics requires loop migrations. If a migration fails halfway, database states become inconsistent, increasing support overhead.

### 1.3 Separate Database per Tenant (Physical Isolation)
Each tenant receives a dedicated SQL instance.
* **Why it was rejected**: Highly cost-inefficient. Idle clinics would still draw CPU/memory overhead, resulting in excessive operational costs.

---

## 2. Recommendation: Shared Schema with Row-Level Security (RLS)

medingest implements the **Shared Database, Shared Schema** strategy utilizing native **PostgreSQL Row-Level Security (RLS)**.

### How it works:
1. Every connection session sets a local configuration parameter representing the active tenant:
   ```sql
   SET LOCAL app.current_tenant_id = 'tenant-123';
   ```
2. PostgreSQL filters all operations against the target policy:
   ```sql
   CREATE POLICY tenant_isolation ON intake_documents
     USING (tenant_id = current_setting('app.current_tenant_id'));
   ```

---

## 3. Rollback Procedures

If a database migration must be rolled back due to deployment issues, run the generated rollback script:
```bash
psql -U postgres -d medingest -f services/medingest-api/deploy/migrations/0001_init_multi_tenant_rollback.sql
```

### Safety Rules:
> [!CAUTION]
> Running rollback drop commands deletes all stored columns and records permanently. **Always execute a backup pg_dump before rollbacks:**
> ```bash
> pg_dump -U postgres -d medingest -F c -b -v -f /deploy/backup/pre_rollback_backup.dump
> ```
