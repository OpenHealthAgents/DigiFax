"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { 
  User, Calendar, ShieldCheck, AlertTriangle, Activity, 
  History, Clock, FileText, ArrowUpRight, CheckCircle2 
} from "lucide-react";

export default function PatientWorkspacePage() {
  const [matchingConfidence, setMatchingConfidence] = useState("98.6%");
  const [duplicateCandidates, setDuplicateCandidates] = useState([
    { name: "Elizabeth A. Blackwell", dob: "1988-05-12", mrn: "MRN-7819", source: "OpenHealth Clinic", confidence: "94.2%" }
  ]);

  const historicalObservations = [
    { date: "2026-07-26", test: "Fasting Glucose", result: "145.0 mg/dL", range: "70 - 100 mg/dL", status: "High" },
    { date: "2026-04-12", test: "Fasting Glucose", result: "98.0 mg/dL", range: "70 - 100 mg/dL", status: "Normal" },
    { date: "2025-10-08", test: "Fasting Glucose", result: "102.0 mg/dL", range: "70 - 100 mg/dL", status: "High" },
    { date: "2025-03-14", test: "Fasting Glucose", result: "94.0 mg/dL", range: "70 - 100 mg/dL", status: "Normal" }
  ];

  const incomingDocs = [
    { id: "DF-9011", type: "Lab Report", date: "2026-07-26", status: "Awaiting Review" },
    { id: "DF-8519", type: "Diagnostic Chart", date: "2026-06-18", status: "Approved" }
  ];

  const fhirTimeline = [
    { time: "14:32", resource: "Observation Resource", event: "LOINC 15074-8 Fasting Glucose observation bundle validated" },
    { time: "14:30", resource: "DiagnosticReport Resource", event: "Quest Blood Chemistry diagnostic report structured" },
    { time: "12:16", resource: "Patient Resource", event: "Patient demographics variables reconciled against Epic index" }
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Patient Workspace</h2>
            <p className="text-sm text-muted-foreground">Audit unified longitudinal charts and extracted faxes.</p>
          </div>
          <Button variant="outline" className="flex items-center space-x-1">
            <span>Export Full FHIR Bundle</span>
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Master column layout */}
        <div className="grid gap-6 lg:grid-cols-4">
          
          {/* 1. LEFT COLUMN: PATIENT CARD & DUPLICATES (Span 1) */}
          <div className="space-y-6">
            
            {/* Demographics Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <User className="h-4 w-4 text-primary" />
                  <span>Demographics</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase">Patient Name</p>
                  <p className="font-bold text-sm text-foreground">Elizabeth Blackwell</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase">Date of Birth</p>
                  <p className="font-semibold">1988-05-12 (Age 38)</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase">MRN Identifier</p>
                  <p className="font-semibold font-mono">MRN-890212</p>
                </div>
                <div className="pt-2 border-t border-border flex items-center justify-between">
                  <span className="font-semibold text-muted-foreground">Index Confidence</span>
                  <Badge variant="success">{matchingConfidence}</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Duplicate Candidates */}
            <Card className="border-warning/30 bg-warning/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-warning flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  <span>Duplicate Candidates</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                {duplicateCandidates.map((dup, idx) => (
                  <div key={idx} className="space-y-2">
                    <p className="text-muted-foreground">Alternate profile match found in clinic databases:</p>
                    <div className="p-2 border border-warning/20 bg-background rounded">
                      <p className="font-bold">{dup.name}</p>
                      <p className="text-[10px] text-muted-foreground">DOB: {dup.dob} • MRN: {dup.mrn}</p>
                      <p className="text-[10px] text-muted-foreground">Source: {dup.source}</p>
                    </div>
                    <Button variant="outline" size="sm" className="w-full text-[10px] h-7 font-semibold border-warning/30 text-warning hover:bg-warning/10">
                      Merge Patient Records
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>

          </div>

          {/* 2. MIDDLE COLUMN: LAB OBSERVATIONS & TRENDS (Span 2) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Lab Parameter Trend Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-bold">Fasting Glucose Longitudinal Trend</CardTitle>
                <CardDescription>Historical laboratory analyte values mapped from document history</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                {/* Minimal SVG chart */}
                <div className="relative h-44 w-full">
                  <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    {/* Reference range area (70-100) shaded in green */}
                    <rect x="0" y="45" width="100" height="25" fill="var(--success)" opacity="0.05" />
                    
                    {/* Grid lines */}
                    <line x1="0" y1="30" x2="100" y2="30" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                    <line x1="0" y1="70" x2="100" y2="70" stroke="var(--border)" strokeWidth="0.5" strokeDasharray="3" />
                    
                    {/* Line path */}
                    <path 
                      d="M 10,75 L 35,47 L 65,51 L 90,20" 
                      fill="none" 
                      stroke="var(--primary)" 
                      strokeWidth="2" 
                    />
                    
                    {/* Data Points */}
                    <circle cx="10" cy="75" r="2" fill="var(--primary)" />
                    <circle cx="35" cy="47" r="2" fill="var(--primary)" />
                    <circle cx="65" cy="51" r="2" fill="var(--primary)" />
                    <circle cx="90" cy="20" r="2" fill="var(--error)" />
                  </svg>
                  
                  {/* Chart axis label overlay */}
                  <div className="absolute top-2 left-2 text-[9px] text-error font-semibold font-mono">145.0 (High)</div>
                  <div className="absolute bottom-6 left-2 text-[9px] text-success font-semibold font-mono">94.0 (Normal)</div>
                  <div className="absolute bottom-0 left-0 right-0 flex justify-between px-2 text-[10px] text-muted-foreground">
                    <span>Mar 2025</span>
                    <span>Oct 2025</span>
                    <span>Apr 2026</span>
                    <span>Jul 2026</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Historical Observations list */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-bold">Historical Observations</CardTitle>
                <CardDescription>Extracted laboratory observation parameters</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Ingest Date</TableHead>
                      <TableHead>Test Analyte</TableHead>
                      <TableHead>Value Result</TableHead>
                      <TableHead>Reference Range</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {historicalObservations.map((obs, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-semibold text-xs">{obs.date}</TableCell>
                        <TableCell className="text-xs">{obs.test}</TableCell>
                        <TableCell className={`text-xs font-bold ${obs.status === "High" ? "text-error" : ""}`}>
                          {obs.result}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">{obs.range}</TableCell>
                        <TableCell>
                          <Badge variant={obs.status === "High" ? "error" : "success"}>
                            {obs.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

          </div>

          {/* 3. RIGHT COLUMN: FHIR TIMELINE & INCOMING FILES (Span 1) */}
          <div className="space-y-6">
            
            {/* FHIR Timeline */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-primary" />
                  <span>FHIR Transaction Timeline</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-2 text-xs">
                {fhirTimeline.map((item, idx) => (
                  <div key={idx} className="relative pl-4 border-l border-primary/40 py-1">
                    {/* Circle icon */}
                    <div className="absolute -left-1.5 top-2.5 h-3 w-3 rounded-full bg-primary border-2 border-background" />
                    <p className="font-bold text-primary text-[11px]">{item.resource} <span className="text-[9px] text-muted-foreground">({item.time})</span></p>
                    <p className="text-muted-foreground mt-0.5 text-[10px] leading-relaxed">{item.event}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Document Ingest History */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <History className="h-4 w-4 text-primary" />
                  <span>Document Ingest History</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                {incomingDocs.map((doc, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 border border-border rounded bg-muted/20">
                    <div className="flex items-center space-x-2 min-w-0">
                      <FileText className="h-4 w-4 text-primary shrink-0" />
                      <div className="min-w-0">
                        <p className="font-semibold truncate">{doc.id}</p>
                        <p className="text-[10px] text-muted-foreground">{doc.type} • {doc.date}</p>
                      </div>
                    </div>
                    <Badge variant={doc.status === "Approved" ? "success" : "warning"}>
                      {doc.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
