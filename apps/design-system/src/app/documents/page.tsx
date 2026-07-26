"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { 
  FileText, CheckCircle2, AlertTriangle, AlertCircle, Search, 
  ChevronDown, History, ShieldAlert, ArrowUpDown, Filter, Bookmark, Archive
} from "lucide-react";

export default function DocumentsPage() {
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Mock list of 15 documents to simulate high density list / virtual scrolling
  const [docs, setDocs] = useState([
    { id: "DF-1001", name: "Elizabeth Blackwell", type: "Lab Report", date: "2026-07-26", status: "Approved", version: "v2", tag: "Urgent" },
    { id: "DF-1002", name: "Arthur Conan Doyle", type: "Prescription", date: "2026-07-26", status: "Approved", version: "v1", tag: "Routine" },
    { id: "DF-1003", name: "Mary Edwards Walker", type: "Diagnostic Chart", date: "2026-07-25", status: "Failed", version: "v3", tag: "Audit Fail" },
    { id: "DF-1004", name: "William Osler", type: "Lab Report", date: "2026-07-25", status: "Approved", version: "v1", tag: "Normal" },
    { id: "DF-1005", name: "Edward Jenner", type: "Immunization Record", date: "2026-07-24", status: "Review Required", version: "v2", tag: "Pending" },
    { id: "DF-1006", name: "Florence Nightingale", type: "Lab Report", date: "2026-07-24", status: "Approved", version: "v1", tag: "Normal" },
    { id: "DF-1007", name: "Louis Pasteur", type: "Clinical Summary", date: "2026-07-23", status: "Approved", version: "v2", tag: "Urgent" },
    { id: "DF-1008", name: "Jonas Salk", type: "Lab Report", date: "2026-07-23", status: "Failed", version: "v1", tag: "Audit Fail" },
    { id: "DF-1009", name: "Alexander Fleming", type: "Prescription", date: "2026-07-22", status: "Approved", version: "v1", tag: "Routine" },
    { id: "DF-1010", name: "Joseph Lister", type: "Lab Report", date: "2026-07-22", status: "Review Required", version: "v3", tag: "Pending" },
  ]);

  const [selectedDocDetails, setSelectedDocDetails] = useState(docs[0]);

  // Version History mock
  const versionHistory = [
    { ver: "v2", date: "2026-07-26 14:30", user: "Kalyan Kalwa", action: "Updated patient demographics metadata details" },
    { ver: "v1", date: "2026-07-26 12:15", user: "System OCR", action: "Extracted baseline values from ingested fax file" }
  ];

  // Audit Trails logs mock
  const auditLogs = [
    { time: "2026-07-26 14:32", msg: "Outbound EHR export transaction completed successfully to Epic Sandbox" },
    { time: "2026-07-26 14:30", msg: "Demographics schema approved under Medplum validators" },
    { time: "2026-07-26 12:16", msg: "NATS intake dispatch received and indexed in OpenSearch cluster" }
  ];

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedDocs(docs.map((d) => d.id));
    } else {
      setSelectedDocs([]);
    }
  };

  const handleSelectDoc = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedDocs((prev) => [...prev, id]);
    } else {
      setSelectedDocs((prev) => prev.filter((d) => d !== id));
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Document Repository</h2>
            <p className="text-sm text-muted-foreground">Manage, search, and audit all parsed clinical records.</p>
          </div>

          {/* Bulk actions selector */}
          {selectedDocs.length > 0 && (
            <div className="flex items-center space-x-2 bg-muted p-2 rounded-lg border border-border">
              <span className="text-xs font-semibold px-2">{selectedDocs.length} selected</span>
              <Button variant="default" size="sm">Approve Selected</Button>
              <Button variant="outline" size="sm">Export to Epic</Button>
              <Button variant="ghost" size="sm" className="text-error hover:bg-error/10">Delete</Button>
            </div>
          )}
        </div>

        {/* Master column grid */}
        <div className="grid gap-6 lg:grid-cols-4">
          
          {/* 1. FILTER SIDEBAR (Span 1) */}
          <div className="space-y-6">
            
            {/* Saved Searches */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <Bookmark className="h-4 w-4 text-primary" />
                  <span>Saved Searches</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                <Button 
                  variant={activeTab === "all" ? "default" : "ghost"} 
                  className="w-full justify-start text-xs font-medium"
                  onClick={() => setActiveTab("all")}
                >
                  All Ingested Documents
                </Button>
                <Button 
                  variant={activeTab === "critical" ? "default" : "ghost"} 
                  className="w-full justify-start text-xs font-medium text-error hover:text-error hover:bg-error/5"
                  onClick={() => setActiveTab("critical")}
                >
                  Critical Audit Failures
                </Button>
                <Button 
                  variant={activeTab === "pending" ? "default" : "ghost"} 
                  className="w-full justify-start text-xs font-medium text-warning hover:text-warning hover:bg-warning/5"
                  onClick={() => setActiveTab("pending")}
                >
                  Pending Manual Review
                </Button>
              </CardContent>
            </Card>

            {/* Advanced Filters */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-primary" />
                  <span>Advanced Filters</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-2">
                <div className="space-y-2">
                  <label className="text-[10px] font-semibold uppercase text-muted-foreground">Document Type</label>
                  <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                    <option>All Types</option>
                    <option>Lab Report</option>
                    <option>Prescription</option>
                    <option>Diagnostic Chart</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-semibold uppercase text-muted-foreground">Time Period</label>
                  <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                    <option>Last 24 Hours</option>
                    <option>Last 7 Days</option>
                    <option>Last 30 Days</option>
                  </select>
                </div>
              </CardContent>
            </Card>

          </div>

          {/* 2. MAIN DOCUMENT LIST TABLE (Span 2) */}
          <div className="lg:col-span-2 space-y-4">
            
            {/* Search and Sort controls */}
            <div className="flex items-center space-x-3 bg-muted/40 p-3 rounded-lg border border-border">
              <div className="relative flex-1">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Search patient name, ID, or tag..." 
                  className="pl-9 h-9" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                className="flex items-center space-x-2 shrink-0"
              >
                <ArrowUpDown className="h-4 w-4" />
                <span>Sort ({sortOrder})</span>
              </Button>
            </div>

            {/* Document list table */}
            <div className="rounded-md border border-border bg-background overflow-hidden">
              <div className="max-h-[500px] overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-background z-10">
                    <TableRow>
                      <TableHead className="w-[50px] p-4">
                        <input 
                          type="checkbox"
                          checked={selectedDocs.length === docs.length}
                          onChange={(e) => handleSelectAll(e.target.checked)}
                          className="rounded border-border bg-background"
                        />
                      </TableHead>
                      <TableHead>Patient Details</TableHead>
                      <TableHead>Type / Version</TableHead>
                      <TableHead>Status / Tag</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {docs.map((doc, idx) => (
                      <TableRow 
                        key={idx} 
                        className={`cursor-pointer transition-colors ${
                          selectedDocDetails.id === doc.id ? "bg-muted/50" : "hover:bg-muted/20"
                        }`}
                        onClick={() => setSelectedDocDetails(doc)}
                      >
                        <TableCell className="p-4" onClick={(e) => e.stopPropagation()}>
                          <input 
                            type="checkbox"
                            checked={selectedDocs.includes(doc.id)}
                            onChange={(e) => handleSelectDoc(doc.id, e.target.checked)}
                            className="rounded border-border bg-background"
                          />
                        </TableCell>
                        <TableCell>
                          <p className="font-semibold text-sm">{doc.name}</p>
                          <p className="text-xs text-muted-foreground">{doc.id} • Ingested: {doc.date}</p>
                        </TableCell>
                        <TableCell>
                          <p className="text-sm font-medium">{doc.type}</p>
                          <span className="text-xs font-semibold text-muted-foreground">{doc.version}</span>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <Badge 
                              variant={
                                doc.status === "Approved" ? "success" :
                                doc.status === "Review Required" ? "warning" : "error"
                              }
                            >
                              {doc.status}
                            </Badge>
                            <div>
                              <span className="text-[10px] font-semibold text-primary/80 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
                                {doc.tag}
                              </span>
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

          </div>

          {/* 3. DOCUMENT DETAILS & AUDIT TIMELINE (Span 1) */}
          <div className="space-y-6">
            
            {/* Version History */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <History className="h-5 w-5 text-primary" />
                  <span>Version History</span>
                </CardTitle>
                <CardDescription className="text-xs">
                  Active Document: **{selectedDocDetails.id}** ({selectedDocDetails.name})
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {versionHistory.map((v, idx) => (
                  <div key={idx} className="border-l-2 border-primary pl-3 py-1 text-xs">
                    <p className="font-semibold">{v.ver} • {v.user}</p>
                    <p className="text-muted-foreground mt-0.5">{v.action}</p>
                    <span className="text-[10px] text-muted-foreground">{v.date}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Audit Logs Trail */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <ShieldAlert className="h-5 w-5 text-warning" />
                  <span>Audit Logs Trail</span>
                </CardTitle>
                <CardDescription className="text-xs">
                  Regulatory schema verification checklist
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {auditLogs.map((log, idx) => (
                  <div key={idx} className="space-y-1 text-xs border-b border-border pb-2 last:border-b-0">
                    <p className="text-foreground">{log.msg}</p>
                    <span className="text-[10px] text-muted-foreground">{log.time}</span>
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
