/**
 * @file page.tsx
 * @description Medical Terminology Mapping Administration Console.
 * 
 * Provides interactive directories supporting clinical codes lookups, concept diff checkers,
 * mapping approval workflows, audit events catalogs, and bulk export integrations.
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
import { Switch } from "../../../components/ui/switch";
import { 
  FolderSync, Activity, Database, CheckSquare, Trash2, 
  Search, ArrowRight, Play, Loader2, ArrowUpRight, Download, Upload,
  Layers, CheckCircle, ShieldAlert, History
} from "lucide-react";

// --- TYPES ---
interface ConceptMapping {
  id: string;
  sourceSystem: string;
  sourceCode: string;
  targetSystem: string;
  targetCode: string;
  display: string;
  status: "APPROVED" | "PENDING_APPROVAL" | "REJECTED";
  version: number;
}

export default function TerminologyAdministrationPage() {
  // --- STATE STORES ---
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSystem, setSelectedSystem] = useState("All Systems");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [testResult, setTestResult] = useState("");

  // Catalog of mappings
  const [mappings, setMappings] = useState<ConceptMapping[]>([
    { id: "map-1", sourceSystem: "local_lab", sourceCode: "WBC_COUNT", targetSystem: "LOINC", targetCode: "26464-8", display: "White Blood Cell Count", status: "APPROVED", version: 2 },
    { id: "map-2", sourceSystem: "local_lab", sourceCode: "Fasting Glucose", targetSystem: "LOINC", targetCode: "15074-8", display: "Fasting Glucose", status: "APPROVED", version: 2 },
    { id: "map-3", sourceSystem: "local_rx", sourceCode: "MET", targetSystem: "RxNorm", targetCode: "866418", display: "Metformin Tab 500mg", status: "APPROVED", version: 3 },
    { id: "map-4", sourceSystem: "local_lab", sourceCode: "TSH Level", targetSystem: "LOINC", targetCode: "12345-6", display: "Thyroid Stimulating Hormone", status: "PENDING_APPROVAL", version: 4 },
    { id: "map-5", sourceSystem: "local_rx", sourceCode: "Serum Digoxin Level", targetSystem: "RxNorm", targetCode: "3407", display: "Digoxin", status: "PENDING_APPROVAL", version: 4 }
  ]);

  // Diff comparison states
  const [showDiff, setShowDiff] = useState(true);

  // --- CONTROLLER HANDLERS ---

  /**
   * Approves a single proposed mapping rule.
   */
  const handleApproveMapping = (id: string) => {
    setMappings(prev => prev.map(m => {
      if (m.id === id) {
        return { ...m, status: "APPROVED" };
      }
      return m;
    }));
    setTestResult("Mapping rule approved. Concepts resolved successfully.");
    setTimeout(() => setTestResult(""), 3000);
  };

  /**
   * Rejects a proposed mapping rule.
   */
  const handleRejectMapping = (id: string) => {
    setMappings(prev => prev.map(m => {
      if (m.id === id) {
        return { ...m, status: "REJECTED" };
      }
      return m;
    }));
    setTestResult("Mapping rule rejected. Entry ignored in translations.");
    setTimeout(() => setTestResult(""), 3000);
  };

  /**
   * Bulk selection controller.
   */
  const toggleSelectRow = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleBulkApprove = () => {
    if (selectedIds.length === 0) return;
    setMappings(prev => prev.map(m => {
      if (selectedIds.includes(m.id)) {
        return { ...m, status: "APPROVED" };
      }
      return m;
    }));
    setSelectedIds([]);
    setTestResult(`Successfully approved ${selectedIds.length} mappings in bulk.`);
    setTimeout(() => setTestResult(""), 3000);
  };

  /**
   * Mock export action.
   */
  const handleExportMappings = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(mappings, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "fhir_conceptmap_export.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    setTestResult("FHIR ConceptMap JSON exported successfully.");
    setTimeout(() => setTestResult(""), 3000);
  };

  // Filter logic
  const filteredMappings = mappings.filter(m => {
    const matchesSearch = 
      m.sourceCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.targetCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.display.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesSystem = selectedSystem === "All Systems" || m.targetSystem === selectedSystem;
    return matchesSearch && matchesSystem;
  });

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Medical Terminology Mapping</h2>
          <p className="text-sm text-muted-foreground">Manage and resolve local clinical codes to standard LOINC, SNOMED CT, UCUM, ICD-10, and RxNorm system endpoints.</p>
        </div>

        {/* Action feedback notifications banner */}
        {testResult && (
          <Alert variant="success" className="py-2.5">
            <CheckCircle className="h-4 w-4" />
            <AlertTitle className="text-xs">Success</AlertTitle>
            <AlertDescription className="text-[11px]">{testResult}</AlertDescription>
          </Alert>
        )}

        {/* METRICS DASHBOARD */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Mapped Concepts</span>
              <Database className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,248 Rules</div>
              <p className="text-[10px] text-muted-foreground">Active in concept translation tables</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Pending Approvals</span>
              <ShieldAlert className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">4 Mappings</div>
              <p className="text-[10px] text-muted-foreground">Awaiting clinical terminologist review</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Version</span>
              <Layers className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Version v4</div>
              <p className="text-[10px] text-muted-foreground">Rollback available to v1, v2, v3</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Audit Events</span>
              <History className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">84 Logs</div>
              <p className="text-[10px] text-muted-foreground">Clinical review changes tracked</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT COLUMN: REGISTRY & SEARCH */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <FolderSync className="h-5 w-5 text-primary" />
                  <span>Terminology Concept Map Registry</span>
                </CardTitle>
                <CardDescription>Perform queries, select bulk rows, and approve/reject clinical mappings.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 space-y-4">
                
                {/* Search and Filters Bar */}
                <div className="flex flex-col space-y-3 sm:flex-row sm:space-y-0 sm:space-x-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="search-input"
                      placeholder="Search local code or standard mapping..." 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <select 
                    id="system-select"
                    value={selectedSystem} 
                    onChange={(e) => setSelectedSystem(e.target.value)}
                    className="h-10 rounded-md border border-border bg-background px-3 text-xs outline-none w-full sm:w-48"
                  >
                    <option>All Systems</option>
                    <option>LOINC</option>
                    <option>RxNorm</option>
                    <option>SNOMED CT</option>
                    <option>ICD-10</option>
                  </select>
                </div>

                {/* Bulk Actions Console */}
                {selectedIds.length > 0 && (
                  <div className="flex items-center justify-between p-2.5 bg-primary/10 border border-primary/20 rounded-md">
                    <span className="text-xs text-foreground font-semibold">{selectedIds.length} rows selected</span>
                    <div className="flex items-center space-x-2">
                      <Button 
                        id="bulk-approve-btn"
                        variant="default" 
                        size="sm" 
                        onClick={handleBulkApprove} 
                        className="h-8 text-xs flex items-center space-x-1"
                      >
                        <CheckSquare className="h-3.5 w-3.5" />
                        <span>Bulk Approve Mappings</span>
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => setSelectedIds([])} 
                        className="h-8 text-xs text-muted-foreground hover:bg-muted/10"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                {/* Rules Table */}
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-10">Select</TableHead>
                      <TableHead>Source Code</TableHead>
                      <TableHead>Standard System/Code</TableHead>
                      <TableHead>Display Label</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredMappings.map((m, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell>
                          <input 
                            type="checkbox" 
                            checked={selectedIds.includes(m.id)} 
                            onChange={() => toggleSelectRow(m.id)}
                            className="rounded border-border"
                          />
                        </TableCell>
                        <TableCell className="font-mono text-xs font-bold text-foreground">{m.sourceCode}</TableCell>
                        <TableCell className="text-xs">
                          <span className="font-bold text-primary mr-1.5">{m.targetSystem}</span>
                          <span className="font-mono text-muted-foreground">{m.targetCode}</span>
                        </TableCell>
                        <TableCell className="text-xs text-foreground">{m.display}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={m.status === "APPROVED" ? "success" : m.status === "PENDING_APPROVAL" ? "warning" : "error"}
                            className="text-[10px] px-2 py-0.5"
                          >
                            {m.status === "PENDING_APPROVAL" ? "PENDING" : m.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right space-x-1.5">
                          {m.status === "PENDING_APPROVAL" ? (
                            <>
                              <Button 
                                id={`approve-${m.sourceCode.toLowerCase().replace(/\s+/g, "-")}`}
                                variant="default" 
                                size="sm" 
                                onClick={() => handleApproveMapping(m.id)}
                                className="bg-success hover:bg-success/80 text-white h-7 px-2 text-xs"
                              >
                                Approve
                              </Button>
                              <Button 
                                id={`reject-${m.sourceCode.toLowerCase().replace(/\s+/g, "-")}`}
                                variant="ghost" 
                                size="sm" 
                                onClick={() => handleRejectMapping(m.id)}
                                className="text-error hover:bg-error/10 h-7 px-2 text-xs"
                              >
                                Reject
                              </Button>
                            </>
                          ) : (
                            <span className="text-[10px] text-muted-foreground">Version v{m.version}</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* VERSION DIFF VISUAL CHECKER */}
            {showDiff && (
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex items-center space-x-2">
                    <Layers className="h-5 w-5 text-primary" />
                    <span>Concept Map Version Diff Viewer</span>
                  </CardTitle>
                  <CardDescription>Compare modified mapping rules between v3 and v4.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <div className="rounded-lg border overflow-hidden font-mono text-[11px]">
                    <div className="grid grid-cols-2 bg-muted p-2 border-b text-muted-foreground font-bold">
                      <span>Version v3 (Previous)</span>
                      <span>Version v4 (Active)</span>
                    </div>
                    <div className="p-3 space-y-1 bg-background/30 max-h-[160px] overflow-y-auto">
                      <div className="text-muted-foreground">  local_rx:MET -&gt; RxNorm:866418 (Approved)</div>
                      <div className="flex bg-error/10 text-error p-0.5 rounded">
                        <span className="w-1/2">- None</span>
                        <span className="w-1/2"> </span>
                      </div>
                      <div className="flex bg-success/10 text-success p-0.5 rounded">
                        <span className="w-1/2"> </span>
                        <span className="w-1/2">+ local_lab:TSH Level -&gt; LOINC:12345-6 (Pending)</span>
                      </div>
                      <div className="flex bg-success/10 text-success p-0.5 rounded">
                        <span className="w-1/2"> </span>
                        <span className="w-1/2">+ local_rx:Serum Digoxin Level -&gt; RxNorm:3407 (Pending)</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* RIGHT COLUMN: IMPORT/EXPORT & AUDIT TIMELINE */}
          <div className="space-y-6">
            
            {/* Import / Export Card Console */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <Download className="h-4.5 w-4.5 text-primary" />
                  <span>Import & Export Mappings</span>
                </CardTitle>
                <CardDescription>Synchronize mappings via FHIR JSON structures.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 pt-1">
                
                <Button 
                  id="export-btn"
                  variant="outline" 
                  onClick={handleExportMappings} 
                  className="w-full flex items-center justify-between text-xs"
                >
                  <span className="flex items-center space-x-2">
                    <Download className="h-4 w-4" />
                    <span>Export ConceptMap JSON</span>
                  </span>
                  <ArrowUpRight className="h-3.5 w-3.5 text-muted-foreground" />
                </Button>

                <div className="border border-dashed border-border rounded-lg p-4 text-center space-y-2 hover:bg-muted/10 transition-all cursor-pointer">
                  <Upload className="h-5 w-5 text-muted-foreground mx-auto" />
                  <span className="block text-xs font-bold text-foreground">Import mapping rules</span>
                  <span className="block text-[10px] text-muted-foreground">Upload CSV, Excel, or FHIR JSON file</span>
                </div>

              </CardContent>
            </Card>

            {/* AUDIT LOG TIMELINE */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <History className="h-4.5 w-4.5 text-primary" />
                  <span>Audit History Timeline</span>
                </CardTitle>
                <CardDescription>Revision logs and rollbacks events.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1">
                <div className="relative pl-5 space-y-4 border-l border-border/60 text-xs">
                  
                  <div className="relative space-y-0.5">
                    <span className="absolute -left-[27px] top-0.5 h-3.5 w-3.5 rounded-full bg-success flex items-center justify-center text-white border border-background">
                      ✓
                    </span>
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="font-bold text-foreground">Version v4</span>
                      <span className="text-muted-foreground font-mono">10m ago</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Proposed TSH and Digoxin local mappings</p>
                  </div>

                  <div className="relative space-y-0.5">
                    <span className="absolute -left-[27px] top-0.5 h-3.5 w-3.5 rounded-full bg-success flex items-center justify-center text-white border border-background">
                      ✓
                    </span>
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="font-bold text-foreground">Version v3</span>
                      <span className="text-muted-foreground font-mono">1h ago</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Approved Metformin local RxNorm mapping</p>
                  </div>

                  <div className="relative space-y-0.5">
                    <span className="absolute -left-[27px] top-0.5 h-3.5 w-3.5 rounded-full bg-success flex items-center justify-center text-white border border-background">
                      ✓
                    </span>
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="font-bold text-foreground">Version v2</span>
                      <span className="text-muted-foreground font-mono">1d ago</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Approved Fasting Glucose mapping</p>
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
