/**
 * @file page.tsx
 * @description DigiFax Observability Analytics Dashboard. Displays real-time operational metrics,
 * model accuracy parameters (OCR and AI confidence), processing durations, and operator output statistics.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  BarChart4, Download, Calendar, Activity, TrendingUp, 
  Clock, ShieldCheck, CheckCircle2, AlertTriangle, ArrowDown 
} from "lucide-react";

export default function AnalyticsPage() {
  // state hooks tracking user-selected intervals and alerts
  const [timeRange, setTimeRange] = useState("Last 7 Days");
  const [csvMessage, setCsvMessage] = useState("");

  // Static mock datasets segmenting data metrics by clinic campuses
  const organizationActivity = [
    { clinic: "OpenHealth Main Campus", volume: 342, ocrAcc: "96.2%", aiConf: "91.0%", exportRate: "99.1%" },
    { clinic: "St. Jude Outpatient Clinic", volume: 185, ocrAcc: "94.0%", aiConf: "88.5%", exportRate: "98.2%" },
    { clinic: "Children's Health Pavilion", volume: 94, ocrAcc: "95.5%", aiConf: "89.0%", exportRate: "100.0%" },
    { clinic: "Westside Lab Center", volume: 48, ocrAcc: "91.2%", aiConf: "84.1%", exportRate: "95.0%" }
  ];

  // Simulates asynchronous compilation and downloads of CSV metrics
  const handleExportCSV = () => {
    setCsvMessage("CSV report downloaded successfully!");
    setTimeout(() => setCsvMessage(""), 3000);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PAGE HEADER & DYNAMIC FILTERS */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h2>
            <p className="text-sm text-muted-foreground">Monitor longitudinal quality KPIs, extraction metrics, and team output.</p>
          </div>
          
          {/* Controls to toggle historical scopes and dispatch downloads */}
          <div className="flex items-center space-x-3">
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="rounded-md border border-border bg-background px-3 py-1.5 text-sm outline-none"
            >
              <option>Today</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>This Year</option>
            </select>
            <Button variant="outline" size="sm" onClick={handleExportCSV} className="flex items-center space-x-1">
              <Download className="h-4 w-4" />
              <span>Export CSV Data</span>
            </Button>
          </div>
        </div>

        {/* Temporary CSV success alert */}
        {csvMessage && (
          <Alert variant="success" className="py-2">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">Export Complete</AlertTitle>
            <AlertDescription className="text-[11px]">{csvMessage}</AlertDescription>
          </Alert>
        )}

        {/* 1. TOP SECTION: KPI SUMMARIES GRID (4 Columns) */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          
          {/* Average OCR Word Accuracy */}
          <Card>
            <CardContent className="p-6">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">Average OCR Accuracy</span>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">94.6%</span>
                <span className="text-xs text-success flex items-center font-medium">
                  <TrendingUp className="h-3 w-3 mr-1" /> +0.8%
                </span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-3">
                <div className="h-full bg-primary" style={{ width: "94.6%" }} />
              </div>
            </CardContent>
          </Card>

          {/* Average AI Model Confidence */}
          <Card>
            <CardContent className="p-6">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">AI Extraction Confidence</span>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">89.2%</span>
                <span className="text-xs text-success flex items-center font-medium">
                  <TrendingUp className="h-3 w-3 mr-1" /> +1.4%
                </span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-3">
                <div className="h-full bg-success" style={{ width: "89.2%" }} />
              </div>
            </CardContent>
          </Card>

          {/* US Core Mappings Accuracy */}
          <Card>
            <CardContent className="p-6">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">Terminology Accuracy</span>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">96.5%</span>
                <span className="text-xs text-success flex items-center font-medium">
                  <TrendingUp className="h-3 w-3 mr-1" /> +0.5%
                </span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-3">
                <div className="h-full bg-success" style={{ width: "96.5%" }} />
              </div>
            </CardContent>
          </Card>

          {/* Average processing pipeline durations */}
          <Card>
            <CardContent className="p-6">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">Avg Processing Time</span>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">14.2m</span>
                <span className="text-xs text-success flex items-center font-medium">
                  <ArrowDown className="h-3 w-3 mr-1" /> -2.1m
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground mt-2">Ingest to export lifecycle duration</p>
            </CardContent>
          </Card>

        </div>

        {/* 2. MIDDLE SECTION: DATA GRAPHS & PRODUCTIVITIES (2 Columns) */}
        <div className="grid gap-6 md:grid-cols-2">
          
          {/* Average Processing Time (SVG Line Plot) */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Average Processing Duration</CardTitle>
              <CardDescription>Minutes elapsed to resolve reviewer audit cycles</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="relative h-48 w-full">
                <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  {/* Grid Lines */}
                  <line x1="0" y1="20" x2="100" y2="20" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                  <line x1="0" y1="60" x2="100" y2="60" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                  {/* Performance Data path vector */}
                  <path 
                    d="M 5,22 L 20,40 L 40,32 L 60,60 L 80,48 L 95,78" 
                    fill="none" 
                    stroke="var(--primary)" 
                    strokeWidth="2.5" 
                  />
                  <circle cx="95" cy="78" r="2" fill="var(--primary)" />
                </svg>
                <div className="absolute top-2 left-2 text-[10px] text-muted-foreground font-mono">22 mins</div>
                <div className="absolute bottom-6 left-2 text-[10px] text-success font-semibold font-mono">14 mins (Current)</div>
              </div>
            </CardContent>
          </Card>

          {/* Clinician Reviewer Productivity outputs (Custom Inline Bar Plots) */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Reviewer Agent Productivity</CardTitle>
              <CardDescription>Reviews completed by operator over the {timeRange}</CardDescription>
            </CardHeader>
            <CardContent className="pt-4 flex flex-col justify-around h-48 text-xs">
              
              {/* Arthur Doyle */}
              <div className="space-y-1">
                <div className="flex justify-between font-semibold">
                  <span>Dr. Arthur Doyle</span>
                  <span>142 reviews</span>
                </div>
                <div className="h-3 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: "85%" }} />
                </div>
              </div>
              
              {/* Mary Walker */}
              <div className="space-y-1">
                <div className="flex justify-between font-semibold">
                  <span>Dr. Mary Walker</span>
                  <span>118 reviews</span>
                </div>
                <div className="h-3 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: "70%" }} />
                </div>
              </div>

              {/* William Osler */}
              <div className="space-y-1">
                <div className="flex justify-between font-semibold">
                  <span>Dr. William Osler</span>
                  <span>84 reviews</span>
                </div>
                <div className="h-3 bg-muted rounded overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: "50%" }} />
                </div>
              </div>
            </CardContent>
          </Card>

        </div>

        {/* 3. BOTTOM SECTION: CLINICAL FACILITY breakdowns */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Clinic Facility Activity Breakdown</CardTitle>
            <CardDescription>Longitudinal ingestion stats segmented by facility index</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Clinical Facility</TableHead>
                  <TableHead>Ingestion Volume</TableHead>
                  <TableHead>OCR Word Acc</TableHead>
                  <TableHead>AI Confidence</TableHead>
                  <TableHead>EHR Export Success</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {organizationActivity.map((org, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-semibold text-sm">{org.clinic}</TableCell>
                    <TableCell>{org.volume} faxes</TableCell>
                    <TableCell className="text-primary font-medium">{org.ocrAcc}</TableCell>
                    <TableCell>{org.aiConf}</TableCell>
                    <TableCell>
                      <Badge variant="success">{org.exportRate}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

      </div>
    </AppShell>
  );
}
