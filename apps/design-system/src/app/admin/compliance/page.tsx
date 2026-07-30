/**
 * @file page.tsx
 * @description Compliance, Policy, and Audit Administration Console.
 * 
 * Provides policy configurations, patient consents directory, legal hold toggles,
 * right-to-deletion purges, audit trails timelines, and retention schedules.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Badge } from "../../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { Switch } from "../../../components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../../components/ui/tabs";
import { 
  ShieldAlert, Activity, FileText, Layers, CheckSquare,
  Search, ArrowRight, Play, Loader2, Download, Upload,
  Layers2, CheckCircle, ShieldCheck, History, Database, Lock, Scale
} from "lucide-react";

// --- TYPES ---
interface PatientConsentRecord {
  id: string;
  scope: string;
  signedDate: string;
  optIn: boolean;
  legalHold: boolean;
}

interface AuditLog {
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  justification: string;
}

export default function ComplianceAdministrationPage() {
  // --- STATE STORES ---
  const [activeTab, setActiveTab] = useState("policies");
  const [deletePatientId, setDeletePatientId] = useState("");
  const [deleteJustification, setDeleteJustification] = useState("");
  const [deletionStatus, setDeletionStatus] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  
  const [isDeleting, setIsDeleting] = useState(false);

  // Enabled Regulations
  const [hipaaActive, setHipaaActive] = useState(true);
  const [gdprActive, setGdprActive] = useState(true);
  const [pipedaActive, setPipedaActive] = useState(false);
  const [apaActive, setApaActive] = useState(false);

  // Consent Records Catalog
  const [consents, setConsents] = useState<PatientConsentRecord[]>([
    { id: "pat-101", scope: "CLINICAL_SHARE", signedDate: "2026-07-28", optIn: true, legalHold: true },
    { id: "pat-102", scope: "CLINICAL_SHARE", signedDate: "2026-07-29", optIn: true, legalHold: false },
    { id: "pat-103", scope: "MARKETING", signedDate: "2026-07-30", optIn: false, legalHold: false }
  ]);

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { timestamp: "2026-07-30T20:00:00Z", user: "Dr. Smith", action: "READ", resource: "Patient/pat-101", justification: "Routine clinical encounter review" },
    { timestamp: "2026-07-30T19:45:00Z", user: "nurse-jane", action: "WRITE", resource: "Observation/obs-999", justification: "Updated Fasting Blood Glucose measurement" },
    { timestamp: "2026-07-30T18:30:00Z", user: "system-agent", action: "EXPORT", resource: "Patient/pat-102", justification: "GDPR Right to Export bundle download" }
  ]);

  // --- HANDLERS ---

  /**
   * Toggles legal hold active state on a patient account.
   */
  const handleToggleLegalHold = (patientId: string, active: boolean) => {
    setConsents(prev => prev.map(c => {
      if (c.id === patientId) {
        return { ...c, legalHold: active };
      }
      return c;
    }));

    // Log the audit event
    const newLog: AuditLog = {
      timestamp: new Date().toISOString(),
      user: "compliance-officer",
      action: active ? "LOCK_HOLD" : "UNLOCK_HOLD",
      resource: `Patient/${patientId}`,
      justification: active ? "Added legal hold restriction" : "Released legal hold lock"
    };
    setAuditLogs(prev => [newLog, ...prev]);
  };

  /**
   * Submits a patient data deletion request.
   */
  const handleDeleteRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!deletePatientId.trim() || !deleteJustification.trim()) return;

    setIsDeleting(true);
    setDeletionStatus(null);

    setTimeout(() => {
      setIsDeleting(false);
      const target = consents.find(c => c.id === deletePatientId.trim());
      
      if (target && target.legalHold) {
        setDeletionStatus({
          success: false,
          message: `Patient ${deletePatientId} has an active legal hold. Deletion blocked.`
        });
      } else {
        // Successful deletion
        setDeletionStatus({
          success: true,
          message: `Patient ${deletePatientId} data purged successfully. PURGE logged in audit.`
        });

        // Add to audit log
        const purgeLog: AuditLog = {
          timestamp: new Date().toISOString(),
          user: "compliance-officer",
          action: "PURGE",
          resource: `Patient/${deletePatientId}`,
          justification: deleteJustification
        };
        setAuditLogs(prev => [purgeLog, ...prev]);
        setDeletePatientId("");
        setDeleteJustification("");
      }
    }, 600);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Compliance & Auditing Control</h2>
          <p className="text-sm text-muted-foreground">Manage active privacy regulations, patient consent policies, legal holds, and data deletion workflows.</p>
        </div>

        {/* METRICS ROW */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Regulations</span>
              <Scale className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">HIPAA, GDPR</div>
              <p className="text-[10px] text-muted-foreground">PIPEDA and APA suspended</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Legal Holds</span>
              <Lock className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">1 Patient</div>
              <p className="text-[10px] text-muted-foreground">Deletion locked on matching resource IDs</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Scheduled Purges</span>
              <Database className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">48 Files</div>
              <p className="text-[10px] text-muted-foreground">Expiration rules trigger in 12 days</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Audit Log Trail</span>
              <History className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4,821 Logs</div>
              <p className="text-[10px] text-muted-foreground">Conforms to SOC2 and HIPAA audit standards</p>
            </CardContent>
          </Card>
        </div>

        {/* TABS LIST */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-muted p-1 w-full justify-start md:w-auto">
            <TabsTrigger value="policies" className="text-xs px-3 py-1.5" id="tab-policies">Policy Editor</TabsTrigger>
            <TabsTrigger value="consents" className="text-xs px-3 py-1.5" id="tab-consents">Consent Registry</TabsTrigger>
            <TabsTrigger value="deletion" className="text-xs px-3 py-1.5" id="tab-deletion">Right to Deletion</TabsTrigger>
            <TabsTrigger value="audit" className="text-xs px-3 py-1.5" id="tab-audit">Audit Trails</TabsTrigger>
            <TabsTrigger value="retention" className="text-xs px-3 py-1.5" id="tab-retention">Retention Dashboard</TabsTrigger>
          </TabsList>

          {/* TAB 1: POLICY EDITOR */}
          <TabsContent value="policies" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Compliance Regulation configuration</CardTitle>
                <CardDescription>Activate global or regional privacy rulesets affecting patient data consent scopes.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-2">
                <div className="grid gap-6 md:grid-cols-4">
                  <div className="border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-40">
                    <div className="space-y-1">
                      <span className="font-bold text-sm text-foreground block">HIPAA (US Health)</span>
                      <p className="text-[10px] text-muted-foreground">Enforces Business Associate Agreements, clinical audits, and encrypted PHI storage.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Status</span>
                      <Switch id="toggle-hipaa" checked={hipaaActive} onCheckedChange={setHipaaActive} />
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-40">
                    <div className="space-y-1">
                      <span className="font-bold text-sm text-foreground block">GDPR (EU Privacy)</span>
                      <p className="text-[10px] text-muted-foreground">Enforces Right to Deletion, right to data portability/export, and clear opt-in consents.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Status</span>
                      <Switch id="toggle-gdpr" checked={gdprActive} onCheckedChange={setGdprActive} />
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-40">
                    <div className="space-y-1">
                      <span className="font-bold text-sm text-foreground block">PIPEDA (Canada)</span>
                      <p className="text-[10px] text-muted-foreground">Enforces Canadian personal information protection and electronic documents regulation.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Status</span>
                      <Switch id="toggle-pipeda" checked={pipedaActive} onCheckedChange={setPipedaActive} />
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-40">
                    <div className="space-y-1">
                      <span className="font-bold text-sm text-foreground block">APA (Australia Privacy)</span>
                      <p className="text-[10px] text-muted-foreground">Enforces Australian Privacy Principles constraints and cross-border data transfer rules.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Status</span>
                      <Switch id="toggle-apa" checked={apaActive} onCheckedChange={setApaActive} />
                    </div>
                  </div>
                </div>

                {/* Retention Rules configuration */}
                <div className="space-y-3">
                  <span className="font-bold text-sm text-foreground block">Resource Retention Schedules</span>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Resource Type</TableHead>
                        <TableHead>Retention Days</TableHead>
                        <TableHead>Action on Expiry</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell className="font-mono text-xs text-foreground">Patient Accounts</TableCell>
                        <TableCell><Input className="h-8 text-xs w-28 font-mono" defaultValue="2555" type="number" /></TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">PURGE</Badge>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-mono text-xs text-foreground">Observations & Labs</TableCell>
                        <TableCell><Input className="h-8 text-xs w-28 font-mono" defaultValue="1825" type="number" /></TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">ARCHIVE</Badge>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: CONSENT REGISTRY */}
          <TabsContent value="consents" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Patient Consent & Legal Hold registry</CardTitle>
                <CardDescription>Verify patient clinical share scopes and lock deletions using legal holds.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Patient ID</TableHead>
                      <TableHead>Consent Scope</TableHead>
                      <TableHead>Signed Date</TableHead>
                      <TableHead>Opt-In Status</TableHead>
                      <TableHead>Legal Hold Lock</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {consents.map((c, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-mono text-xs font-bold text-foreground">{c.id}</TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">{c.scope}</TableCell>
                        <TableCell className="text-xs text-foreground">{c.signedDate}</TableCell>
                        <TableCell>
                          <Badge variant={c.optIn ? "success" : "secondary"} className="text-[10px]">
                            {c.optIn ? "OPT_IN" : "OPT_OUT"}
                          </Badge>
                        </TableCell>
                        <TableCell className="flex items-center space-x-3">
                          <Switch 
                            id={`toggle-hold-${c.id}`} 
                            checked={c.legalHold} 
                            onCheckedChange={(checked) => handleToggleLegalHold(c.id, checked)}
                          />
                          <span className="text-[11px] font-semibold text-muted-foreground flex items-center space-x-1">
                            {c.legalHold && <Lock className="h-3 w-3 text-warning shrink-0" />}
                            <span>{c.legalHold ? "Active Lock" : "Unlocked"}</span>
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 3: RIGHT TO DELETION */}
          <TabsContent value="deletion" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-3">
              
              <Card className="lg:col-span-2 border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Right to Deletion request console</CardTitle>
                  <CardDescription>Submit GDPR Right to Deletion requests. Validates active legal holds prior to purging.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <form onSubmit={handleDeleteRequest} className="space-y-4">
                    <div className="space-y-1">
                      <label htmlFor="delete-patient-input" className="block text-xs font-semibold text-muted-foreground">Patient ID</label>
                      <Input 
                        id="delete-patient-input"
                        placeholder="Enter Patient ID (e.g. pat-101)" 
                        value={deletePatientId}
                        onChange={(e) => setDeletePatientId(e.target.value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="delete-justification-input" className="block text-xs font-semibold text-muted-foreground">Compliance justification / request details</label>
                      <textarea 
                        id="delete-justification-input"
                        placeholder="State legal justification for this deletion request..." 
                        value={deleteJustification}
                        onChange={(e) => setDeleteJustification(e.target.value)}
                        className="w-full h-24 p-3 rounded-md border border-border bg-muted/20 text-xs focus:outline-none"
                      />
                    </div>
                    <Button 
                      id="delete-submit-btn"
                      type="submit" 
                      disabled={isDeleting}
                      className="bg-error hover:bg-error/80 text-white text-xs flex items-center space-x-1.5 h-10 px-5"
                    >
                      {isDeleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldAlert className="h-4 w-4" />}
                      <span>Execute Purge Deletion</span>
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Feedback status pane */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-base font-bold">Execution Status diagnostics</CardTitle>
                  <CardDescription>Deletion outcome logs.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2 space-y-4">
                  {deletionStatus === null ? (
                    <div className="text-center py-16 text-muted-foreground space-y-2">
                      <ShieldCheck className="h-8 w-8 text-muted-foreground/40 mx-auto" />
                      <p className="text-xs">Submit deletion request to trigger compliance safety validations.</p>
                    </div>
                  ) : deletionStatus.success ? (
                    <Alert variant="success">
                      <CheckCircle className="h-4 w-4" />
                      <AlertTitle className="text-xs">Purge Succeeded</AlertTitle>
                      <AlertDescription className="text-[11px]">
                        {deletionStatus.message}
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Alert variant="error">
                      <ShieldAlert className="h-4 w-4" />
                      <AlertTitle className="text-xs">Purge BLOCKED</AlertTitle>
                      <AlertDescription className="text-[11px]">
                        {deletionStatus.message}
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 4: AUDIT TRAIL LOGS */}
          <TabsContent value="audit" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Access Audit timeline logs</CardTitle>
                <CardDescription>SOC2-compliant clinical access record log timelines.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User / Agent</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Resource ID</TableHead>
                      <TableHead>Justification Reason</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditLogs.map((log, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-mono text-[10px] text-muted-foreground">{log.timestamp}</TableCell>
                        <TableCell className="text-xs font-bold text-foreground">{log.user}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={log.action === "PURGE" ? "error" : log.action === "LOCK_HOLD" ? "warning" : "secondary"} 
                            className="text-[10px]"
                          >
                            {log.action}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs">{log.resource}</TableCell>
                        <TableCell className="text-xs text-foreground">{log.justification}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 5: RETENTION DASHBOARD */}
          <TabsContent value="retention" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Storage Expiration Countdown</CardTitle>
                <CardDescription>Monitor resource storage ages and scheduled purges timelines.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="border rounded-lg p-4 bg-background/30 space-y-2">
                    <span className="font-bold text-xs text-muted-foreground block uppercase">Clinical Documents</span>
                    <div className="text-2xl font-bold text-foreground">1,280 files</div>
                    <div className="w-full bg-muted h-2 rounded overflow-hidden">
                      <div className="bg-primary h-full w-[45%]" />
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-muted-foreground pt-1">
                      <span>45% of retention elapsed</span>
                      <span>1,024 days left</span>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 space-y-2">
                    <span className="font-bold text-xs text-muted-foreground block uppercase">Observation Records</span>
                    <div className="text-2xl font-bold text-foreground">14,890 entries</div>
                    <div className="w-full bg-muted h-2 rounded overflow-hidden">
                      <div className="bg-warning h-full w-[85%]" />
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-muted-foreground pt-1">
                      <span className="text-warning">85% of retention elapsed</span>
                      <span>244 days left</span>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 space-y-2">
                    <span className="font-bold text-xs text-muted-foreground block uppercase">Archived Backups</span>
                    <div className="text-2xl font-bold text-foreground">412 backups</div>
                    <div className="w-full bg-muted h-2 rounded overflow-hidden">
                      <div className="bg-success h-full w-[15%]" />
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-muted-foreground pt-1">
                      <span>15% of retention elapsed</span>
                      <span>1,800 days left</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>

      </div>
    </AppShell>
  );
}
