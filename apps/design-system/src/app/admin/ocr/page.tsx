/**
 * @file page.tsx
 * @description OCR Provider Administration Console.
 * 
 * Provides interactive benchmarking sandboxes comparing character error rates,
 * execution latencies, quality passing distributions, and prioritized failovers.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { 
  FileText, Activity, Zap, CheckCircle2, ShieldAlert, 
  BarChart, ArrowRight, Play, Loader2, Award, History
} from "lucide-react";

// --- TYPES ---
interface EngineComparison {
  name: string;
  latency: string;
  confidence: string;
  wer: string; // Word Error Rate
  text: string;
}

export default function OCRAdministrationPage() {
  // --- STATE STORES ---
  const [selectedSample, setSelectedSample] = useState("Lab Scan Report");
  const [isComparing, setIsComparing] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [activeTab, setActiveTab] = useState<"Tesseract" | "PaddleOCR" | "SuryaOCR">("Tesseract");

  // Comparison outputs catalog
  const comparisonResults: Record<string, EngineComparison> = {
    Tesseract: {
      name: "Tesseract OCR",
      latency: "84ms",
      confidence: "88.2%",
      wer: "4.8%",
      text: "PATIENT: JOHN DOE\nDOB: 12/04/1982\nHbA1c: 7.4% (HIGH)\nNOTES: Retest in 3 months if sugar index remains elevated."
    },
    PaddleOCR: {
      name: "PaddleOCR",
      latency: "410ms",
      confidence: "94.5%",
      wer: "2.1%",
      text: "PATIENT: JOHN DOE\nDOB: 12/04/1982\nHbA1c: 7.4% (HIGH)\nNOTES: Retest in 3 months if sugar index remains elevated."
    },
    SuryaOCR: {
      name: "Surya OCR",
      latency: "920ms",
      confidence: "97.1%",
      wer: "0.8%",
      text: "PATIENT: JOHN DOE\nDOB: 12/04/1982\nHbA1c: 7.4% (HIGH)\nNOTES: Retest in 3 months if sugar index remains elevated."
    }
  };

  // --- CONTROLLER HANDLERS ---
  const handleRunComparison = (e: React.FormEvent) => {
    e.preventDefault();
    setIsComparing(true);
    setShowComparison(false);

    setTimeout(() => {
      setIsComparing(false);
      setShowComparison(true);
    }, 1200);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">OCR Provider Administration</h2>
          <p className="text-sm text-muted-foreground">Test, compare, and benchmark optical character recognition engines. Track Word Error Rates (WER) and failover routing thresholds.</p>
        </div>

        {/* METRICS DASHBOARD */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Character Accuracy</span>
              <Award className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">96.8% Avg</div>
              <p className="text-[10px] text-muted-foreground">Word Recognition rate last 30d</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Average Processing</span>
              <Activity className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">240ms / doc</div>
              <p className="text-[10px] text-muted-foreground">Tesseract: 84ms | Surya: 920ms</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">High Confidence Pass</span>
              <CheckCircle2 className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">94.8% Pass</div>
              <p className="text-[10px] text-muted-foreground">Exceeds 0.80 validation limit</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Engines</span>
              <Zap className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">5 / 6 Online</div>
              <p className="text-[10px] text-muted-foreground">Tesseract, Paddle, Surya, Easy, DocTR</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT COLUMN: COMPARISON SANDBOX */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-primary" />
                  <span>OCR Engine Comparison Sandbox</span>
                </CardTitle>
                <CardDescription>Select clinical document samples to benchmark OCR outputs side-by-side.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <form onSubmit={handleRunComparison} className="space-y-4">
                  <div className="space-y-1.5">
                    <label htmlFor="sample-select" className="text-xs font-semibold uppercase text-muted-foreground">Select Ingestion Sample Scan</label>
                    <select 
                      id="sample-select"
                      value={selectedSample}
                      onChange={(e) => setSelectedSample(e.target.value)}
                      className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                    >
                      <option>Lab Scan Report</option>
                      <option>Patient Referral Document</option>
                      <option>Handwritten Prescription Scan</option>
                    </select>
                  </div>

                  <div className="flex justify-between items-center pt-2">
                    <span className="text-[11px] text-muted-foreground">Comparing: Tesseract, PaddleOCR, Surya OCR</span>
                    <Button id="compare-btn" type="submit" disabled={isComparing} className="flex items-center space-x-1.5">
                      {isComparing ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>Ingesting Sample...</span>
                        </>
                      ) : (
                        <>
                          <Play className="h-3.5 w-3.5" />
                          <span>Run Comparison Benchmark</span>
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Sandboxed comparative results presentation */}
                  {showComparison && (
                    <div className="space-y-4 pt-4 border-t">
                      
                      {/* Custom Tab Triggers */}
                      <div className="flex space-x-2 border-b pb-2">
                        {["Tesseract", "PaddleOCR", "SuryaOCR"].map((t) => (
                          <button
                            key={t}
                            id={`tab-btn-${t.toLowerCase()}`}
                            type="button"
                            onClick={() => setActiveTab(t as any)}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                              activeTab === t 
                                ? "bg-primary text-white" 
                                : "text-muted-foreground hover:bg-muted/30"
                            }`}
                          >
                            {t}
                          </button>
                        ))}
                      </div>

                      {/* Engine Details Cards */}
                      <div className="grid gap-3 grid-cols-3">
                        <div className="p-3 border border-border/80 bg-background/50 rounded-lg text-center space-y-1">
                          <span className="text-[9px] uppercase font-semibold text-muted-foreground">Latency</span>
                          <p className="font-bold text-xs text-foreground">{comparisonResults[activeTab].latency}</p>
                        </div>
                        <div className="p-3 border border-border/80 bg-background/50 rounded-lg text-center space-y-1">
                          <span className="text-[9px] uppercase font-semibold text-muted-foreground">Confidence</span>
                          <p className="font-bold text-xs text-success">{comparisonResults[activeTab].confidence}</p>
                        </div>
                        <div className="p-3 border border-border/80 bg-background/50 rounded-lg text-center space-y-1">
                          <span className="text-[9px] uppercase font-semibold text-muted-foreground">Word Error Rate (WER)</span>
                          <p className="font-bold text-xs text-warning">{comparisonResults[activeTab].wer}</p>
                        </div>
                      </div>

                      {/* Text content area */}
                      <div className="p-4 border border-border/80 bg-muted/20 rounded-lg">
                        <pre id="extracted-text-output" className="font-mono text-xs text-foreground whitespace-pre-wrap leading-relaxed select-all">
                          {comparisonResults[activeTab].text}
                        </pre>
                      </div>

                    </div>
                  )}

                </form>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT COLUMN: FAILOVERS & ACCURACY REPORTS */}
          <div className="space-y-6">
            
            {/* Fallback chain visual mapping */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <History className="h-4.5 w-4.5 text-primary" />
                  <span>Prioritized OCR Routing</span>
                </CardTitle>
                <CardDescription>Failover chain sequence triggered on low-confidence.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1">
                <div className="relative pl-6 space-y-5 border-l border-border/60">
                  <div className="relative space-y-1">
                    <span className="absolute -left-[31px] top-0.5 h-5 w-5 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white border border-background">1</span>
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-foreground">Tesseract</span>
                      <Badge variant="secondary" className="text-[8px] px-1 py-0 font-mono">Primary</Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Ultra-fast local check (84ms)</p>
                  </div>

                  <div className="relative space-y-1">
                    <span className="absolute -left-[31px] top-0.5 h-5 w-5 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white border border-background">2</span>
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-foreground">PaddleOCR</span>
                      <Badge variant="secondary" className="text-[8px] px-1 py-0 font-mono">Failover 1</Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Triggered if Tesseract confidence &lt; 0.80</p>
                  </div>

                  <div className="relative space-y-1">
                    <span className="absolute -left-[31px] top-0.5 h-5 w-5 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white border border-background">3</span>
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-foreground">Surya OCR</span>
                      <Badge variant="secondary" className="text-[8px] px-1 py-0 font-mono">Failover 2</Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Deep layout analysis check (920ms)</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quality warnings report alert */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <BarChart className="h-4.5 w-4.5 text-primary" />
                  <span>Quality & Accuracy Distribution</span>
                </CardTitle>
                <CardDescription>Daily parse volumes and quality metrics.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1 text-xs">
                
                <div className="p-3 border border-warning/10 bg-warning/5 rounded-lg flex items-start space-x-2.5">
                  <ShieldAlert className="h-4 w-4 text-warning mt-0.5 shrink-0" />
                  <div className="space-y-1">
                    <span className="font-bold text-warning text-xs">Degradation Warning</span>
                    <p className="text-[10px] text-muted-foreground">Tesseract character error rates in Spanish scans increased to 5.2% after recent update. Review language packs config.</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>High Confidence scans (&gt; 0.85)</span>
                      <span className="font-bold text-success">92.4%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-1.5">
                      <div className="bg-success h-1.5 rounded-full" style={{ width: "92%" }} />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>Borderline passes (0.75 - 0.85)</span>
                      <span className="font-bold text-warning">5.2%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-1.5">
                      <div className="bg-warning h-1.5 rounded-full" style={{ width: "5%" }} />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>Low confidence failures (&lt; 0.75)</span>
                      <span className="font-bold text-error">2.4%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-1.5">
                      <div className="bg-error h-1.5 rounded-full" style={{ width: "2%" }} />
                    </div>
                  </div>
                </div>

              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
