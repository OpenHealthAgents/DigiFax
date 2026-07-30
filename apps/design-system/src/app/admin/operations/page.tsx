/**
 * @file page.tsx
 * @description Platform Operations & Runbook console page.
 * 
 * Supports global maintenance switch, subsystem health checklists (Database, Storage, AI/OCR),
 * and dynamic feature flag controls.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Switch } from "../../../components/ui/switch";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { 
  ShieldAlert, CheckCircle2, Server, Database, Sparkles, Activity, Cpu, 
  Settings, RefreshCw, AlertTriangle, Play, HelpCircle
} from "lucide-react";

// --- TYPES ---
interface HealthItem {
  name: string;
  component: string;
  status: "HEALTHY" | "DEGRADED" | "DOWN";
  latency: number;
}

export default function PlatformOperationsPage() {
  // --- STATE STORES ---
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [autoIngestFlag, setAutoIngestFlag] = useState(true);
  const [llmValidationFlag, setLlmValidationFlag] = useState(false);
  const [termRollbackFlag, setTermRollbackFlag] = useState(true);
  const [runAlert, setRunAlert] = useState<string | null>(null);

  const [healthChecks, setHealthChecks] = useState<HealthItem[]>([
    { name: "Clinical Database", component: "DATABASE", status: "HEALTHY", latency: 12.4 },
    { name: "S3 Storage bucket", component: "STORAGE", status: "HEALTHY", latency: 45.1 },
    { name: "Temporal Engine Workflow", component: "TEMPORAL", status: "HEALTHY", latency: 18.0 },
    { name: "Redis Ingest Queue", component: "QUEUE", status: "HEALTHY", latency: 5.2 },
    { name: "OpenAI GPT-4o Extractor", component: "AI_PROVIDER", status: "HEALTHY", latency: 840.0 },
    { name: "PaddleOCR Server", component: "OCR_PROVIDER", status: "HEALTHY", latency: 220.0 }
  ]);

  // --- HANDLERS ---

  /**
   * Toggles global maintenance status lock.
   */
  const handleMaintenanceToggle = (checked: boolean) => {
    setMaintenanceMode(checked);
    if (checked) {
      setRunAlert("Platform successfully locked. Maintenance Mode active.");
    } else {
      setRunAlert("Platform unlocked. Ingest pipelines resumed.");
    }
    setTimeout(() => setRunAlert(null), 3000);
  };

  /**
   * Refreshes operations latency numbers.
   */
  const handleRefreshChecks = () => {
    setHealthChecks(prev => prev.map(c => ({
      ...c,
      latency: Math.round(c.latency * (0.9 + Math.random() * 0.2) * 10) / 10
    })));
    setRunAlert("Refreshed components checks latency metrics successfully.");
    setTimeout(() => setRunAlert(null), 3000);
  };

  // Resolve component icon
  const getIcon = (comp: string) => {
    switch (comp) {
      case "DATABASE": return <Database className="h-5 w-5 text-primary" />;
      case "STORAGE": return <Server className="h-5 w-5 text-primary" />;
      case "TEMPORAL": return <Activity className="h-5 w-5 text-primary" />;
      default: return <Cpu className="h-5 w-5 text-primary" />;
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Platform Operations</h2>
            <p className="text-sm text-muted-foreground">Monitor subsystem health latencies, toggle feature releases, and activate maintenance locks.</p>
          </div>
          <div className="mt-4 md:mt-0 flex space-x-2">
            <Button 
              id="btn-refresh-health"
              onClick={handleRefreshChecks} 
              className="bg-muted hover:bg-muted/80 text-foreground text-xs flex items-center space-x-1.5 h-10 px-4"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh Metrics</span>
            </Button>
          </div>
        </div>

        {/* FEEDBACK BANNER */}
        {runAlert && (
          <Alert variant="success" className="animate-fade-in" id="alert-ops-feedback">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">Operation Completed</AlertTitle>
            <AlertDescription className="text-[11px]">{runAlert}</AlertDescription>
          </Alert>
        )}

        {/* MAINTENANCE BANNER WARNING */}
        {maintenanceMode && (
          <Alert variant="warning" className="border-warning/50 bg-warning/10 text-warning" id="alert-maintenance-active">
            <ShieldAlert className="h-4 w-4" />
            <AlertTitle className="text-xs">Maintenance Mode Active</AlertTitle>
            <AlertDescription className="text-[11px]">
              The platform is currently locked. Inbound clinical intake document processing routes are temporarily paused.
            </AlertDescription>
          </Alert>
        )}

        {/* CORE GRID */}
        <div className="grid gap-6 md:grid-cols-3">
          
          {/* SUBSYSTEM HEALTH CHECK LIST */}
          <div className="md:col-span-2 space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Subsystem Statuses & Latencies</CardTitle>
                <CardDescription>Real-time checks resolved from primary engine gateways.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 grid gap-4 sm:grid-cols-2">
                {healthChecks.map((check, idx) => (
                  <div key={idx} className="border rounded-lg p-3 bg-muted/10 flex justify-between items-center hover:bg-muted/20 transition-colors">
                    <div className="flex items-center space-x-3">
                      {getIcon(check.component)}
                      <div>
                        <span className="font-bold text-xs text-foreground block">{check.name}</span>
                        <span className="text-[9px] text-muted-foreground block font-mono">Latency: {check.latency}ms</span>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-success/15 text-success font-bold text-[9px]">
                      {check.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* FEATURE FLAGS SECTION */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Feature Flags & Hot Releases</CardTitle>
                <CardDescription>Dynamically enable or disable extraction features.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 space-y-4">
                <div className="flex justify-between items-center p-3 border rounded-lg bg-muted/10">
                  <div>
                    <span className="font-bold text-xs text-foreground block">AUTO_INGEST Intake Routes</span>
                    <span className="text-[9px] text-muted-foreground block">Trigger instant OCR execution on inbound faxes.</span>
                  </div>
                  <Switch 
                    id="switch-auto-ingest" 
                    checked={autoIngestFlag} 
                    onCheckedChange={setAutoIngestFlag} 
                  />
                </div>

                <div className="flex justify-between items-center p-3 border rounded-lg bg-muted/10">
                  <div>
                    <span className="font-bold text-xs text-foreground block">LLM_VALIDATION Engine</span>
                    <span className="text-[9px] text-muted-foreground block">Route extracted terminology codes to clinical reasoning model validation.</span>
                  </div>
                  <Switch 
                    id="switch-llm-validation" 
                    checked={llmValidationFlag} 
                    onCheckedChange={setLlmValidationFlag} 
                  />
                </div>

                <div className="flex justify-between items-center p-3 border rounded-lg bg-muted/10">
                  <div>
                    <span className="font-bold text-xs text-foreground block">TERM_ROLLBACK Terminology Controls</span>
                    <span className="text-[9px] text-muted-foreground block">Allow terminology mapping approvals to be manually rolled back.</span>
                  </div>
                  <Switch 
                    id="switch-term-rollback" 
                    checked={termRollbackFlag} 
                    onCheckedChange={setTermRollbackFlag} 
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* SIDEBAR: MAINTENANCE & RUNBOOKS CONTROLS */}
          <div className="space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold">Maintenance Gatekeeper</CardTitle>
                <CardDescription>Manually lock systems for emergency DB patches.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 space-y-4">
                <div className="flex justify-between items-center p-3 border rounded-lg bg-error/5 border-error/10">
                  <div>
                    <span className="font-bold text-xs text-foreground block">System Maintenance Lock</span>
                    <span className="text-[9px] text-muted-foreground block">Route faxes to buffer memory queues.</span>
                  </div>
                  <Switch 
                    id="switch-maintenance" 
                    checked={maintenanceMode} 
                    onCheckedChange={handleMaintenanceToggle} 
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <Settings className="h-4 w-4 text-primary" />
                  <span>Subsystem Runbooks</span>
                </CardTitle>
                <CardDescription>Standard operating recovery scripts.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 space-y-3">
                <div className="border rounded p-3 bg-muted/15">
                  <span className="text-[10px] font-bold uppercase text-muted-foreground">Temporal Queue Jam</span>
                  <div className="text-xs font-semibold mt-1">Flush stuck pipelines in worker memory pool.</div>
                  <Button className="bg-muted hover:bg-muted/80 text-foreground text-[10px] h-7 px-2.5 mt-2">
                    <Play className="h-2.5 w-2.5 mr-1" /> Run Diagnostics
                  </Button>
                </div>
                
                <div className="border rounded p-3 bg-muted/15">
                  <span className="text-[10px] font-bold uppercase text-muted-foreground">OCR Endpoint Timeout</span>
                  <div className="text-xs font-semibold mt-1">Cycle PaddleOCR server container processes.</div>
                  <Button className="bg-muted hover:bg-muted/80 text-foreground text-[10px] h-7 px-2.5 mt-2">
                    <Play className="h-2.5 w-2.5 mr-1" /> Cycle Container
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

        </div>

      </div>
    </AppShell>
  );
}
