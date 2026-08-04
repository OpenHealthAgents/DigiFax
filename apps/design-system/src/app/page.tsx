"use client";

import React, { useState } from "react";
import { AppShell } from "../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../components/ui/table";
import { 
  FileText, CheckCircle2, AlertTriangle, AlertCircle, TrendingUp, 
  Activity, ArrowUpRight, UploadCloud, RefreshCw, Layers, ShieldCheck
} from "lucide-react";

export default function DashboardPage() {
  // Today's total document upload metric tracker state
  const [uploadsCount, setUploadsCount] = useState(48);

  // Mock list representing recent ingested patient files in the dashboard queue.
  // This state is mapped into standard tables to show ID, Demographics details, OCR and AI extraction accuracies.
  const [recentDocs, setRecentDocs] = useState([
    { id: "DF-9011", name: "Elizabeth Blackwell", type: "Blood Chemistry", time: "10m ago", status: "Awaiting Review", ocr: "96.4%", ai: "91.2%" },
    { id: "DF-9010", name: "Arthur Conan Doyle", type: "Lipid Profile", time: "25m ago", status: "Approved", ocr: "98.1%", ai: "94.5%" },
    { id: "DF-9009", name: "Mary Edwards Walker", type: "Urinalysis", time: "1h ago", status: "Failed Validation", ocr: "71.0%", ai: "82.0%" },
    { id: "DF-9008", name: "William Osler", type: "Metabolic Panel", time: "2h ago", status: "Approved", ocr: "95.5%", ai: "90.0%" },
  ]);

  // Mock timeline logs representing system-level logs like EHR transaction events,
  // OCR processing warnings, and schema validator updates.
  const recentActivity = [
    { text: "EHR transaction export success to Epic Sandbox", time: "5m ago", type: "success" },
    { text: "OCR threshold warning on DF-9009 (patient signature fuzzy)", time: "1h ago", type: "warning" },
    { text: "Temporal intake workflow started for doc-9011-scan.pdf", time: "15m ago", type: "info" },
    { text: "Medplum schema validation successfully approved transaction bundle", time: "3h ago", type: "success" }
  ];

  return (
    <AppShell>
      <div className="space-y-8">
        
        {/* 1. Header Widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Clinical Dashboard</h2>
            <p className="text-sm text-muted-foreground">Monitor real-time document ingest pipelines and terminology normalizations.</p>
          </div>
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2">
            <Button variant="default" className="flex items-center space-x-2">
              <UploadCloud className="h-4 w-4" />
              <span>Upload Clinical Document</span>
            </Button>
            <Button variant="outline" className="flex items-center space-x-2">
              <RefreshCw className="h-4 w-4" />
              <span>Re-run Batch Pipeline</span>
            </Button>
          </div>
        </div>

        {/* 2. Top Row Statistics Widgets */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {/* Today's Uploads */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between space-y-0">
                <span className="text-sm font-medium text-muted-foreground">Today's Ingested Documents</span>
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">{uploadsCount}</span>
                <span className="text-xs text-success flex items-center font-medium">
                  <TrendingUp className="h-3 w-3 mr-1" /> +12.4%
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">vs yesterday average (38)</p>
            </CardContent>
          </Card>

          {/* Documents Awaiting Review */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between space-y-0">
                <span className="text-sm font-medium text-muted-foreground">Awaiting Review</span>
                <Layers className="h-5 w-5 text-warning" />
              </div>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">14</span>
                <Badge variant="warning" className="ml-2">Action Required</Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Average wait-time: 14 mins</p>
            </CardContent>
          </Card>

          {/* Validation Failures */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between space-y-0">
                <span className="text-sm font-medium text-muted-foreground">Validation Failures</span>
                <AlertCircle className="h-5 w-5 text-error" />
              </div>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">3</span>
                <span className="text-xs text-error font-medium">6.2% of total</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Failed physiological bounds</p>
            </CardContent>
          </Card>

          {/* Export Success Rate */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between space-y-0">
                <span className="text-sm font-medium text-muted-foreground">EHR Export Success</span>
                <ShieldCheck className="h-5 w-5 text-success" />
              </div>
              <div className="flex items-baseline space-x-2 mt-3">
                <span className="text-2xl font-bold">98.4%</span>
                <span className="text-xs text-success font-medium">Goal: 98%</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Epic/Cerner transaction rate</p>
            </CardContent>
          </Card>
        </div>

        {/* 3. Middle Row: Interactive Chart & Accuracy Metrics */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* Daily Ingestion Volume Chart */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Daily Ingestion Volume</CardTitle>
              <CardDescription>Document pipeline traffic volumes over the past 7 days</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              {/* Minimal Interactive SVG Line Chart */}
              <div className="relative h-64 w-full">
                <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  {/* Grid lines */}
                  <line x1="0" y1="20" x2="100" y2="20" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                  <line x1="0" y1="50" x2="100" y2="50" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                  <line x1="0" y1="80" x2="100" y2="80" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                  
                  {/* Smooth line representing volume */}
                  <path
                    d="M 5,80 Q 20,40 35,60 T 65,30 T 95,15"
                    fill="none"
                    stroke="var(--primary)"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                  
                  {/* Shading fill underneath line */}
                  <path
                    d="M 5,80 Q 20,40 35,60 T 65,30 T 95,15 L 95,95 L 5,95 Z"
                    fill="url(#gradient)"
                    opacity="0.1"
                  />

                  <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="var(--primary)" />
                      <stop offset="100%" stopColor="var(--background)" />
                    </linearGradient>
                  </defs>
                </svg>

                {/* Day labels overlay */}
                <div className="absolute bottom-0 left-0 right-0 flex justify-between px-2 text-[10px] text-muted-foreground">
                  <span>Mon</span>
                  <span>Tue</span>
                  <span>Wed</span>
                  <span>Thu</span>
                  <span>Fri</span>
                  <span>Sat</span>
                  <span>Sun</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pipeline Accuracy Status Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Accuracy & Generation Rates</CardTitle>
              <CardDescription>Current accuracy metrics across pipeline nodes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-4">
              
              {/* OCR Character Accuracy */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">OCR Word Accuracy</span>
                  <span className="font-semibold text-primary">94.6%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: "94.6%" }} />
                </div>
                <span className="text-xs text-muted-foreground">Goal: 95.0% threshold</span>
              </div>

              {/* AI Extraction Confidence */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">AI Extraction Confidence</span>
                  <span className="font-semibold text-success">89.2%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-success" style={{ width: "89.2%" }} />
                </div>
                <span className="text-xs text-muted-foreground">Goal: 85.0% threshold</span>
              </div>

              {/* FHIR Generation Rate */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">FHIR Generation Success</span>
                  <span className="font-semibold text-success">100.0%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-success" style={{ width: "100.0%" }} />
                </div>
                <span className="text-xs text-muted-foreground">Goal: 99.9% threshold</span>
              </div>

            </CardContent>
          </Card>
        </div>

        {/* 4. Bottom Row: Recent Ingested Documents & Activity Logs */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* Recent Ingested Documents list table */}
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-lg font-bold">Recent Ingested Documents</CardTitle>
                <CardDescription>Clinical files ingested through NATS endpoint queues</CardDescription>
              </div>
              <Button variant="ghost" size="sm" className="text-xs font-semibold">
                <span>View all documents</span>
                <ArrowUpRight className="h-4 w-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent className="pt-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document ID</TableHead>
                    <TableHead>Patient Name</TableHead>
                    <TableHead>Test Type</TableHead>
                    <TableHead>OCR / AI</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentDocs.map((doc, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="font-medium">{doc.id}</TableCell>
                      <TableCell>{doc.name}</TableCell>
                      <TableCell>{doc.type}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{doc.ocr} / {doc.ai}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            doc.status === "Approved" ? "success" :
                            doc.status === "Awaiting Review" ? "warning" : "error"
                          }
                        >
                          {doc.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Recent Activity Feed */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Recent Activity Feed</CardTitle>
              <CardDescription>Transactional logs from pipeline adapters</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-4">
                {recentActivity.map((act, idx) => (
                  <div key={idx} className="flex space-x-3 text-sm">
                    {/* Status Dot */}
                    <div className="mt-1 flex h-2 w-2 shrink-0 rounded-full bg-primary" />
                    <div>
                      <p className="text-foreground">{act.text}</p>
                      <span className="text-xs text-muted-foreground">{act.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

        </div>

      </div>
    </AppShell>
  );
}
