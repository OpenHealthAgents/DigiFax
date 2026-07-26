"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { ErrorBoundary } from "../../components/shell/error-boundary";
import { Skeleton } from "../../components/ui/skeleton";
import { Button } from "../../components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { AlertCircle, ShieldCheck, Database, FileText } from "lucide-react";

// Helper component that throws an error when trigger state is true
function CrashyWidget({ shouldCrash }: { shouldCrash: boolean }) {
  if (shouldCrash) {
    throw new Error("Simulated React workspace rendering failure!");
  }
  return (
    <Card className="border border-border">
      <CardHeader>
        <CardTitle className="text-sm font-semibold">Active Health Status</CardTitle>
        <CardDescription>Live connection stats</CardDescription>
      </CardHeader>
      <CardContent className="text-sm">
        All pipeline endpoints responding normal on 200 OK.
      </CardContent>
    </Card>
  );
}

export default function ShellShowcasePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [hasCrashed, setHasCrashed] = useState(false);

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Page title */}
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System Status Panel</h2>
          <p className="text-sm text-muted-foreground">Manage and audit clinical OCR document queues.</p>
        </div>

        {/* Action controllers */}
        <div className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => setIsLoading(!isLoading)}>
            Toggle Loading State ({isLoading ? "On" : "Off"})
          </Button>
          <Button variant="danger" onClick={() => setHasCrashed(true)}>
            Simulate Rendering Error
          </Button>
        </div>

        {/* Dashboard Grid layouts */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          
          {/* Card 1: Protected route access info */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-sm font-semibold">Security Level</CardTitle>
                <CardDescription>Access permissions</CardDescription>
              </div>
              <ShieldCheck className="h-5 w-5 text-success" />
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2 mt-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-3/4" />
                </div>
              ) : (
                <p className="text-sm mt-2 text-muted-foreground">
                  Current Session: **Authenticated**. Access matches Clinical Reviewer scopes. Outbound EHR API edits require dual-factor validation flags.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Card 2: Queues */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-sm font-semibold">Temporal Workflows</CardTitle>
                <CardDescription>Document pipeline queue size</CardDescription>
              </div>
              <FileText className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2 mt-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              ) : (
                <p className="text-sm mt-2 text-muted-foreground">
                  Ingested Faxes: **14 Pending Review**, 0 Running OCR, 127 Exported to Epic.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Card 3: Error Boundary Showcase widget */}
          <ErrorBoundary>
            <CrashyWidget shouldCrash={hasCrashed} />
          </ErrorBoundary>

        </div>

      </div>
    </AppShell>
  );
}
