"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { 
  Play, Square, RotateCcw, AlertTriangle, Clock, 
  Terminal, ArrowRight, Activity, Cpu, ShieldAlert 
} from "lucide-react";

export default function WorkflowPage() {
  const [retriesCount, setRetriesCount] = useState(2);
  const [workflowStatus, setWorkflowStatus] = useState("Running / Retrying");

  const workflowSteps = [
    { name: "IngestFaxActivity", status: "Completed", time: "1.2s", retries: 0 },
    { name: "RunOCRActivity", status: "Completed", time: "12.4s", retries: 0 },
    { name: "ClinicalExtractActivity", status: "Completed", time: "8.1s", retries: 0 },
    { name: "FHIRValidationActivity", status: "Completed", time: "0.8s", retries: 0 },
    { name: "EHRIntegrationExportActivity", status: "Failed", time: "Retrying...", retries: 2 }
  ];

  const temporalEvents = [
    { id: "EV-108", type: "ActivityTaskStarted", time: "14:32:01", duration: "0.1s", status: "Running" },
    { id: "EV-107", type: "ActivityTaskScheduled", time: "14:32:00", duration: "-", status: "Scheduled" },
    { id: "EV-106", type: "ActivityTaskFailed", time: "14:31:45", duration: "2.1s", status: "Failed" },
    { id: "EV-105", type: "WorkflowTaskCompleted", time: "14:31:40", duration: "0.2s", status: "Completed" }
  ];

  const rawLogs = [
    "[14:31:38] [INFO] Temporal workflow started for workflowId=df-wf-9011",
    "[14:31:39] [INFO] IngestFaxActivity: completed successfully. fax_hash=sha256:901a182",
    "[14:31:51] [INFO] RunOCRActivity: parsed 3 pages, word_confidence=96.4%",
    "[14:31:59] [INFO] ClinicalExtractActivity: patient Blackwell found. Observation LOINC 15074-8 validated.",
    "[14:32:00] [INFO] FHIRValidationActivity: Bundle conforms to US Core Laboratory Observation profile",
    "[14:32:02] [ERROR] EHRIntegrationExportActivity: Epic server returned 401 Unauthorized. Refreshing token...",
    "[14:32:02] [WARN] Temporal Activity retry scheduled in 30 seconds. retryCount=2"
  ];

  const handleRetry = () => {
    setRetriesCount(retriesCount + 1);
    setWorkflowStatus("Retry Dispatched");
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Workflow Visualization</h2>
            <p className="text-sm text-muted-foreground">Monitor and manage Temporal state machine execution paths.</p>
          </div>
          
          {/* Action triggers */}
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={handleRetry} className="flex items-center space-x-1">
              <RotateCcw className="h-4 w-4" />
              <span>Retry Failed Activity</span>
            </Button>
            <Button variant="outline" size="sm" className="text-error hover:bg-error/10 border-error/20 flex items-center space-x-1">
              <Square className="h-4 w-4" />
              <span>Cancel Workflow</span>
            </Button>
            <Button variant="default" size="sm" className="flex items-center space-x-1">
              <Play className="h-4 w-4" />
              <span>Restart Workflow</span>
            </Button>
          </div>
        </div>

        {/* 1. TOP ROW: ERROR ALERTS & TIMING METRICS */}
        <div className="grid gap-6 md:grid-cols-3">
          
          {/* Workflow Status summary */}
          <Card>
            <CardContent className="p-6 text-xs space-y-2">
              <span className="font-bold text-muted-foreground uppercase text-[10px]">Workflow State</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-xl font-bold text-primary">{workflowStatus}</span>
                <Badge variant="warning">Retrying</Badge>
              </div>
              <p className="text-muted-foreground">Workflow ID: **df-wf-9011**</p>
            </CardContent>
          </Card>

          {/* Timing metrics */}
          <Card>
            <CardContent className="p-6 text-xs space-y-2">
              <span className="font-bold text-muted-foreground uppercase text-[10px]">Execution Duration</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-xl font-bold">45.2s</span>
                <span className="text-muted-foreground">elapsed</span>
              </div>
              <p className="text-muted-foreground flex items-center">
                <Clock className="h-3.5 w-3.5 mr-1" /> Timeout threshold: 300s limit
              </p>
            </CardContent>
          </Card>

          {/* Active Error warning */}
          <Card className="border-error/30 bg-error/5">
            <CardContent className="p-6 text-xs space-y-2">
              <span className="font-bold text-error uppercase text-[10px] flex items-center">
                <ShieldAlert className="h-4 w-4 mr-1 shrink-0" /> Active Exception
              </span>
              <p className="font-bold text-sm">401 Unauthorized</p>
              <p className="text-muted-foreground">Epic gateway credentials expired. Retried **{retriesCount}** times.</p>
            </CardContent>
          </Card>

        </div>

        {/* 2. MIDDLE ROW: TEMPORAL STATE GRAPH */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Temporal State Graph</CardTitle>
            <CardDescription>Chronological sequence of orchestrated activity nodes</CardDescription>
          </CardHeader>
          <CardContent className="pt-2 flex items-center justify-center">
            {/* SVG Visual state flowchart */}
            <div className="flex items-center space-x-4 bg-muted/20 p-6 rounded border border-border text-xs font-mono w-full justify-around overflow-x-auto">
              {workflowSteps.map((step, idx) => (
                <React.Fragment key={idx}>
                  <div className={`border p-3 rounded shadow-sm text-center min-w-[140px] ${
                    step.status === "Completed" ? "border-success/30 bg-success/5 text-success" :
                    step.status === "Failed" ? "border-error/30 bg-error/5 text-error animate-pulse" :
                    "border-border bg-background"
                  }`}>
                    <p className="font-bold truncate">{step.name}</p>
                    <p className="text-[10px] text-muted-foreground mt-1">{step.time} • Retries: {step.retries}</p>
                    <span className="text-[9px] font-bold uppercase mt-1.5 block">
                      {step.status}
                    </span>
                  </div>
                  {idx < workflowSteps.length - 1 && (
                    <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                  )}
                </React.Fragment>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 3. BOTTOM ROW: EVENTS TABLE & RAW LOGS CONSOLE */}
        <div className="grid gap-6 md:grid-cols-2">
          
          {/* Events table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Temporal Events Log</CardTitle>
              <CardDescription>History event logs matching Temporal engine schemas</CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Event ID</TableHead>
                    <TableHead>Event Type</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {temporalEvents.map((evt, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="font-semibold text-xs">{evt.id}</TableCell>
                      <TableCell className="text-xs">{evt.type}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{evt.time}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            evt.status === "Completed" ? "success" :
                            evt.status === "Running" ? "default" : "error"
                          }
                        >
                          {evt.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Raw logs console */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Execution Raw Logs</CardTitle>
              <CardDescription>Activity worker console streams</CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <pre className="p-4 bg-zinc-950 text-amber-400 text-xs font-mono rounded overflow-auto h-48 leading-relaxed">
                {rawLogs.join("\n")}
              </pre>
            </CardContent>
          </Card>

        </div>

      </div>
    </AppShell>
  );
}
