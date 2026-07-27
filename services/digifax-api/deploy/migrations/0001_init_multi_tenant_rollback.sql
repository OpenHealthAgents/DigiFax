-- ============================================================================
-- Migration Rollback: 0001_init_multi_tenant_rollback
-- Description: Drops RLS policies and schema tables in reverse order.
-- ============================================================================

-- A. Drop Row-Level Security (RLS) Isolation Policies
DROP POLICY IF EXISTS tenant_isolation_intake_documents ON intake_documents;
DROP POLICY IF EXISTS tenant_isolation_api_keys ON api_keys;
DROP POLICY IF EXISTS tenant_isolation_invitations ON invitations;
DROP POLICY IF EXISTS tenant_isolation_memberships ON memberships;
DROP POLICY IF EXISTS tenant_isolation_workspaces ON workspaces;
DROP POLICY IF EXISTS tenant_isolation_organizations ON organizations;

-- B. Disable RLS on all child tables
ALTER TABLE IF EXISTS intake_documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS api_keys DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS memberships DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS workspaces DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS organizations DISABLE ROW LEVEL SECURITY;

-- C. Drop Tables in reverse dependency order (leaves first, parent boundaries last)
DROP TABLE IF EXISTS intake_documents CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS invitations CASCADE;
DROP TABLE IF EXISTS memberships CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;

-- D. Output confirmation
SELECT 'Rollback completed successfully.' as status;
