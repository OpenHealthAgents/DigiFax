/**
 * @file page.tsx
 * @description DigiFax Tenant Administration Console.
 * 
 * Provides administrative controls for tenant configuration, organization hierarchies,
 * user rosters, invitations, RBAC roles, API keys, feature flags, subscriptions,
 * compliance audit trails, and data retention policies.
 * 
 * BUSINESS CONTEXT:
 * Clinical administrators require self-service consoles to manage facility access,
 * audit PHI access paths, customizeTerminologies, and track usage against subscription bounds.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Switch } from "../../components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  Users, Key, Settings, ShieldCheck, Heart, Database, 
  Cpu, HardDrive, RefreshCw, Terminal, Eye, EyeOff, Activity,
  Sliders, Calendar, PlusCircle, CheckCircle2, AlertTriangle, Layers,
  Trash2, Mail, FileText, Check, ShieldAlert
} from "lucide-react";

// --- DATA STRUCTURES & DOCS ---

/**
 * @typedef UserProfile
 * @property {string} id - Unique identifier
 * @property {string} name - Practitioner full name
 * @property {string} email - Organization address
 * @property {string} role - System/Org role (e.g. Platform Super Admin)
 * @property {string} status - Active or Suspended status
 */
interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  status: "Active" | "Suspended";
}

/**
 * @typedef Invitation
 * @property {string} id - Unique identifier
 * @property {string} email - Recipient email
 * @property {string} organization - Facility name
 * @property {string} role - Target assigned role
 * @property {string} status - Pending, Accepted, or Expired status
 * @property {string} expiresAt - ISO datetime string
 */
interface Invitation {
  id: string;
  email: string;
  organization: string;
  role: string;
  status: "Pending" | "Accepted" | "Expired";
  expiresAt: string;
}

/**
 * @typedef ApiKeyRecord
 * @property {string} id - Unique identifier
 * @property {string} name - API token label
 * @property {string} prefix - Key prefix (obscured secret key)
 * @property {string} created - Creation ISO date
 * @property {string} status - Active or Revoked state
 */
interface ApiKeyRecord {
  id: string;
  name: string;
  prefix: string;
  created: string;
  status: "Active" | "Revoked";
}

/**
 * @typedef AuditLogRecord
 * @property {string} timestamp - Transaction datetime
 * @property {string} user - Requesting practitioner email or System
 * @property {string} action - Performed operation
 * @property {string} correlationId - Unique transaction request boundary ID
 * @property {string} status - Success or Failure status
 */
interface AuditLogRecord {
  timestamp: string;
  user: string;
  action: string;
  correlationId: string;
  status: "Success" | "Failure";
}

