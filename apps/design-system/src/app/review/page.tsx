"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  ZoomIn, ZoomOut, RotateCw, Check, X, AlertTriangle, AlertCircle, 
  Terminal, Undo2, Redo2, HelpCircle, Save, Code, History, Send 
} from "lucide-react";

export default function ReviewPage() {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [showJson, setShowJson] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState([
    { user: "System AI", text: "OCR confidence matches US-Core thresholds. Fasting glucose exceeds reference range.", time: "10m ago" }
  ]);

  // Form states
  const [patientName, setPatientName] = useState("Elizabeth Blackwell");
  const [dob, setDob] = useState("1988-05-12");
  const [glucoseVal, setGlucoseVal] = useState("145.0");

  const fhirPreview = {
    resourceType: "Observation",
    id: "df-obs-glucose",
    status: "final",
    category: [
      {
        coding: [
          { system: "http://terminology.hl7.org/CodeSystem/observation-category", code: "laboratory" }
        ]
      }
    ],
    code: {
      coding: [
        { system: "http://loinc.org", code: "15074-8", display: "Glucose [Mass/volume] in Blood" }
      ]
    },
    subject: { reference: "Patient/df-pat-blackwell" },
    valueQuantity: {
      value: parseFloat(glucoseVal) || 0,
      unit: "mg/dL",
      system: "http://unitsofmeasure.org",
      code: "mg/dL"
    }
  };

  const handlePostComment = () => {
    if (commentText.trim()) {
      setComments([...comments, { user: "Kalyan Kalwa", text: commentText, time: "Just now" }]);
      setCommentText("");
    }
  };

  return (
    <AppShell>
      <div className="space-y-4 flex flex-col h-[calc(100vh-8rem)]">
        
        {/* 1. TOP TOOLBAR BAR */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-muted/40 p-3 rounded-lg border border-border shrink-0">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-bold text-primary">DF-9011: Intake Review</span>
            <span className="text-xs text-muted-foreground flex items-center">
              <Save className="h-3.5 w-3.5 mr-1 text-success" /> Autosaved 2s ago
            </span>
            <div className="flex items-center space-x-1 border-l border-border pl-3">
              <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Undo"><Undo2 className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Redo"><Redo2 className="h-4 w-4" /></Button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" className="flex items-center space-x-1">
              <Code className="h-4 w-4" />
              <span>Re-run AI Parser</span>
            </Button>
            <Button variant="outline" size="sm" className="text-error hover:bg-error/15 border-error/30 flex items-center space-x-1">
              <X className="h-4 w-4" />
              <span>Reject</span>
            </Button>
            <Button variant="default" size="sm" className="bg-success text-success-foreground hover:bg-success/90 flex items-center space-x-1">
              <Check className="h-4 w-4" />
              <span>Approve & Export</span>
            </Button>
          </div>
        </div>

        {/* 2. MIDDLE SPLIT WORKSPACE (Flexible height) */}
        <div className="grid gap-6 md:grid-cols-2 flex-1 min-h-0 overflow-hidden">
          
          {/* LEFT COLUMN: HIGH-RES PDF VIEWERS */}
          <div className="flex flex-col border border-border rounded-lg bg-muted/10 overflow-hidden min-h-0">
            {/* Viewer Controls */}
            <div className="flex items-center justify-between p-2 border-b border-border bg-muted/30 shrink-0">
              <div className="flex items-center space-x-2 text-xs font-semibold text-muted-foreground">
                <span>blood_chemistry_report.pdf</span>
              </div>
              <div className="flex items-center space-x-1">
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setZoom(Math.max(50, zoom - 10))}><ZoomOut className="h-4 w-4" /></Button>
                <span className="text-xs font-mono px-2">{zoom}%</span>
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setZoom(zoom + 10)}><ZoomIn className="h-4 w-4" /></Button>
                <Button variant="ghost" size="icon" className="h-7 w-7 border-l border-border pl-2" onClick={() => setRotation(rotation + 90)}><RotateCw className="h-4 w-4" /></Button>
              </div>
            </div>

            {/* Document Canvas Sandbox */}
            <div className="flex-1 overflow-auto p-6 flex justify-center items-start bg-zinc-800">
              <div 
                className="relative aspect-[3/4] w-full max-w-lg bg-white rounded shadow-md p-8 text-black transition-all duration-200"
                style={{ 
                  transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                  transformOrigin: "top center" 
                }}
              >
                {/* Bounding Box Mock Overlay 1 */}
                <div 
                  className="absolute border-2 border-primary bg-primary/10 rounded cursor-pointer"
                  style={{ top: "10%", left: "15%", width: "40%", height: "8%" }}
                  title="Evidence: Patient Name"
                >
                  <span className="absolute -top-5 left-0 bg-primary text-primary-foreground text-[8px] px-1 font-bold rounded">PATIENT_NAME</span>
                </div>

                {/* Bounding Box Mock Overlay 2 */}
                <div 
                  className="absolute border-2 border-error bg-error/10 rounded cursor-pointer"
                  style={{ top: "45%", left: "15%", width: "70%", height: "12%" }}
                  title="Evidence: Fasting Glucose value out of bounds"
                >
                  <span className="absolute -top-5 left-0 bg-error text-error-foreground text-[8px] px-1 font-bold rounded">OBSERVATION_VAL</span>
                </div>

                {/* Document contents (mock patient report) */}
                <div className="space-y-6 mt-8 font-sans">
                  <div className="border-b border-zinc-200 pb-2">
                    <h3 className="text-lg font-bold text-zinc-900">Quest Diagnostics</h3>
                    <p className="text-[10px] text-zinc-500">121 Clinician Plaza, Suite A</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <p className="font-semibold text-zinc-500">PATIENT DETAIL</p>
                      <p className="font-bold text-zinc-800">Elizabeth Blackwell</p>
                      <p className="text-zinc-600">DOB: 1988-05-12</p>
                    </div>
                    <div>
                      <p className="font-semibold text-zinc-500">ORDER INFO</p>
                      <p className="text-zinc-800">Order ID: 15074-8</p>
                      <p className="text-zinc-600">Date: 2026-07-26</p>
                    </div>
                  </div>

                  <div className="mt-8 border-t border-zinc-200 pt-4">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-zinc-200 text-left font-bold text-zinc-500">
                          <th className="pb-2">ANALYTE</th>
                          <th className="pb-2">RESULT</th>
                          <th className="pb-2">REF RANGE</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b border-zinc-100">
                          <td className="py-2 text-zinc-800 font-semibold">Fasting Glucose</td>
                          <td className="py-2 text-red-600 font-bold">145.0 mg/dL</td>
                          <td className="py-2 text-zinc-600">70 - 100 mg/dL</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: CLINICAL METADATA EDITOR & PREVIEW */}
          <div className="flex flex-col border border-border rounded-lg bg-background overflow-hidden min-h-0">
            {/* Editor toggle tabs */}
            <div className="flex items-center justify-between p-2 border-b border-border bg-muted/30 shrink-0">
              <span className="text-xs font-bold">Clinical Extraction Mapping</span>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowJson(!showJson)}
                className="h-7 text-[10px] font-semibold"
              >
                {showJson ? "View Forms" : "Preview FHIR JSON"}
              </Button>
            </div>

            {/* Form Fields Editor */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {showJson ? (
                /* JSON Preview code snippet */
                <pre className="p-3 bg-muted text-foreground text-xs rounded-md font-mono overflow-auto max-h-[350px]">
                  {JSON.stringify(fhirPreview, null, 2)}
                </pre>
              ) : (
                /* Interactive Form Fields */
                <div className="space-y-4">
                  {/* Validation Alerts */}
                  <Alert variant="error" className="py-2.5">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle className="text-xs">Out of Bounds Value Detected</AlertTitle>
                    <AlertDescription className="text-[11px]">
                      Fasting Glucose result value **145.0 mg/dL** exceeds reference range limits (70-100 mg/dL).
                    </AlertDescription>
                  </Alert>

                  {/* Demographics */}
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center justify-between">
                        <span>Patient Name</span>
                        <Badge variant="success" className="text-[9px] px-1 py-0 font-bold">98% Match</Badge>
                      </label>
                      <Input value={patientName} onChange={(e) => setPatientName(e.target.value)} />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-muted-foreground uppercase">Date of Birth</label>
                      <Input type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
                    </div>
                  </div>

                  {/* Lab Results */}
                  <div className="space-y-3 border-t border-border pt-4">
                    <span className="text-xs font-bold text-muted-foreground uppercase block">Analyte Details</span>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-muted-foreground uppercase flex items-center justify-between">
                          <span>Fasting Glucose</span>
                          <Badge variant="error" className="text-[9px] px-1 py-0 font-bold">OCR Flag</Badge>
                        </label>
                        <Input value={glucoseVal} onChange={(e) => setGlucoseVal(e.target.value)} />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-muted-foreground uppercase">Units</label>
                        <Input defaultValue="mg/dL" disabled />
                      </div>
                    </div>
                  </div>

                  {/* Terminology Maps */}
                  <div className="space-y-2 border-t border-border pt-4">
                    <span className="text-xs font-bold text-muted-foreground uppercase block">Terminology Mapping</span>
                    <div className="flex items-center justify-between p-2 rounded bg-muted/50 border border-border text-xs">
                      <div>
                        <p className="font-semibold">LOINC Target Concept</p>
                        <p className="text-muted-foreground">15074-8 (Glucose [Mass/volume] in Blood)</p>
                      </div>
                      <Badge variant="success">96% Conf</Badge>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* 3. BOTTOM SECTION: TIMELINE & COMMENTS FEED */}
        <div className="h-32 border border-border rounded-lg bg-muted/10 p-3 grid grid-cols-3 gap-6 shrink-0 text-xs min-h-0">
          
          {/* Keyboard Shortcuts Legend */}
          <div className="space-y-1.5 border-r border-border pr-4">
            <span className="font-bold text-muted-foreground uppercase tracking-wider block text-[10px]">Shortcuts Legend</span>
            <div className="space-y-1 text-muted-foreground text-[11px]">
              <p><kbd className="px-1 bg-muted border rounded">Ctrl</kbd>+<kbd className="px-1 bg-muted border rounded">Z</kbd> : Undo changes</p>
              <p><kbd className="px-1 bg-muted border rounded">Ctrl</kbd>+<kbd className="px-1 bg-muted border rounded">S</kbd> : Manual Save</p>
              <p><kbd className="px-1 bg-muted border rounded">Enter</kbd> : Approve & Export</p>
            </div>
          </div>

          {/* Timeline / Audit logs */}
          <div className="space-y-1.5 border-r border-border pr-4 overflow-y-auto max-h-full">
            <span className="font-bold text-muted-foreground uppercase tracking-wider block text-[10px]">Audit logs Timeline</span>
            <div className="space-y-1 text-[11px]">
              <p className="text-success font-medium">✓ System OCR extraction completed (12:15)</p>
              <p className="text-muted-foreground">✓ Demographics verification triggered (14:30)</p>
            </div>
          </div>

          {/* Comments section */}
          <div className="flex flex-col h-full">
            <span className="font-bold text-muted-foreground uppercase tracking-wider block text-[10px] shrink-0 mb-1">Intake Comments</span>
            <div className="flex-1 overflow-y-auto space-y-1 mb-2 max-h-[50px]">
              {comments.map((c, idx) => (
                <p key={idx} className="text-[11px]"><strong className="text-primary">{c.user}</strong>: {c.text} <span className="text-[9px] text-muted-foreground">({c.time})</span></p>
              ))}
            </div>
            <div className="flex items-center space-x-1 shrink-0">
              <input 
                type="text" 
                placeholder="Post comment..." 
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handlePostComment()}
                className="flex-1 rounded border border-border bg-background px-2 py-1 text-xs outline-none"
              />
              <Button size="icon" variant="default" className="h-7 w-7 shrink-0" onClick={handlePostComment} aria-label="Send Comment">
                <Send className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>

        </div>

      </div>
    </AppShell>
  );
}
