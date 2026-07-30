/**
 * @file page.tsx
 * @description Inbound clinical Usage Metering & Quotas Dashboard.
 * 
 * Provides daily/monthly transaction visualizations, quota alerts, department billing breakdown
 * summaries, forecasts, and manual cycle reset workflows.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../../components/ui/tabs";
import { 
  TrendingUp, Activity, FileText, Database, ShieldAlert, CheckCircle, Loader2,
  Calendar, Layers, Sparkles, Server, HardDrive, RefreshCw, BarChart3, Users
} from "lucide-react";

// --- TYPES ---
interface DeptUsage {
  name: string;
  ocrCount: number;
  aiCount: number;
  userCount: number;
  storageGb: number;
}

export default function MeteringAdministrationPage() {
  // --- STATE STORES ---
  const [activeTab, setActiveTab] = useState("quotas");
  const [accruedCost, setAccruedCost] = useState(1240.50);
  const [ocrRemaining, setOcrRemaining] = useState(2450);
  const [aiRemaining, setAiRemaining] = useState(850);
  const [isResetting, setIsResetting] = useState(false);
  const [resetAlert, setResetAlert] = useState<string | null>(null);

  // Departments Usage
  const [departments, setDepartments] = useState<DeptUsage[]>([
    { name: "Cardiology Unit", ocrCount: 4500, aiCount: 2100, userCount: 14, storageGb: 84.5 },
    { name: "Emergency Department", ocrCount: 2050, aiCount: 1850, userCount: 28, storageGb: 120.2 },
    { name: "Pediatrics Clinic", ocrCount: 1000, aiCount: 200, userCount: 8, storageGb: 32.1 }
  ]);

  // --- HANDLERS ---

  /**
   * Resets active usage billing statistics.
   */
  const handleResetBilling = () => {
    setIsResetting(true);
    setResetAlert(null);

    setTimeout(() => {
      setIsResetting(false);
      setAccruedCost(0.00);
      setOcrRemaining(10000);
      setAiRemaining(5000);
      setDepartments(prev => prev.map(d => ({
        ...d,
        ocrCount: 0,
        aiCount: 0,
        storageGb: 0.0
      })));
      setResetAlert("Accrued usage statistics successfully flushed for new billing period cycle.");
    }, 800);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Usage Metering & Billing</h2>
            <p className="text-sm text-muted-foreground">Monitor system transaction volumes, department breakdowns, current remaining quotas, and forecast trends.</p>
          </div>
          <div className="mt-4 md:mt-0">
            <Button 
              id="btn-reset-billing"
              onClick={handleResetBilling} 
              disabled={isResetting}
              className="bg-primary hover:bg-primary/80 text-foreground text-xs flex items-center space-x-1.5 h-10 px-4"
            >
              {isResetting ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              <span>Reset Billing Period</span>
            </Button>
          </div>
        </div>

        {/* METRICS ROW */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Accrued Cost</span>
              <TrendingUp className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" id="metric-accrued-cost">${accruedCost.toFixed(2)}</div>
              <p className="text-[10px] text-muted-foreground">Current monthly cycle accruals</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">OCR Quota Remaining</span>
              <Server className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success" id="metric-ocr-quota">{ocrRemaining.toLocaleString()} pages</div>
              <p className="text-[10px] text-muted-foreground">Out of 10,000 monthly pages limit</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">AI Quota Remaining</span>
              <Sparkles className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning" id="metric-ai-quota">{aiRemaining.toLocaleString()} calls</div>
              <p className="text-[10px] text-muted-foreground">Out of 5,000 monthly queries limit</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Daily Avg Volume</span>
              <Activity className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">125 tasks</div>
              <p className="text-[10px] text-muted-foreground">Average pages processed per 24 hours</p>
            </CardContent>
          </Card>
        </div>

        {/* RESET ALERT banner */}
        {resetAlert && (
          <Alert variant="success" className="animate-fade-in">
            <CheckCircle className="h-4 w-4" />
            <AlertTitle className="text-xs">Billing Period Flushed</AlertTitle>
            <AlertDescription className="text-[11px]">{resetAlert}</AlertDescription>
          </Alert>
        )}

        {/* TABS LIST */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-muted p-1 w-full justify-start md:w-auto">
            <TabsTrigger value="quotas" className="text-xs px-3 py-1.5" id="tab-quotas">Overview & Quotas</TabsTrigger>
            <TabsTrigger value="charts" className="text-xs px-3 py-1.5" id="tab-charts">Usage Charts & Forecasts</TabsTrigger>
            <TabsTrigger value="breakdown" className="text-xs px-3 py-1.5" id="tab-breakdown">Org & Dept Breakdown</TabsTrigger>
          </TabsList>

          {/* TAB 1: OVERVIEW & QUOTAS */}
          <TabsContent value="quotas" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Active Transaction Limits & Quotas</CardTitle>
                <CardDescription>Track remaining allocations across processing engines.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-2">
                
                {/* OCR Progress Meter */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold flex items-center space-x-1.5">
                      <Server className="h-4 w-4 text-primary" />
                      <span>OCR Requests Capacity</span>
                    </span>
                    <span className="text-muted-foreground">{10000 - ocrRemaining} / 10,000 pages ({((10000 - ocrRemaining) / 100).toFixed(0)}% consumed)</span>
                  </div>
                  <div className="w-full bg-muted h-2 rounded overflow-hidden">
                    <div className="bg-primary h-full transition-all duration-500" style={{ width: `${((10000 - ocrRemaining) / 100)}%` }} />
                  </div>
                </div>

                {/* AI Progress Meter */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold flex items-center space-x-1.5">
                      <Sparkles className="h-4 w-4 text-warning" />
                      <span>AI Extractor Requests Capacity</span>
                    </span>
                    <span className="text-muted-foreground">{5000 - aiRemaining} / 5,000 calls ({((5000 - aiRemaining) / 50).toFixed(0)}% consumed)</span>
                  </div>
                  <div className="w-full bg-muted h-2 rounded overflow-hidden">
                    <div className="bg-warning h-full transition-all duration-500" style={{ width: `${((5000 - aiRemaining) / 50)}%` }} />
                  </div>
                </div>

                {/* Documents Uploads Capacity */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold flex items-center space-x-1.5">
                      <FileText className="h-4 w-4 text-success" />
                      <span>Documents Uploads Count</span>
                    </span>
                    <span className="text-muted-foreground">480 / 1,000 files (48% consumed)</span>
                  </div>
                  <div className="w-full bg-muted h-2 rounded overflow-hidden">
                    <div className="bg-success h-full w-[48%]" />
                  </div>
                </div>

                {/* Warnings pane */}
                {aiRemaining < 1000 && (
                  <Alert variant="warning" className="mt-4">
                    <ShieldAlert className="h-4 w-4" />
                    <AlertTitle className="text-xs">Quota Consumptions Warning</AlertTitle>
                    <AlertDescription className="text-[11px]">
                      AI requests quota has consumed over 80% capacity. Consider upgrading plan to prevent extraction blockages.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: CHARTS & FORECASTS */}
          <TabsContent value="charts" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-3">
              
              {/* Daily SVG usage chart */}
              <Card className="md:col-span-2 border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">Daily Processing Volume (Last 7 Days)</CardTitle>
                  <CardDescription>Pages processed across OCR & extraction engines.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2 flex justify-center">
                  {/* SVG Chart */}
                  <svg className="w-full max-w-[500px] h-[200px]" viewBox="0 0 500 200">
                    {/* Grid lines */}
                    <line x1="40" y1="20" x2="480" y2="20" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="70" x2="480" y2="70" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="120" x2="480" y2="120" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="170" x2="480" y2="170" stroke="rgba(255,255,255,0.2)" />
                    
                    {/* Data line */}
                    <path 
                      d="M 60 150 L 120 130 L 180 80 L 240 120 L 300 60 L 360 40 L 420 50" 
                      fill="none" 
                      stroke="var(--primary)" 
                      strokeWidth="3" 
                      strokeLinecap="round"
                    />

                    {/* Chart Points */}
                    <circle cx="60" cy="150" r="5" fill="var(--primary)" />
                    <circle cx="120" cy="130" r="5" fill="var(--primary)" />
                    <circle cx="180" cy="80" r="5" fill="var(--primary)" />
                    <circle cx="240" cy="120" r="5" fill="var(--primary)" />
                    <circle cx="300" cy="60" r="5" fill="var(--primary)" />
                    <circle cx="360" cy="40" r="5" fill="var(--primary)" />
                    <circle cx="420" cy="50" r="5" fill="var(--primary)" />

                    {/* Labels */}
                    <text x="60" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Mon</text>
                    <text x="120" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Tue</text>
                    <text x="180" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Wed</text>
                    <text x="240" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Thu</text>
                    <text x="300" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Fri</text>
                    <text x="360" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Sat</text>
                    <text x="420" y="190" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">Sun</text>
                  </svg>
                </CardContent>
              </Card>

              {/* Forecast Card */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-base font-bold flex items-center space-x-1.5">
                    <BarChart3 className="h-4 w-4 text-primary" />
                    <span>Usage Forecast</span>
                  </CardTitle>
                  <CardDescription>Predictive analysis based on transaction velocity.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="border rounded-lg p-3 bg-muted/10">
                    <span className="text-[10px] font-bold uppercase text-muted-foreground">OCR Projection</span>
                    <div className="text-xl font-bold text-foreground">8,900 / 10,000 pages</div>
                    <p className="text-[9px] text-muted-foreground">Within active quota limits (Confidence: High)</p>
                  </div>

                  <div className="border rounded-lg p-3 bg-muted/10">
                    <span className="text-[10px] font-bold uppercase text-muted-foreground">AI Requests Projection</span>
                    <div className="text-xl font-bold text-warning">5,450 / 5,000 calls</div>
                    <p className="text-[9px] text-warning">Projected over-quota limit (Confidence: High)</p>
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 3: ORG & DEPT BREAKDOWN */}
          <TabsContent value="breakdown" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Departmental Billing Breakdown</CardTitle>
                <CardDescription>Accrued resource usage split between active hospital units.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Hospital Department</TableHead>
                      <TableHead>OCR Pages</TableHead>
                      <TableHead>AI Queries</TableHead>
                      <TableHead>Active Users</TableHead>
                      <TableHead>Storage (GB)</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {departments.map((dept, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="text-xs font-bold text-foreground">{dept.name}</TableCell>
                        <TableCell className="font-mono text-xs text-foreground">{dept.ocrCount.toLocaleString()}</TableCell>
                        <TableCell className="font-mono text-xs text-foreground">{dept.aiCount.toLocaleString()}</TableCell>
                        <TableCell className="font-mono text-xs text-foreground">{dept.userCount}</TableCell>
                        <TableCell className="font-mono text-xs text-foreground">{dept.storageGb.toFixed(1)} GB</TableCell>
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