export default function TenantAdminPage() {
  // --- STATE STORES (Simulated Database) ---

  // Tenant General Details
  const [tenantName, setTenantName] = useState("OpenHealth Hospital Network");
  const [tenantStatus, setTenantStatus] = useState<"Active" | "Suspended">("Active");
  const [rawRetentionDays, setRawRetentionDays] = useState(90);
  const [processedRetentionDays, setProcessedRetentionDays] = useState(365);
  const [allowedMimeTypes, setAllowedMimeTypes] = useState(["application/pdf", "image/tiff"]);

  // Organizations & Workspaces
  const [organizations, setOrganizations] = useState([
    { id: "org-1", name: "OpenHealth Main Campus", npi: "1892839201", workspaces: ["Pediatrics", "Internal Medicine"] },
    { id: "org-2", name: "St. Jude Clinic Outpost", npi: "1029302930", workspaces: ["Emergency Care", "Radiology"] }
  ]);
  const [newOrgName, setNewOrgName] = useState("");
  const [newOrgNpi, setNewOrgNpi] = useState("");
  const [newWorkspaceName, setNewWorkspaceName] = useState<{ [orgId: string]: string }>({});

  // Users Roster
  const [users, setUsers] = useState<UserProfile[]>([
    { id: "usr-1", name: "Kalyan Kalwa", email: "kalyan@openhealthagents.org", role: "Platform Super Admin", status: "Active" },
    { id: "usr-2", name: "Arthur Conan Doyle", email: "arthur@openhealthagents.org", role: "Clinician", status: "Active" },
    { id: "usr-3", name: "Jane Smith", email: "jane.smith@openhealthagents.org", role: "Reviewer", status: "Active" },
    { id: "usr-4", name: "Naveen Raj", email: "naveen@openhealthagents.org", role: "Uploader", status: "Active" }
  ]);

  // Invitations
  const [invitations, setInvitations] = useState<Invitation[]>([
    { id: "inv-1", email: "reviewer-candidate@openhealthagents.org", organization: "OpenHealth Main Campus", role: "Reviewer", status: "Pending", expiresAt: "2026-08-10" },
    { id: "inv-2", email: "audit-partner@openhealthagents.org", organization: "St. Jude Clinic Outpost", role: "Auditor", status: "Expired", expiresAt: "2026-07-20" }
  ]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("Reviewer");
  const [inviteOrg, setInviteOrg] = useState("OpenHealth Main Campus");

  // Custom Roles & Permissions
  const [customRoles, setCustomRoles] = useState([
    { name: "Platform Super Admin", parent: "None", permissions: ["*:*"] },
    { name: "Tenant Owner", parent: "None", permissions: ["tenant:write", "organization:write", "user:write", "document:read"] },
    { name: "Clinician", parent: "Viewer", permissions: ["document:read", "validation:write", "fhir:write"] },
    { name: "Reviewer", parent: "Viewer", permissions: ["document:read", "validation:write"] },
    { name: "Auditor", parent: "Viewer", permissions: ["audit:read"] }
  ]);
  const [newRoleName, setNewRoleName] = useState("");
  const [newRoleParent, setNewRoleParent] = useState("Viewer");
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
  const permissionsList = ["document:read", "document:write", "validation:write", "fhir:write", "billing:write", "audit:read", "apikey:manage"];

  // API Keys
  const [apiKeys, setApiKeys] = useState<ApiKeyRecord[]>([
    { id: "key-1", name: "Primary EHR Ingestion Endpoint", prefix: "df_live_8a92...", created: "2026-07-01", status: "Active" },
    { id: "key-2", name: "Fax Gateway Integration", prefix: "df_live_901c...", created: "2026-07-15", status: "Active" }
  ]);
  const [newKeyLabel, setNewKeyLabel] = useState("");

  // Feature Flags
  const [featureFlags, setFeatureFlags] = useState({
    "realtime-ocr-indexing": true,
    "automatic-fhir-export": false,
    "ai_summarization": true,
    "advanced_analytics": false
  });

  // Subscription Tier & Usage Counts
  const [subscriptionTier, setSubscriptionTier] = useState<"FREE" | "PROFESSIONAL" | "ENTERPRISE">("PROFESSIONAL");
  const [usageStats, setUsageStats] = useState({
    storage_mb: 2350.5,
    ocr_pages: 1420,
    api_calls: 34100,
    documents: 780
  });

  // Quota mappings
  const quotas = {
    FREE: { storage: 500, ocr: 100, api: 1000, documents: 50 },
    PROFESSIONAL: { storage: 10000, ocr: 2000, api: 50000, documents: 1000 },
    ENTERPRISE: { storage: 1000000, ocr: 50000, api: 1000000, documents: 20000 }
  };

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState<AuditLogRecord[]>([
    { timestamp: "2026-07-30T06:10:24Z", user: "kalyan@openhealthagents.org", action: "API_KEY_GENERATED", correlationId: "corr-8a92a01", status: "Success" },
    { timestamp: "2026-07-30T05:42:15Z", user: "arthur@openhealthagents.org", action: "USER_INVITATION_SENT", correlationId: "corr-901c10b", status: "Success" },
    { timestamp: "2026-07-30T04:12:00Z", user: "system@openhealthagents.org", action: "LICENSE_TIER_VALIDATED", correlationId: "corr-002f5a0", status: "Success" },
    { timestamp: "2026-07-30T03:15:30Z", user: "jane.smith@openhealthagents.org", action: "RETENTION_POLICY_UPDATED", correlationId: "corr-71b56ce", status: "Success" }
  ]);
  const [auditFilter, setAuditFilter] = useState("");

  // Feedback notifications
  const [bannerText, setBannerText] = useState("");
  const [bannerType, setBannerType] = useState<"success" | "warning" | "error">("success");

  // --- CONTROLLER HANDLERS (Simulated Core Actions) ---

  const triggerBanner = (text: string, type: "success" | "warning" | "error" = "success") => {
    setBannerText(text);
    setBannerType(type);
    setTimeout(() => setBannerText(""), 4000);
  };

  /**
   * Updates general settings for the current active Tenant.
   */
  const handleUpdateGeneralSettings = () => {
    // Audit trace event
    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: "TENANT_SETTINGS_UPDATED",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner("Tenant parameters and retention rules saved successfully.");
  };

  /**
   * Registers a new clinical organization facility.
   */
  const handleAddOrg = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim() || !newOrgNpi.trim()) {
      triggerBanner("NPI and Organization Name must be declared.", "error");
      return;
    }
    const newOrg = {
      id: `org-${organizations.length + 1}`,
      name: newOrgName,
      npi: newOrgNpi,
      workspaces: []
    };
    setOrganizations([...organizations, newOrg]);
    setNewOrgName("");
    setNewOrgNpi("");

    // Log administrative action
    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: "FACILITY_ORGANIZATION_ADDED",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner(`Facility organization "${newOrg.name}" registered successfully.`);
  };

  /**
   * Adds a workspace to a specific organization.
   */
  const handleAddWorkspace = (orgId: string) => {
    const wsName = newWorkspaceName[orgId];
    if (!wsName || !wsName.trim()) return;

    setOrganizations(organizations.map(org => {
      if (org.id === orgId) {
        return { ...org, workspaces: [...org.workspaces, wsName] };
      }
      return org;
    }));

    setNewWorkspaceName({ ...newWorkspaceName, [orgId]: "" });
    triggerBanner(`Workspace "${wsName}" added successfully.`);
  };

  /**
   * Sends user invitations.
   */
  const handleSendInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim()) {
      triggerBanner("Email address is required.", "error");
      return;
    }
    const newInvite: Invitation = {
      id: `inv-${invitations.length + 1}`,
      email: inviteEmail,
      organization: inviteOrg,
      role: inviteRole,
      status: "Pending",
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0]
    };
    setInvitations([...invitations, newInvite]);
    setInviteEmail("");

    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: "USER_INVITATION_SENT",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner(`Invitation sent to ${newInvite.email}.`);
  };

  /**
   * Revokes pending invitation link.
   */
  const handleRevokeInvite = (inviteId: string) => {
    setInvitations(invitations.filter(i => i.id !== inviteId));
    triggerBanner("Invitation link revoked successfully.", "warning");
  };

  /**
   * Toggles active roster status for a clinical user.
   */
  const toggleUserStatus = (userId: string) => {
    setUsers(users.map(u => {
      if (u.id === userId) {
        const nextStatus = u.status === "Active" ? "Suspended" : "Active";
        
        const newAudit: AuditLogRecord = {
          timestamp: new Date().toISOString(),
          user: "kalyan@openhealthagents.org",
          action: nextStatus === "Active" ? "USER_REACTIVATED" : "USER_SUSPENDED",
          correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
          status: "Success"
        };
        setAuditLogs([newAudit, ...auditLogs]);

        return { ...u, status: nextStatus };
      }
      return u;
    }));
    triggerBanner("User security status modified.");
  };

  /**
   * Creates a custom RBAC role with selected capability permissions.
   */
  const handleCreateRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoleName.trim()) return;

    const newRole = {
      name: newRoleName,
      parent: newRoleParent,
      permissions: selectedPermissions.length > 0 ? selectedPermissions : ["Viewer"]
    };
    setCustomRoles([...customRoles, newRole]);
    setNewRoleName("");
    setSelectedPermissions([]);

    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: "RBAC_ROLE_CREATED",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner(`Custom clinical role "${newRole.name}" created.`);
  };

  const handleTogglePermission = (perm: string) => {
    if (selectedPermissions.includes(perm)) {
      setSelectedPermissions(selectedPermissions.filter(p => p !== perm));
    } else {
      setSelectedPermissions([...selectedPermissions, perm]);
    }
  };

  /**
   * Generates programmatic integration secret keys.
   */
  const handleGenerateKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyLabel.trim()) return;

    const newKey: ApiKeyRecord = {
      id: `key-${apiKeys.length + 1}`,
      name: newKeyLabel,
      prefix: `df_live_${Math.random().toString(36).substring(2, 6)}...`,
      created: new Date().toISOString().split("T")[0],
      status: "Active"
    };
    setApiKeys([...apiKeys, newKey]);
    setNewKeyLabel("");

    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: "API_KEY_GENERATED",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner(`API Key "${newKey.name}" generated successfully.`);
  };

  /**
   * Revokes an existing API integration key.
   */
  const handleRevokeKey = (keyId: string) => {
    setApiKeys(apiKeys.map(k => {
      if (k.id === keyId) {
        return { ...k, status: "Revoked" };
      }
      return k;
    }));
    triggerBanner("API security token revoked.", "warning");
  };

  /**
   * Toggle system wide feature flags.
   */
  const handleToggleFlag = (key: keyof typeof featureFlags) => {
    const nextVal = !featureFlags[key];
    setFeatureFlags({ ...featureFlags, [key]: nextVal });
    
    const newAudit: AuditLogRecord = {
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      action: nextVal ? "FEATURE_FLAG_ENABLED" : "FEATURE_FLAG_DISABLED",
      correlationId: `corr-${Math.random().toString(36).substring(2, 9)}`,
      status: "Success"
    };
    setAuditLogs([newAudit, ...auditLogs]);
    triggerBanner(`Feature flag "${key}" toggled.`);
  };

  // Filter audit logs list dynamically based on target action query
  const filteredAuditLogs = auditLogs.filter(log => 
    log.action.toLowerCase().includes(auditFilter.toLowerCase()) ||
    log.user.toLowerCase().includes(auditFilter.toLowerCase())
  );

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER WITH FEEDBACK NOTIFICATION METADATA */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Tenant Administration</h2>
            <p className="text-sm text-muted-foreground">Manage organization layouts, clinical personnel credentials, API scopes, and subscriptions.</p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={tenantStatus === "Active" ? "success" : "error"} className="px-3 py-1">
              Tenant Status: {tenantStatus.toUpperCase()}
            </Badge>
          </div>
        </div>

        {/* Global actions response notification banner */}
        {bannerText && (
          <Alert variant={bannerType === "success" ? "success" : bannerType === "warning" ? "warning" : "error"}>
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">System Alert</AlertTitle>
            <AlertDescription className="text-xs">{bannerText}</AlertDescription>
          </Alert>
        )}

        {/* --- TABS LAYOUT: 6 CORE CONFIGURATION PANELS --- */}
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 max-w-4xl bg-muted/50 rounded-lg p-1">
            <TabsTrigger value="general" className="flex items-center space-x-1.5"><Settings className="h-4 w-4" /> <span>General</span></TabsTrigger>
            <TabsTrigger value="orgs" className="flex items-center space-x-1.5"><Layers className="h-4 w-4" /> <span>Facilities</span></TabsTrigger>
            <TabsTrigger value="roster" className="flex items-center space-x-1.5"><Users className="h-4 w-4" /> <span>Roster & Invites</span></TabsTrigger>
            <TabsTrigger value="rbac" className="flex items-center space-x-1.5"><ShieldCheck className="h-4 w-4" /> <span>Roles & Keys</span></TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center space-x-1.5"><Database className="h-4 w-4" /> <span>Plans & Quotas</span></TabsTrigger>
            <TabsTrigger value="audit" className="flex items-center space-x-1.5"><Activity className="h-4 w-4" /> <span>Audit Trail</span></TabsTrigger>
          </TabsList>

          {/* TAB 1: GENERAL TENANT PROFILE & RETENTION POLICIES */}
          <TabsContent value="general" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Tenant aggregate profile details */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <Settings className="h-4 w-4 text-primary" />
                    <span>Tenant Profile Settings</span>
                  </CardTitle>
                  <CardDescription>Configure primary demographics and operational status indicators.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1">
                    <label htmlFor="tenant-name-input" className="text-xs font-semibold uppercase text-muted-foreground">Tenant Name</label>
                    <Input id="tenant-name-input" value={tenantName} onChange={(e) => setTenantName(e.target.value)} />
                  </div>
                  <div className="flex items-center justify-between p-3 border border-border/60 rounded bg-muted/10 text-xs">
                    <div className="space-y-0.5">
                      <p className="font-bold">Active System Status</p>
                      <p className="text-muted-foreground text-[10px]">Suspended tenants immediately block document OCR pipelines</p>
                    </div>
                    <Switch 
                      id="tenant-status-switch"
                      checked={tenantStatus === "Active"} 
                      onCheckedChange={(checked) => setTenantStatus(checked ? "Active" : "Suspended")} 
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Allowed MIME Format Types</label>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {allowedMimeTypes.map((mime, idx) => (
                        <Badge key={idx} variant="secondary" className="font-mono text-[10px]">{mime}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex justify-end pt-2">
                    <Button id="save-general-settings-btn" onClick={handleUpdateGeneralSettings}>Save Demographics</Button>
                  </div>
                </CardContent>
              </Card>

              {/* Data retention policies configuration */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <HardDrive className="h-4 w-4 text-primary" />
                    <span>Data Retention Policies</span>
                  </CardTitle>
                  <CardDescription>Setup automated storage lifecycles to guarantee HIPAA privacy compliance.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1">
                    <label htmlFor="raw-retention-input" className="text-xs font-semibold uppercase text-muted-foreground">Raw Source PDF Duration (Days)</label>
                    <Input 
                      id="raw-retention-input"
                      type="number" 
                      value={rawRetentionDays} 
                      onChange={(e) => setRawRetentionDays(parseInt(e.target.value) || 0)} 
                    />
                  </div>
                  <div className="space-y-1">
                    <label htmlFor="processed-retention-input" className="text-xs font-semibold uppercase text-muted-foreground">Processed JSON Extraction Duration (Days)</label>
                    <Input 
                      id="processed-retention-input"
                      type="number" 
                      value={processedRetentionDays} 
                      onChange={(e) => setProcessedRetentionDays(parseInt(e.target.value) || 0)} 
                    />
                  </div>
                  <Alert variant="warning" className="py-2.5">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    <AlertDescription className="text-[11px] leading-relaxed">
                      Files exceeding raw retention are permanently pruned from s3 storage buckets.
                    </AlertDescription>
                  </Alert>
                  <div className="flex justify-end">
                    <Button id="save-retention-btn" onClick={handleUpdateGeneralSettings}>Apply Lifecycles</Button>
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 2: FACILITIES & WORKSPACES DIRECTORY */}
          <TabsContent value="orgs" className="space-y-6">
            
            {/* Form: Register new clinic facility */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <PlusCircle className="h-4.5 w-4.5 text-primary" />
                  <span>Register Clinical Facility Organization</span>
                </CardTitle>
                <CardDescription>Onboard clinic divisions and assign physical department workspaces.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <form onSubmit={handleAddOrg} className="grid gap-4 sm:grid-cols-3">
                  <div className="space-y-1">
                    <label htmlFor="org-name-input" className="text-xs font-semibold uppercase text-muted-foreground">Organization Name</label>
                    <Input id="org-name-input" value={newOrgName} onChange={(e) => setNewOrgName(e.target.value)} placeholder="e.g. OpenHealth ER Room" />
                  </div>
                  <div className="space-y-1">
                    <label htmlFor="org-npi-input" className="text-xs font-semibold uppercase text-muted-foreground">NPI Identifier Code</label>
                    <Input id="org-npi-input" value={newOrgNpi} onChange={(e) => setNewOrgNpi(e.target.value)} placeholder="e.g. 1049283921" />
                  </div>
                  <div className="flex items-end">
                    <Button id="register-org-btn" type="submit" className="w-full">Register Facility</Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* List: Organizations, NPI codes, and workspaces lists */}
            <div className="grid gap-6 md:grid-cols-2">
              {organizations.map((org) => (
                <Card key={org.id} className="border border-border/80 bg-background/50 backdrop-blur-md">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-base font-bold text-primary">{org.name}</CardTitle>
                        <CardDescription className="font-mono text-xs">NPI ID: {org.npi}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-2">
                    
                    {/* Workspaces sub list */}
                    <div className="space-y-2">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Workspaces Ingestion Queues</p>
                      <div className="flex flex-wrap gap-1.5">
                        {org.workspaces.length === 0 ? (
                          <span className="text-xs text-muted-foreground italic">No workspaces registered</span>
                        ) : (
                          org.workspaces.map((ws, idx) => (
                            <Badge key={idx} variant="default" className="text-xs">{ws}</Badge>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Add workspace inline control */}
                    <div className="flex gap-2 pt-2 border-t border-border/40">
                      <Input 
                        id={`ws-input-${org.id}`}
                        placeholder="New workspace (e.g. Radiology)..." 
                        value={newWorkspaceName[org.id] || ""}
                        onChange={(e) => setNewWorkspaceName({ ...newWorkspaceName, [org.id]: e.target.value })}
                        className="text-xs h-8"
                      />
                      <Button 
                        id={`ws-add-btn-${org.id}`}
                        size="sm" 
                        onClick={() => handleAddWorkspace(org.id)}
                        className="h-8"
                      >
                        Add
                      </Button>
                    </div>

                  </CardContent>
                </Card>
              ))}
            </div>

          </TabsContent>

          {/* TAB 3: USER ROSTER & INVITATION PIPELINE */}
          <TabsContent value="roster" className="space-y-6">
            
            {/* User credentials roster */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <Users className="h-4.5 w-4.5 text-primary" />
                  <span>Clinical Staff Roster</span>
                </CardTitle>
                <CardDescription>Manage active practitioner directory rosters and login statuses.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Practitioner</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>System Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((usr) => (
                      <TableRow key={usr.id} className="hover:bg-muted/10">
                        <TableCell className="font-semibold text-sm">{usr.name}</TableCell>
                        <TableCell className="font-mono text-xs">{usr.email}</TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">{usr.role}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={usr.status === "Active" ? "success" : "error"} className="text-xs">{usr.status}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button 
                            id={`toggle-user-btn-${usr.id}`}
                            variant="outline" 
                            size="sm" 
                            onClick={() => toggleUserStatus(usr.id)}
                            className="text-xs h-7"
                          >
                            {usr.status === "Active" ? "Suspend" : "Activate"}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Invitations sub-layout */}
            <div className="grid gap-6 md:grid-cols-3">
              
              {/* Form: Invite User */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md md:col-span-1">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <Mail className="h-4.5 w-4.5 text-primary" />
                    <span>Invite Practitioner</span>
                  </CardTitle>
                  <CardDescription>Send secure links to new clinical operators.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <form onSubmit={handleSendInvite} className="space-y-4">
                    <div className="space-y-1">
                      <label htmlFor="invite-email-input" className="text-xs font-semibold uppercase text-muted-foreground">Recipient Email</label>
                      <Input 
                        id="invite-email-input"
                        type="email" 
                        placeholder="practitioner@hospital.org" 
                        value={inviteEmail} 
                        onChange={(e) => setInviteEmail(e.target.value)} 
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold uppercase text-muted-foreground">Assigned Role</label>
                      <select 
                        id="invite-role-select"
                        value={inviteRole} 
                        onChange={(e) => setInviteRole(e.target.value)}
                        className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none"
                      >
                        <option>Platform Super Admin</option>
                        <option>Tenant Owner</option>
                        <option>Clinician</option>
                        <option>Reviewer</option>
                        <option>Auditor</option>
                      </select>
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold uppercase text-muted-foreground">Target Organization</label>
                      <select 
                        id="invite-org-select"
                        value={inviteOrg} 
                        onChange={(e) => setInviteOrg(e.target.value)}
                        className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none"
                      >
                        {organizations.map(org => (
                          <option key={org.id}>{org.name}</option>
                        ))}
                      </select>
                    </div>
                    <Button id="send-invite-btn" type="submit" className="w-full">Dispatch Invite Link</Button>
                  </form>
                </CardContent>
              </Card>

              {/* List: Pending Invitations */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Pending Invitations</CardTitle>
                  <CardDescription>Verify link statuses, expirations, and revoke keys.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Invited Operator</TableHead>
                        <TableHead>Facility</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {invitations.map((inv) => (
                        <TableRow key={inv.id} className="hover:bg-muted/10">
                          <TableCell className="font-semibold text-xs leading-none space-y-1">
                            <p>{inv.email}</p>
                            <p className="text-[10px] text-muted-foreground font-mono">Expires: {inv.expiresAt}</p>
                          </TableCell>
                          <TableCell className="text-xs">{inv.organization}</TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-[10px]">{inv.role}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={inv.status === "Pending" ? "warning" : "error"} className="text-[10px]">{inv.status}</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {inv.status === "Pending" && (
                              <Button 
                                id={`revoke-invite-btn-${inv.id}`}
                                variant="ghost" 
                                size="sm" 
                                onClick={() => handleRevokeInvite(inv.id)}
                                className="text-xs text-error hover:text-error hover:bg-error/10 h-7"
                              >
                                Revoke
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

            </div>

          </TabsContent>

          {/* TAB 4: RBAC ROLES & API KEYS */}
          <TabsContent value="rbac" className="space-y-6">
            
            {/* Roles and Custom Creation forms */}
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Custom Roles registration */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <ShieldCheck className="h-4.5 w-4.5 text-primary" />
                    <span>Create Custom Clinical Role</span>
                  </CardTitle>
                  <CardDescription>Onboard specialized security roles containing targeted capabilities.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <form onSubmit={handleCreateRole} className="space-y-4">
                    <div className="space-y-1">
                      <label htmlFor="custom-role-input" className="text-xs font-semibold uppercase text-muted-foreground">Custom Role Name</label>
                      <Input 
                        id="custom-role-input"
                        placeholder="e.g. Clinical Terminology Manager" 
                        value={newRoleName} 
                        onChange={(e) => setNewRoleName(e.target.value)} 
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold uppercase text-muted-foreground">Inherit Capabilities from Role</label>
                      <select 
                        id="parent-role-select"
                        value={newRoleParent} 
                        onChange={(e) => setNewRoleParent(e.target.value)}
                        className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none"
                      >
                        <option>None</option>
                        <option>Viewer</option>
                        <option>Reviewer</option>
                        <option>Clinician</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold uppercase text-muted-foreground">Capability Permissions Mapping</label>
                      <div className="grid grid-cols-2 gap-2 pt-1">
                        {permissionsList.map((perm) => (
                          <div key={perm} className="flex items-center space-x-2">
                            <input 
                              id={`perm-checkbox-${perm}`}
                              type="checkbox" 
                              checked={selectedPermissions.includes(perm)}
                              onChange={() => handleTogglePermission(perm)}
                              className="rounded border-border bg-background text-primary"
                            />
                            <span className="text-xs font-mono text-muted-foreground">{perm}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <Button id="create-custom-role-btn" type="submit">Create Custom Role</Button>
                    </div>
                  </form>
                </CardContent>
              </Card>

              {/* Roles matrix listing */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Standard Roles & Capabilities</CardTitle>
                  <CardDescription>View permission matrices and hierarchy inheritance chains.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Role Title</TableHead>
                        <TableHead>Inheritance Parent</TableHead>
                        <TableHead>Permissions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {customRoles.map((role, idx) => (
                        <TableRow key={idx} className="hover:bg-muted/10">
                          <TableCell className="font-semibold text-xs text-primary">{role.name}</TableCell>
                          <TableCell className="text-xs font-mono text-muted-foreground">{role.parent}</TableCell>
                          <TableCell className="flex flex-wrap gap-1 max-w-[200px]">
                            {role.permissions.map((p, pIdx) => (
                              <Badge key={pIdx} variant="secondary" className="font-mono text-[9px] px-1 py-0">{p}</Badge>
                            ))}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

            </div>

            {/* API access tokens */}
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Form: Generate Key */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <Key className="h-4.5 w-4.5 text-primary" />
                    <span>Generate API Ingestion Key</span>
                  </CardTitle>
                  <CardDescription>Onboard programmatic integrations for digital faxes intake.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <form onSubmit={handleGenerateKey} className="space-y-4">
                    <div className="space-y-1">
                      <label htmlFor="api-key-label-input" className="text-xs font-semibold uppercase text-muted-foreground">API Token Label</label>
                      <Input 
                        id="api-key-label-input"
                        placeholder="e.g. Medplum US Core Ingress" 
                        value={newKeyLabel} 
                        onChange={(e) => setNewKeyLabel(e.target.value)} 
                      />
                    </div>
                    <div className="flex items-center justify-between p-3 border border-border/60 rounded bg-muted/10 text-xs">
                      <div className="space-y-0.5">
                        <p className="font-bold">Set Expiration Window</p>
                        <p className="text-muted-foreground text-[10px]">Deactivates key automatically after 90 days</p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex justify-end">
                      <Button id="generate-key-btn" type="submit">Generate Integration Key</Button>
                    </div>
                  </form>
                </CardContent>
              </Card>

              {/* List: API Keys */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">API Ingress Access Keys</CardTitle>
                  <CardDescription>Manage active programmatic gateways keys.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Token Label</TableHead>
                        <TableHead>Obscured Secret</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {apiKeys.map((key) => (
                        <TableRow key={key.id} className="hover:bg-muted/10">
                          <TableCell className="font-semibold text-xs leading-none space-y-1">
                            <p>{key.name}</p>
                            <p className="text-[9px] text-muted-foreground font-mono">Issued: {key.created}</p>
                          </TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">{key.prefix}</TableCell>
                          <TableCell>
                            <Badge variant={key.status === "Active" ? "success" : "secondary"} className="text-[10px]">{key.status}</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {key.status === "Active" && (
                              <Button 
                                id={`revoke-key-btn-${key.id}`}
                                variant="ghost" 
                                size="sm" 
                                onClick={() => handleRevokeKey(key.id)}
                                className="text-xs text-error hover:text-error hover:bg-error/10 h-7"
                              >
                                Revoke
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

            </div>

          </TabsContent>

          {/* TAB 5: PLANS & QUOTAS METERS */}
          <TabsContent value="billing" className="space-y-6">
            
            {/* Top overview of plan tier */}
            <div className="grid gap-6 md:grid-cols-3">
              
              {/* Plan select card: Free */}
              <Card className={`border ${subscriptionTier === "FREE" ? "border-primary bg-primary/5" : "border-border/80 bg-background/50"} backdrop-blur-md cursor-pointer hover:border-primary/80 transition-all`} onClick={() => setSubscriptionTier("FREE")}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base font-bold">Free Plan Tier</CardTitle>
                    {subscriptionTier === "FREE" && <Badge variant="success" className="text-xs">Active Plan</Badge>}
                  </div>
                  <CardDescription className="text-lg font-bold pt-1">$0.00 <span className="text-xs font-normal text-muted-foreground">/ month</span></CardDescription>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1 pt-1 leading-relaxed">
                  <p>• 500 MB storage quota</p>
                  <p>• 100 OCR processed pages</p>
                  <p>• 1,000 monthly API calls</p>
                  <p>• 50 total ingested documents</p>
                </CardContent>
              </Card>

              {/* Plan select card: Pro */}
              <Card className={`border ${subscriptionTier === "PROFESSIONAL" ? "border-primary bg-primary/5" : "border-border/80 bg-background/50"} backdrop-blur-md cursor-pointer hover:border-primary/80 transition-all`} onClick={() => setSubscriptionTier("PROFESSIONAL")}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base font-bold">Professional Tier</CardTitle>
                    {subscriptionTier === "PROFESSIONAL" && <Badge variant="success" className="text-xs">Active Plan</Badge>}
                  </div>
                  <CardDescription className="text-lg font-bold pt-1">$149.00 <span className="text-xs font-normal text-muted-foreground">/ month</span></CardDescription>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1 pt-1 leading-relaxed">
                  <p>• 10,000 MB storage quota</p>
                  <p>• 2,000 OCR processed pages</p>
                  <p>• 50,000 monthly API calls</p>
                  <p>• 1,000 total ingested documents</p>
                </CardContent>
              </Card>

              {/* Plan select card: Enterprise */}
              <Card className={`border ${subscriptionTier === "ENTERPRISE" ? "border-primary bg-primary/5" : "border-border/80 bg-background/50"} backdrop-blur-md cursor-pointer hover:border-primary/80 transition-all`} onClick={() => setSubscriptionTier("ENTERPRISE")}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base font-bold">Enterprise System</CardTitle>
                    {subscriptionTier === "ENTERPRISE" && <Badge variant="success" className="text-xs">Active Plan</Badge>}
                  </div>
                  <CardDescription className="text-lg font-bold pt-1">Custom <span className="text-xs font-normal text-muted-foreground">/ contract</span></CardDescription>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1 pt-1 leading-relaxed">
                  <p>• 1,000,000 MB storage quota</p>
                  <p>• 50,000 OCR processed pages</p>
                  <p>• 1,000,000 monthly API calls</p>
                  <p>• 20,000 total ingested documents</p>
                </CardContent>
              </Card>

            </div>

            {/* Quota consumption progress bars */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <Sliders className="h-4.5 w-4.5 text-primary" />
                  <span>SaaS Subscription Quotas Usage</span>
                </CardTitle>
                <CardDescription>Track real-time tenant compute allocations.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-2">
                
                {/* 1. Storage quota meter */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold">Total Storage Quota</span>
                    <span className="font-mono text-muted-foreground">
                      {usageStats.storage_mb} MB / {quotas[subscriptionTier].storage} MB
                    </span>
                  </div>
                  <div className="h-2.5 w-full bg-muted border border-border/40 rounded-full overflow-hidden">
                    <div 
                      id="storage-quota-bar"
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (usageStats.storage_mb / quotas[subscriptionTier].storage) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* 2. OCR pages quota meter */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold">OCR Page Credits</span>
                    <span className="font-mono text-muted-foreground">
                      {usageStats.ocr_pages} pages / {quotas[subscriptionTier].ocr} pages
                    </span>
                  </div>
                  <div className="h-2.5 w-full bg-muted border border-border/40 rounded-full overflow-hidden">
                    <div 
                      id="ocr-quota-bar"
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (usageStats.ocr_pages / quotas[subscriptionTier].ocr) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* 3. API calls quota meter */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold">Programmatic API Requests</span>
                    <span className="font-mono text-muted-foreground">
                      {usageStats.api_calls} calls / {quotas[subscriptionTier].api} calls
                    </span>
                  </div>
                  <div className="h-2.5 w-full bg-muted border border-border/40 rounded-full overflow-hidden">
                    <div 
                      id="api-quota-bar"
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (usageStats.api_calls / quotas[subscriptionTier].api) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* 4. Ingest documents quota meter */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold">Monthly Inbound Documents</span>
                    <span className="font-mono text-muted-foreground">
                      {usageStats.documents} faxes / {quotas[subscriptionTier].documents} documents
                    </span>
                  </div>
                  <div className="h-2.5 w-full bg-muted border border-border/40 rounded-full overflow-hidden">
                    <div 
                      id="documents-quota-bar"
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (usageStats.documents / quotas[subscriptionTier].documents) * 100)}%` }}
                    />
                  </div>
                </div>

              </CardContent>
            </Card>

            {/* Feature Flags Settings Gates (Coupled with current active tier) */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <ShieldAlert className="h-4.5 w-4.5 text-primary" />
                  <span>Feature Flags Toggles</span>
                </CardTitle>
                <CardDescription>Enable custom features and beta gates dynamically.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2 pt-2 text-xs">
                
                <div className="flex items-start justify-between p-3 border border-border/60 rounded bg-muted/10">
                  <div className="space-y-1 mr-4">
                    <p className="font-bold font-mono text-primary">realtime-ocr-indexing</p>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">Submit baseline OCR files immediately on NATS ingest queues.</p>
                  </div>
                  <Switch 
                    id="flag-realtime-ocr-switch"
                    checked={featureFlags["realtime-ocr-indexing"]} 
                    onCheckedChange={() => handleToggleFlag("realtime-ocr-indexing")} 
                  />
                </div>

                <div className="flex items-start justify-between p-3 border border-border/60 rounded bg-muted/10">
                  <div className="space-y-1 mr-4">
                    <p className="font-bold font-mono text-primary">automatic-fhir-export</p>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">Directly dispatch parsed US Core FHIR documents to EHR endpoints.</p>
                  </div>
                  <Switch 
                    id="flag-fhir-export-switch"
                    checked={featureFlags["automatic-fhir-export"]} 
                    onCheckedChange={() => handleToggleFlag("automatic-fhir-export")} 
                  />
                </div>

                <div className="flex items-start justify-between p-3 border border-border/60 rounded bg-muted/10">
                  <div className="space-y-1 mr-4">
                    <div className="flex items-center space-x-1.5">
                      <p className="font-bold font-mono text-primary">ai_summarization</p>
                      <Badge variant="warning" className="text-[9px] px-1 py-0 shrink-0">Beta</Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">Opt-in to experimental OpenAI/Gemini semantic summarizations.</p>
                  </div>
                  <Switch 
                    id="flag-ai-summarization-switch"
                    checked={featureFlags["ai_summarization"]} 
                    onCheckedChange={() => handleToggleFlag("ai_summarization")} 
                  />
                </div>

                <div className={`flex items-start justify-between p-3 border rounded ${subscriptionTier === "ENTERPRISE" ? "border-border/60 bg-muted/10" : "border-border/30 bg-muted/5 opacity-60"}`}>
                  <div className="space-y-1 mr-4">
                    <div className="flex items-center space-x-1.5">
                      <p className="font-bold font-mono text-primary">advanced_analytics</p>
                      <Badge variant="secondary" className="text-[9px] px-1 py-0 shrink-0">Enterprise Only</Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">Unlock high-volume diagnostic dashboard metrics tracking.</p>
                  </div>
                  <Switch 
                    id="flag-advanced-analytics-switch"
                    checked={featureFlags["advanced_analytics"]} 
                    disabled={subscriptionTier !== "ENTERPRISE"}
                    onCheckedChange={() => handleToggleFlag("advanced_analytics")} 
                  />
                </div>

              </CardContent>
            </Card>

          </TabsContent>

          {/* TAB 6: COMPLIANCE AUDIT TRAILS */}
          <TabsContent value="audit" className="space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
                  <div>
                    <CardTitle className="text-lg font-bold flex items-center space-x-2">
                      <Terminal className="h-4.5 w-4.5 text-primary" />
                      <span>Security Audit Logs</span>
                    </CardTitle>
                    <CardDescription>Chronological compliance trail of all administrative updates.</CardDescription>
                  </div>
                  <div className="w-full max-w-xs">
                    <Input 
                      id="audit-search-input"
                      placeholder="Filter by user email or action type..." 
                      value={auditFilter}
                      onChange={(e) => setAuditFilter(e.target.value)}
                      className="text-xs"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User Profile</TableHead>
                      <TableHead>Action Event</TableHead>
                      <TableHead>Correlation ID</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredAuditLogs.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center text-muted-foreground py-6 italic">
                          No audit event records match your filter criteria
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredAuditLogs.map((log, idx) => (
                        <TableRow key={idx} className="hover:bg-muted/10">
                          <TableCell className="font-mono text-xs text-muted-foreground">{log.timestamp}</TableCell>
                          <TableCell className="font-semibold text-xs">{log.user}</TableCell>
                          <TableCell className="font-mono text-xs text-primary font-bold">{log.action}</TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">{log.correlationId}</TableCell>
                          <TableCell>
                            <Badge variant={log.status === "Success" ? "success" : "error"} className="text-[10px]">{log.status}</Badge>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

      </div>
    </AppShell>
  );
}
