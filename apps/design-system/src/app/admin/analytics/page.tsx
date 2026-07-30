/**
 * @file page.tsx
 * @description Executive Analytics Dashboard.
 * 
 * Provides Executive, Operations, Clinical, IT, Security, Compliance, Revenue,
 * Tenant Health, Document Processing, and Workflow Performance dashboards.
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
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../../components/ui/tabs";
import { 
  BarChart3, Activity, Users, ShieldCheck, Scale, DollarSign, Heart, 
  Settings, Database, CheckCircle, Share2, Download, Save, Plus, Trash2
} from "lucide-react";

// --- TYPES ---
interface SavedDashboard {
  id: string;
  name: string;
  tab: string;
  filters: string;
}

export default function AnalyticsAdministrationPage() {
  // --- STATE STORES ---
  const [activeTab, setActiveTab] = useState("executive");
  const [dateRange, setDateRange] = useState("last-30");
  const [department, setDepartment] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const [savedDashboards, setSavedDashboards] = useState<SavedDashboard[]>([
    { id: "saved-1", name: "Monthly Operational Overview", tab: "operations", filters: "Last 30 Days | All Depts" },
    { id: "saved-2", name: "Compliance & Security Health Check", tab: "compliance", filters: "Last 30 Days | Cardiology" }
  ]);

  const [newDashboardName, setNewDashboardName] = useState("");
  const [shareSuccess, setShareSuccess] = useState(false);
  const [exportAlert, setExportAlert] = useState<string | null>(null);

  // --- HANDLERS ---

  /**
   * Saves the current dashboard configuration view.
   */
  const handleSaveDashboard = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDashboardName.trim()) return;

    const newDash: SavedDashboard = {
      id: `saved-${Date.now()}`,
      name: newDashboardName,
      tab: activeTab,
      filters: `${dateRange === "last-30" ? "Last 30 Days" : "Last 7 Days"} | ${department.toUpperCase()}`
    };

    setSavedDashboards(prev => [...prev, newDash]);
    setNewDashboardName("");
  };

  /**
   * Deletes a saved dashboard configuration view.
   */
  const handleDeleteSavedDashboard = (id: string) => {
    setSavedDashboards(prev => prev.filter(d => d.id !== id));
  };

  /**
   * Simulates dashboard view load.
   */
  const handleLoadSavedDashboard = (dash: SavedDashboard) => {
    setActiveTab(dash.tab);
  };

  /**
   * Simulates report export triggers.
   */
  const handleExport = (format: string) => {
    setExportAlert(`Exported current ${activeTab.toUpperCase()} dashboard view to ${format} file format.`);
    setTimeout(() => setExportAlert(null), 3000);
  };

  /**
   * Simulates sharing URLs copy.
   */
  const handleShare = () => {
    setShareSuccess(true);
    setTimeout(() => setShareSuccess(false), 2000);
  };

  // --- MOCK SVG CHART GENERATORS ---
  const renderSVGChart = (tabName: string) => {
    switch (tabName) {
      case "executive":
        return (
          <svg className="w-full max-w-[500px] h-[180px]" viewBox="0 0 500 180">
            {/* Executive SVG: Line graph showing costs/accerals */}
            <line x1="40" y1="20" x2="480" y2="20" stroke="rgba(255,255,255,0.05)" />
            <line x1="40" y1="80" x2="480" y2="80" stroke="rgba(255,255,255,0.05)" />
            <line x1="40" y1="140" x2="480" y2="140" stroke="rgba(255,255,255,0.2)" />
            <path d="M 60 120 L 140 110 L 220 70 L 300 90 L 380 40 L 460 30" fill="none" stroke="var(--primary)" strokeWidth="3" strokeLinecap="round" />
            <circle cx="60" cy="120" r="4" fill="var(--primary)" />
            <circle cx="140" cy="110" r="4" fill="var(--primary)" />
            <circle cx="220" cy="70" r="4" fill="var(--primary)" />
            <circle cx="300" cy="90" r="4" fill="var(--primary)" />
            <circle cx="380" cy="40" r="4" fill="var(--primary)" />
            <circle cx="460" cy="30" r="4" fill="var(--primary)" />
          </svg>
        );
      case "operations":
        return (
          <svg className="w-full max-w-[500px] h-[180px]" viewBox="0 0 500 180">
            {/* Operations SVG: Bar chart for volumes */}
            <rect x="60" y="80" width="30" height="60" fill="var(--primary)" rx="2" />
            <rect x="140" y="50" width="30" height="90" fill="var(--primary)" rx="2" />
            <rect x="220" y="30" width="30" height="110" fill="var(--primary)" rx="2" />
            <rect x="300" y="60" width="30" height="80" fill="var(--primary)" rx="2" />
            <rect x="380" y="20" width="30" height="120" fill="var(--primary)" rx="2" />
            <rect x="460" y="40" width="30" height="100" fill="var(--primary)" rx="2" />
            <line x1="40" y1="140" x2="480" y2="140" stroke="rgba(255,255,255,0.2)" />
          </svg>
        );
      case "revenue":
        return (
          <svg className="w-full max-w-[500px] h-[180px]" viewBox="0 0 500 180">
            {/* Revenue SVG: Multi-line chart */}
            <line x1="40" y1="140" x2="480" y2="140" stroke="rgba(255,255,255,0.2)" />
            <path d="M 60 130 L 140 100 L 220 90 L 300 60 L 380 50 L 460 20" fill="none" stroke="var(--primary)" strokeWidth="3" strokeLinecap="round" />
            <path d="M 60 140 L 140 120 L 220 110 L 300 90 L 380 70 L 460 50" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="2" strokeLinecap="round" />
          </svg>
        );
      default:
        return (
          <svg className="w-full max-w-[500px] h-[180px]" viewBox="0 0 500 180">
            {/* Fallback chart */}
            <line x1="40" y1="140" x2="480" y2="140" stroke="rgba(255,255,255,0.2)" />
            <path d="M 60 100 Q 250 20 460 100" fill="none" stroke="var(--primary)" strokeWidth="2" />
          </svg>
        );
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Executive Analytics</h2>
            <p className="text-sm text-muted-foreground">Monitor high-level clinical processing trends, system operations, and security profiles.</p>
          </div>
          
          {/* EXPORTS & SHARING CONTROL BAR */}
          <div className="mt-4 md:mt-0 flex flex-wrap gap-2 items-center">
            <Button 
              onClick={() => handleExport("PDF")} 
              className="bg-muted hover:bg-muted/80 text-foreground text-xs flex items-center space-x-1 h-9 px-3"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export PDF</span>
            </Button>
            <Button 
              onClick={() => handleExport("CSV")} 
              className="bg-muted hover:bg-muted/80 text-foreground text-xs flex items-center space-x-1 h-9 px-3"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export CSV</span>
            </Button>
            <Button 
              id="btn-share-dashboard"
              onClick={handleShare} 
              className="bg-primary hover:bg-primary/80 text-foreground text-xs flex items-center space-x-1.5 h-9 px-3"
            >
              <Share2 className="h-3.5 w-3.5" />
              <span>{shareSuccess ? "Copied Link!" : "Share View"}</span>
            </Button>
          </div>
        </div>

        {/* DIAGNOSTIC POPUPS */}
        {exportAlert && (
          <Alert variant="success" className="animate-fade-in">
            <CheckCircle className="h-4 w-4" />
            <AlertTitle className="text-xs">Export Confirmed</AlertTitle>
            <AlertDescription className="text-[11px]">{exportAlert}</AlertDescription>
          </Alert>
        )}

        {/* FILTER BAR ROW */}
        <Card className="border border-border/80 bg-background/50">
          <CardContent className="p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4 items-center w-full md:w-auto">
              <div className="space-y-1">
                <span className="text-[10px] font-semibold text-muted-foreground uppercase block">Date Range Filter</span>
                <select 
                  id="select-date-range"
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="bg-muted border border-border rounded px-3 py-1.5 text-xs text-foreground focus:outline-none"
                >
                  <option value="last-7">Last 7 Days</option>
                  <option value="last-30">Last 30 Days</option>
                  <option value="last-90">Last 90 Days</option>
                </select>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] font-semibold text-muted-foreground uppercase block">Department Filter</span>
                <select 
                  id="select-department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="bg-muted border border-border rounded px-3 py-1.5 text-xs text-foreground focus:outline-none"
                >
                  <option value="all">All Departments</option>
                  <option value="cardiology">Cardiology</option>
                  <option value="emergency">Emergency Dept</option>
                  <option value="pediatrics">Pediatrics</option>
                </select>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] font-semibold text-muted-foreground uppercase block">Status Filter</span>
                <select 
                  id="select-status"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-muted border border-border rounded px-3 py-1.5 text-xs text-foreground focus:outline-none"
                >
                  <option value="all">All Statuses</option>
                  <option value="success">Success</option>
                  <option value="warn">Warnings</option>
                  <option value="error">Errors</option>
                </select>
              </div>
            </div>

            {/* SAVED DASHBOARDS FORM */}
            <form onSubmit={handleSaveDashboard} className="flex gap-2 items-end w-full md:w-auto">
              <div className="space-y-1 w-full md:w-48">
                <label htmlFor="input-save-name" className="text-[10px] font-semibold text-muted-foreground uppercase block">Save current layout</label>
                <Input 
                  id="input-save-name"
                  placeholder="Dashboard Name..." 
                  value={newDashboardName}
                  onChange={(e) => setNewDashboardName(e.target.value)}
                  className="h-8 text-xs bg-muted/20"
                />
              </div>
              <Button 
                id="btn-save-dashboard"
                type="submit" 
                className="bg-success hover:bg-success/80 text-foreground h-8 px-3 text-xs flex items-center space-x-1"
              >
                <Save className="h-3 w-3" />
                <span>Save View</span>
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* TABS CONTAINER */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-muted p-1 w-full justify-start">
            <TabsTrigger value="executive" className="text-xs px-3 py-1.5" id="tab-exec">Executive</TabsTrigger>
            <TabsTrigger value="operations" className="text-xs px-3 py-1.5" id="tab-ops">Operations</TabsTrigger>
            <TabsTrigger value="clinical" className="text-xs px-3 py-1.5" id="tab-clinical">Clinical</TabsTrigger>
            <TabsTrigger value="it" className="text-xs px-3 py-1.5" id="tab-it">IT</TabsTrigger>
            <TabsTrigger value="security" className="text-xs px-3 py-1.5" id="tab-security">Security</TabsTrigger>
            <TabsTrigger value="compliance" className="text-xs px-3 py-1.5" id="tab-compliance">Compliance</TabsTrigger>
            <TabsTrigger value="revenue" className="text-xs px-3 py-1.5" id="tab-rev">Revenue</TabsTrigger>
            <TabsTrigger value="tenant" className="text-xs px-3 py-1.5" id="tab-tenant">Tenant Health</TabsTrigger>
            <TabsTrigger value="docs" className="text-xs px-3 py-1.5" id="tab-docs">Doc Processing</TabsTrigger>
            <TabsTrigger value="workflow" className="text-xs px-3 py-1.5" id="tab-workflow">Workflow Performance</TabsTrigger>
          </TabsList>

          <div className="grid gap-6 lg:grid-cols-3">
            
            {/* SVG CHART PANEL */}
            <Card className="lg:col-span-2 border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold uppercase flex items-center space-x-1.5">
                  <BarChart3 className="h-5 w-5 text-primary" />
                  <span>{activeTab} Analytics Trend</span>
                </CardTitle>
                <CardDescription>Visual metrics over the selected period.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 flex justify-center py-8">
                {renderSVGChart(activeTab)}
              </CardContent>
            </Card>

            {/* SAVED DASHBOARDS SIDEBAR */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold">Saved Dashboards Preset</CardTitle>
                <CardDescription>Load custom configurations view layouts.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 space-y-4">
                {savedDashboards.length === 0 ? (
                  <div className="text-center py-10 text-muted-foreground text-xs">
                    No custom layouts saved yet.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {savedDashboards.map((d, idx) => (
                      <div key={idx} className="border rounded-lg p-3 bg-muted/10 flex justify-between items-center">
                        <div 
                          className="space-y-1 cursor-pointer w-full"
                          onClick={() => handleLoadSavedDashboard(d)}
                        >
                          <span className="font-bold text-xs text-foreground block hover:text-primary">{d.name}</span>
                          <span className="text-[9px] text-muted-foreground block">
                            Type: {d.tab.toUpperCase()} | Filters: {d.filters}
                          </span>
                        </div>
                        <Button 
                          onClick={() => handleDeleteSavedDashboard(d.id)} 
                          className="bg-transparent hover:bg-error/20 text-muted-foreground hover:text-error h-8 w-8 p-0"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

          </div>

          {/* TAB CONTENTS (DETAILS GRID SUMMARY CARDS) */}
          <TabsContent value="executive" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Org Accrued cost</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">$12,410.50</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Total Ingestions</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">142,500 faxes</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">SOC2 Status</span></CardHeader>
                <CardContent><div className="text-2xl font-bold text-success">Compliant</div></CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="operations" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Processing Time</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">12.8s avg</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Reviewer Productivity</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">45.2s per review</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Success Rate</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">99.8%</div></CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="revenue" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Cardiology cost</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">$4,500.00</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Emergency cost</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">$2,850.00</div></CardContent>
              </Card>
              <Card className="border border-border/80 bg-background/50">
                <CardHeader><span className="text-xs uppercase text-muted-foreground">Pediatrics cost</span></CardHeader>
                <CardContent><div className="text-2xl font-bold">$920.00</div></CardContent>
              </Card>
            </div>
          </TabsContent>

        </Tabs>

      </div>
    </AppShell>
  );
}
