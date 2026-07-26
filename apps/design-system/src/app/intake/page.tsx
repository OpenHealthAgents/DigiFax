"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { 
  UploadCloud, FileText, CheckCircle2, AlertTriangle, AlertCircle, 
  Trash2, ArrowRight, Layers, Database, Activity, RefreshCw 
} from "lucide-react";

export default function IntakePage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([
    { name: "blood_chemistry_blackwell.pdf", size: "1.4 MB", progress: 100, status: "Success", ocr: "96.4%" },
    { name: "lipid_profile_doyle.pdf", size: "850 KB", progress: 100, status: "Success", ocr: "98.1%" },
    { name: "urinalysis_walker_dup.pdf", size: "1.1 MB", progress: 100, status: "Duplicate", ocr: "71.0%" },
    { name: "metabolic_panel_osler.pdf", size: "2.1 MB", progress: 45, status: "Processing", ocr: "Analyzing..." },
  ]);

  const [patientSearch, setPatientSearch] = useState("Elizabeth Blackwell");
  const [selectedOrg, setSelectedOrg] = useState("OpenHealth Hospital");
  const [docType, setDocType] = useState("Lab Report");

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    // Simulate drop item
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFile = {
        name: e.dataTransfer.files[0].name,
        size: `${(e.dataTransfer.files[0].size / (1024 * 1024)).toFixed(1)} MB`,
        progress: 0,
        status: "Processing",
        ocr: "Queuing..."
      };
      setUploadedFiles((prev) => [newFile, ...prev]);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Document Intake Workspace</h2>
          <p className="text-sm text-muted-foreground">Upload and catalog clinical fax documents in batch streams.</p>
        </div>

        {/* Workspace split grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT COLUMN: UPLOAD CONTROLS (Span 2) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Drag & Drop Zone */}
            <div 
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
                dragActive ? "border-primary bg-primary/5" : "border-border hover:bg-muted/10"
              }`}
            >
              <UploadCloud className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="font-semibold text-lg">Drag & Drop Fax Documents Here</p>
              <p className="text-xs text-muted-foreground mt-2">Supports PDF, TIFF, PNG up to 25MB per file</p>
              <Button variant="outline" className="mt-4">Select Files manually</Button>
            </div>

            {/* Ingested Uploads Queue */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div>
                  <CardTitle className="text-lg font-bold">Ingested Uploads Queue</CardTitle>
                  <CardDescription>Documents undergoing parsing and AI clinical extraction</CardDescription>
                </div>
                <Badge variant="default" className="text-xs">{uploadedFiles.length} files total</Badge>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {uploadedFiles.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border border-border rounded-lg bg-background hover:shadow-sm transition-shadow">
                    <div className="flex items-center space-x-3 min-w-0 flex-1 mr-4">
                      <FileText className="h-8 w-8 text-primary/70 shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold truncate">{file.name}</p>
                        <p className="text-xs text-muted-foreground">{file.size} • OCR: {file.ocr}</p>
                        
                        {/* Progress Bar */}
                        {file.progress < 100 && (
                          <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-2 max-w-xs">
                            <div className="h-full bg-primary" style={{ width: `${file.progress}%` }} />
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <Badge 
                        variant={
                          file.status === "Success" ? "success" :
                          file.status === "Duplicate" ? "warning" : "default"
                        }
                      >
                        {file.status}
                      </Badge>
                      <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-error">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

          </div>

          {/* RIGHT COLUMN: METADATA & PREVIEW (Span 1) */}
          <div className="space-y-6">
            
            {/* Metadata Editor card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-bold">Metadata Editor & Preview</CardTitle>
                <CardDescription>Verify clinical identifiers mapped by pipeline extraction</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                
                {/* Document preview mock box */}
                <div className="relative aspect-[3/4] w-full rounded-md border border-border bg-muted/20 flex items-center justify-center overflow-hidden">
                  <FileText className="h-12 w-12 text-muted-foreground/40" />
                  <span className="absolute bottom-2 right-2 text-[10px] text-muted-foreground/60 font-mono">PAGE 1 OF 3</span>
                </div>

                {/* Duplicate warning card */}
                <div className="flex items-start space-x-3 p-3 bg-warning/10 text-warning border border-warning/30 rounded-lg text-xs">
                  <AlertTriangle className="h-5 w-5 shrink-0" />
                  <div>
                    <p className="font-semibold">Duplicate Document Detected</p>
                    <p className="mt-1 text-muted-foreground">A document containing matching OCR hash variables was uploaded 3 hours ago.</p>
                  </div>
                </div>

                {/* Form fields */}
                <div className="space-y-3 border-t border-border pt-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Patient Lookup</label>
                    <Input value={patientSearch} onChange={(e) => setPatientSearch(e.target.value)} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Date of Birth</label>
                    <Input type="date" defaultValue="1988-05-12" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Organization Target</label>
                    <Input value={selectedOrg} onChange={(e) => setSelectedOrg(e.target.value)} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Document Type</label>
                    <Input value={docType} onChange={(e) => setDocType(e.target.value)} />
                  </div>
                </div>

                {/* Pipeline Node Map Progress */}
                <div className="border-t border-border pt-4 space-y-3">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Ingest Pipeline Progress</span>
                  
                  <div className="grid grid-cols-4 gap-1 text-center text-[10px] font-semibold">
                    <div className="bg-success/15 text-success rounded py-1.5 border border-success/30">Ingest</div>
                    <div className="bg-success/15 text-success rounded py-1.5 border border-success/30">OCR</div>
                    <div className="bg-primary/10 text-primary rounded py-1.5 border border-primary/20 animate-pulse">Extract</div>
                    <div className="bg-muted text-muted-foreground rounded py-1.5 border border-border">Export</div>
                  </div>
                </div>

                {/* Confirm actions */}
                <div className="flex justify-end pt-4 space-x-2">
                  <Button variant="outline">Discard Fax</Button>
                  <Button variant="default">Verify Metadata</Button>
                </div>

              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
