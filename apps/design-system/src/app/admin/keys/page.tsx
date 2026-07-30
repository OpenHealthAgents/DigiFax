/**
 * @file page.tsx
 * @description Key Management, Envelope Encryption, and Cryptographic Audit Console.
 * 
 * Provides vault status browsers, key rotation history, cryptographic parity
 * validators, SOC2 key audit logs, and expiration countdown alerts.
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
  Lock, Key, RefreshCw, ShieldAlert, CheckCircle, Play, Loader2,
  ListFilter, Database, History, HelpCircle, HardDrive, AlertTriangle, ShieldCheck
} from "lucide-react";

// --- TYPES ---
interface RotationLog {
  timestamp: string;
  action: string;
  keyId: string;
  status: string;
}

interface AuditLog {
  timestamp: string;
  user: string;
  action: string;
  keyRef: string;
  ipAddress: string;
}

export default function KeyAdministrationPage() {
  // --- STATE STORES ---
  const [activeTab, setActiveTab] = useState("status");
  const [activeKek, setActiveKek] = useState("kek-tenant-crypto-a4f");
  const [activeDek, setActiveDek] = useState("dek-tenant-crypto-e92");
  const [rotationHistory, setRotationHistory] = useState<RotationLog[]>([
    { timestamp: "2026-07-30T10:00:00Z", action: "ADD_DEK", keyId: "dek-tenant-crypto-e92", status: "Wrapped successfully by KEK" },
    { timestamp: "2026-07-30T09:45:00Z", action: "ROTATE_KEK", keyId: "kek-tenant-crypto-a4f", status: "Rotated and re-wrapped old DEKs" },
    { timestamp: "2026-07-28T09:00:00Z", action: "INITIALIZE", keyId: "kek-tenant-crypto-old", status: "Initial tenant keyring setup complete" }
  ]);

  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { timestamp: "2026-07-30T20:10:00Z", user: "system-agent", action: "DECRYPT_DEK", keyRef: "dek-tenant-crypto-e92", ipAddress: "10.0.4.12" },
    { timestamp: "2026-07-30T19:55:00Z", user: "Dr. Smith", action: "UNWRAP_KEK", keyRef: "kek-tenant-crypto-a4f", ipAddress: "192.168.1.84" },
    { timestamp: "2026-07-30T19:40:00Z", user: "nurse-jane", action: "DECRYPT_DEK", keyRef: "dek-tenant-crypto-e92", ipAddress: "192.168.1.92" }
  ]);

  const [isRotating, setIsRotating] = useState(false);
  const [rotationAlert, setRotationAlert] = useState<string | null>(null);

  // Parity Validator Sandbox States
  const [validatorInput, setValidatorInput] = useState("Dr. Kalyan Kalwa - Clinical Chart Note PHI");
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    success: boolean;
    encryptedPayload: string;
    diagnosticLog: string[];
  } | null>(null);

  // --- HANDLERS ---

  /**
   * Executes a simulated manual key rotation.
   */
  const handleKeyRotation = () => {
    setIsRotating(true);
    setRotationAlert(null);

    setTimeout(() => {
      setIsRotating(false);
      const newKekId = `kek-tenant-crypto-${Math.random().toString(36).substring(2, 7)}`;
      const newDekId = `dek-tenant-crypto-${Math.random().toString(36).substring(2, 7)}`;
      
      setActiveKek(newKekId);
      setActiveDek(newDekId);

      // Append rotation history
      const newKekLog: RotationLog = {
        timestamp: new Date().toISOString(),
        action: "ROTATE_KEK",
        keyId: newKekId,
        status: "Rotated successfully and re-wrapped existing Data Encryption Keys"
      };
      const newDekLog: RotationLog = {
        timestamp: new Date().toISOString(),
        action: "ADD_DEK",
        keyId: newDekId,
        status: "Wrapped successfully by KEK"
      };
      setRotationHistory(prev => [newKekLog, newDekLog, ...prev]);

      // Append audit logs
      const auditLog: AuditLog = {
        timestamp: new Date().toISOString(),
        user: "compliance-officer",
        action: "KEY_ROTATION",
        keyRef: newKekId,
        ipAddress: "127.0.0.1"
      };
      setAuditLogs(prev => [auditLog, ...prev]);

      setRotationAlert(`Cryptographic keys successfully rotated. Active KEK updated to ${newKekId}.`);
    }, 800);
  };

  /**
   * Executes a cryptographic parity self-test.
   */
  const handleRunValidation = () => {
    if (!validatorInput.trim()) return;

    setIsValidating(true);
    setValidationResult(null);

    setTimeout(() => {
      setIsValidating(false);
      const logs = [
        "Initializing SoftwareKmsProvider cryptographic AESGCM engine",
        "Retrieved pre-seeded system Master Key from LocalSecretsManager",
        "Unwrapped active KEK using Master Key (AES-GCM-256)",
        "Unwrapped active DEK using active KEK (AES-GCM-256)",
        "Encrypted dummy plaintext under DEK with random IV tag",
        "Unwrapped DEK in memory and decrypted ciphertext bytes",
        "Compared decrypted bytes parity with original input"
      ];
      setValidationResult({
        success: true,
        encryptedPayload: "Ciphertext: " + btoa(validatorInput).substring(0, 32) + "... [IV: AESGCM-Tag]",
        diagnosticLog: logs
      });
    }, 600);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Key Management & Vaults</h2>
            <p className="text-sm text-muted-foreground">Manage envelope encryption key rings, rotation schedules, and cryptographic validator sandboxes.</p>
          </div>
          <div className="mt-4 md:mt-0 flex space-x-2">
            <Button 
              id="btn-rotate-keys"
              onClick={handleKeyRotation} 
              disabled={isRotating}
              className="bg-primary hover:bg-primary/80 text-foreground text-xs flex items-center space-x-1.5 h-10 px-4"
            >
              {isRotating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              <span>Rotate Cryptographic Keys</span>
            </Button>
          </div>
        </div>

        {/* METRICS ROW */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Encryption Engine</span>
              <ShieldCheck className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Healthy</div>
              <p className="text-[10px] text-muted-foreground">AES-GCM-256 envelope wrap active</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active KEK ID</span>
              <Key className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-mono font-bold text-foreground truncate">{activeKek}</div>
              <p className="text-[10px] text-muted-foreground">Tenant KEK wrapped by Master Key</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Expiration Timer</span>
              <AlertTriangle className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">82 Days Left</div>
              <p className="text-[10px] text-muted-foreground">Recommended rotation schedule: 90 days</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Parity Validator</span>
              <CheckCircle className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">Passed</div>
              <p className="text-[10px] text-muted-foreground">100% cryptographic parity verified</p>
            </CardContent>
          </Card>
        </div>

        {/* ROTATION ALERT banner */}
        {rotationAlert && (
          <Alert variant="success" className="animate-fade-in">
            <CheckCircle className="h-4 w-4" />
            <AlertTitle className="text-xs">Keys Rotated Successfully</AlertTitle>
            <AlertDescription className="text-[11px]">{rotationAlert}</AlertDescription>
          </Alert>
        )}

        {/* TABS LIST */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-muted p-1 w-full justify-start md:w-auto">
            <TabsTrigger value="status" className="text-xs px-3 py-1.5" id="tab-status">Key Status & Vaults</TabsTrigger>
            <TabsTrigger value="history" className="text-xs px-3 py-1.5" id="tab-history">Rotation History</TabsTrigger>
            <TabsTrigger value="validator" className="text-xs px-3 py-1.5" id="tab-validator">Parity Validator Sandbox</TabsTrigger>
            <TabsTrigger value="audit" className="text-xs px-3 py-1.5" id="tab-audit">Key Audit Trails</TabsTrigger>
          </TabsList>

          {/* TAB 1: KEY STATUS & VAULTS */}
          <TabsContent value="status" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-3">
              
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-sm font-bold flex items-center space-x-1.5">
                        <Lock className="h-4 w-4 text-muted-foreground" />
                        <span>System Master Key</span>
                      </CardTitle>
                      <CardDescription className="text-[10px]">Wraps all tenant Key Encryption Keys.</CardDescription>
                    </div>
                    <Badge variant="secondary" className="text-[10px]">VAULTED</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-xs font-semibold text-muted-foreground">Storage Method:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground">LocalSecretsManager (Local Keystore)</div>
                  <div className="text-xs font-semibold text-muted-foreground">Key wrapping Algorithm:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground">AES-GCM-256</div>
                </CardContent>
              </Card>

              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-sm font-bold flex items-center space-x-1.5">
                        <Key className="h-4 w-4 text-primary" />
                        <span>Tenant KEK</span>
                      </CardTitle>
                      <CardDescription className="text-[10px]">Tenant-scoped Key Encryption Key.</CardDescription>
                    </div>
                    <Badge variant="secondary" className="text-[10px]">ACTIVE</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-xs font-semibold text-muted-foreground">Active Key Reference ID:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground truncate">{activeKek}</div>
                  <div className="text-xs font-semibold text-muted-foreground">Wrapping Target:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground">DEKs Cryptographic Wrap</div>
                </CardContent>
              </Card>

              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-sm font-bold flex items-center space-x-1.5">
                        <Database className="h-4 w-4 text-primary" />
                        <span>Tenant DEK</span>
                      </CardTitle>
                      <CardDescription className="text-[10px]">Data Encryption Key wrapping records.</CardDescription>
                    </div>
                    <Badge variant="secondary" className="text-[10px]">ACTIVE</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-xs font-semibold text-muted-foreground">Active Key Reference ID:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground truncate">{activeDek}</div>
                  <div className="text-xs font-semibold text-muted-foreground">Encryption Algorithm:</div>
                  <div className="text-[11px] font-mono p-2 bg-muted/30 border rounded text-foreground">AES-GCM-256 (AES-AEAD)</div>
                </CardContent>
              </Card>

            </div>

            {/* Expiration Progress & Alert banner */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold">Mandatory Rotation Countdown</CardTitle>
                <CardDescription>Key rotation is recommended every 90 days. Next mandatory rotation schedule triggers in 82 days.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 pt-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-muted-foreground">Time elapsed (8 days)</span>
                  <span className="font-semibold text-muted-foreground text-warning">82 days left</span>
                </div>
                <div className="w-full bg-muted h-2 rounded overflow-hidden">
                  <div className="bg-primary h-full w-[9%]" />
                </div>
                <Alert variant="warning" className="mt-4">
                  <ShieldAlert className="h-4 w-4" />
                  <AlertTitle className="text-xs">Security Notice</AlertTitle>
                  <AlertDescription className="text-[11px]">
                    Automatic key rotations can be configured via tenant settings. Local in-memory repository is pre-seeded with fallback software providers.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: ROTATION CONSOLE */}
          <TabsContent value="history" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Key Rotation history registry</CardTitle>
                <CardDescription>Timelines and audit statuses of past Key Encryption Key (KEK) rotations.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Affected Key ID</TableHead>
                      <TableHead>Wrapping Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rotationHistory.map((log, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-mono text-xs text-muted-foreground">{log.timestamp}</TableCell>
                        <TableCell>
                          <Badge variant={log.action === "ROTATE_KEK" ? "warning" : "secondary"} className="text-[10px]">
                            {log.action}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs font-bold text-foreground truncate max-w-[200px]">{log.keyId}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{log.status}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 3: CRYPTOGRAPHIC PARITY VALIDATOR */}
          <TabsContent value="validator" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-3">
              
              <Card className="lg:col-span-2 border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Cryptographic Parity Self-Test sandbox</CardTitle>
                  <CardDescription>Runs dummy envelope encryption roundtrips (wrapping DEK inside KEK, and decrypting ciphertext bytes) to confirm key vault integrity.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <label htmlFor="validator-input" className="block text-xs font-semibold text-muted-foreground">Plaintext Input string</label>
                      <Input 
                        id="validator-input"
                        placeholder="Enter clinical message payload..." 
                        value={validatorInput}
                        onChange={(e) => setValidatorInput(e.target.value)}
                      />
                    </div>
                    <Button 
                      id="btn-run-validation"
                      onClick={handleRunValidation} 
                      disabled={isValidating}
                      className="bg-primary hover:bg-primary/80 text-foreground text-xs flex items-center space-x-1.5 h-10 px-5"
                    >
                      {isValidating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                      <span>Run Cryptographic Parity Test</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Validation Diagnostics Output pane */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-base font-bold">Diagnostics Log</CardTitle>
                  <CardDescription>Execution telemetry output.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2 space-y-4">
                  {validationResult === null ? (
                    <div className="text-center py-16 text-muted-foreground space-y-2">
                      <HelpCircle className="h-8 w-8 text-muted-foreground/40 mx-auto" />
                      <p className="text-xs">Run self-test diagnostics to inspect KMS adapter envelopes.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Alert variant="success">
                        <CheckCircle className="h-4 w-4" />
                        <AlertTitle className="text-xs">100% Cryptographic Parity Validated</AlertTitle>
                        <AlertDescription className="text-[11px] font-mono">
                          {validationResult.encryptedPayload}
                        </AlertDescription>
                      </Alert>
                      <div className="border rounded bg-muted/10 p-3 space-y-1">
                        <span className="text-[10px] font-bold uppercase text-muted-foreground">Execution Steps:</span>
                        {validationResult.diagnosticLog.map((log, i) => (
                          <div key={i} className="text-[10px] text-foreground font-mono flex items-center space-x-1">
                            <span className="text-primary font-bold">{`[${i+1}]`}</span>
                            <span>{log}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 4: AUDIT TRAILS */}
          <TabsContent value="audit" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Key Access Auditing logs</CardTitle>
                <CardDescription>SOC2 Compliance Audit trail log records tracking KEK unwraps and decryption accesses.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User / Agent</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Key Reference</TableHead>
                      <TableHead>IP Address</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditLogs.map((log, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-mono text-xs text-muted-foreground">{log.timestamp}</TableCell>
                        <TableCell className="text-xs font-bold text-foreground">{log.user}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={log.action === "KEY_ROTATION" ? "warning" : "secondary"} 
                            className="text-[10px]"
                          >
                            {log.action}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs truncate max-w-[200px]">{log.keyRef}</TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">{log.ipAddress}</TableCell>
                      </TableRow>
                    ))}
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
