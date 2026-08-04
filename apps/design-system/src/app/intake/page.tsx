/**
 * @file page.tsx
 * @description MedIngest Ingestion Workspace. Manages document intake pipelines, including manual uploads,
 * drag-and-drop triggers, metadata parsing previews, duplicate warn blocks, and backend uploads connector.
 */

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

// Structure definition for files managed inside the intake queue
interface UploadedFileType {
  id: string;
  name: string;
  size: string;
  progress: number;
  status: string;
  ocr: string;
  docId?: string;
}

export default function IntakePage() {
  // Drag zone hover state indicators
  const [dragActive, setDragActive] = useState(false);

  // Queue of uploaded files, initialized with mock values
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileType[]>([
    { id: "mock-1", name: "blood_chemistry_blackwell.pdf", size: "1.4 MB", progress: 100, status: "Success", ocr: "96.4%", docId: "df_doc_8a7c29b" },
    { id: "mock-2", name: "lipid_profile_doyle.pdf", size: "850 KB", progress: 100, status: "Success", ocr: "98.1%", docId: "df_doc_90b1e4c" },
    { id: "mock-3", name: "urinalysis_walker_dup.pdf", size: "1.1 MB", progress: 100, status: "Duplicate", ocr: "71.0%", docId: "df_doc_cd0193e" },
    { id: "mock-4", name: "metabolic_panel_osler.pdf", size: "2.1 MB", progress: 45, status: "Processing", ocr: "Analyzing..." },
  ]);

  // Form input field configurations
  const [patientSearch, setPatientSearch] = useState("Elizabeth Blackwell");
  const [selectedOrg, setSelectedOrg] = useState("OpenHealth Hospital");
  const [docType, setDocType] = useState("Lab Report");
  const [sourceChannel, setSourceChannel] = useState("FAX_UPLOAD");

  // Track hover state when dragging faxes
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  /**
   * Upload file logic that connects to FastAPI backend /api/intake/upload
   * Creates a multipart FormData boundary, dispatches it to the controller,
   * and updates queue progress states.
   */
  const uploadFile = async (file: File) => {
    const tempFileId = Math.random().toString();
    const newFile: UploadedFileType = {
      id: tempFileId,
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      progress: 20,
      status: "Processing",
      ocr: "Uploading..."
    };
    setUploadedFiles((prev) => [newFile, ...prev]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("source", sourceChannel);

      // Executes the fetch API proxy call to FastAPI
      const response = await fetch("/api/intake/upload", {
        method: "POST",
        headers: {
          "X-Tenant-ID": "tenant-123"
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      
      // Update queue card with success states and returned doc ID
      setUploadedFiles((prev) =>
        prev.map((item) =>
          item.id === tempFileId
            ? { ...item, progress: 100, status: "Success", ocr: "Completed", docId: data.document_id }
            : item
        )
      );
    } catch (error) {
      console.error(error);
      // Fallback state on network failures
      setUploadedFiles((prev) =>
        prev.map((item) =>
          item.id === tempFileId
            ? { ...item, progress: 100, status: "Error", ocr: "Failed" }
            : item
        )
      );
    }
  };

  // Intercept dropped files and pass them to the ingestion pipeline
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  // Remove elements from list view
  const handleDelete = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Workspace Title bar */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Document Intake Workspace</h2>
          <p className="text-sm text-muted-foreground">Upload and catalog clinical documents (faxes, email attachments, scanned files) in batch streams.</p>
        </div>

        {/* Master layout split grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT SECTION: UPLOAD & QUEUES PANELS (Span 2) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Drag & Drop File Zone */}
            <div 
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer relative ${
                dragActive ? "border-primary bg-primary/5" : "border-border hover:bg-muted/10"
              }`}
            >
              <UploadCloud className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="font-semibold text-lg">Drag & Drop Clinical Documents Here</p>
              <p className="text-xs text-muted-foreground mt-2">Supports PDF, TIFF, PNG up to 25MB per file</p>
              
              {/* Invisible file input trigger */}
              <input
                type="file"
                id="file-upload-input"
                className="hidden"
                multiple={false}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    uploadFile(e.target.files[0]);
                  }
                }}
              />
              <label htmlFor="file-upload-input" className="mt-4">
                <span className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 cursor-pointer">
                  Select Files manually
                </span>
              </label>
            </div>

            {/* Live Ingestion Queue card */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div>
                  <CardTitle className="text-lg font-bold">Ingested Uploads Queue</CardTitle>
                  <CardDescription>Documents undergoing parsing and AI clinical extraction</CardDescription>
                </div>
                <Badge variant="default" className="text-xs">{uploadedFiles.length} files total</Badge>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 border border-border rounded-lg bg-background hover:shadow-sm transition-shadow">
                    <div className="flex items-center space-x-3 min-w-0 flex-1 mr-4">
                      <FileText className="h-8 w-8 text-primary/70 shrink-0" />
                      <div className="min-w-0 flex-1 text-xs">
                        <p className="text-sm font-semibold truncate">{file.name}</p>
                        <p className="text-muted-foreground mt-0.5">
                          {file.size} • OCR: {file.ocr}
                          {file.docId && <span className="ml-2 font-mono text-primary font-bold">({file.docId})</span>}
                        </p>
                        
                        {/* Progress Bar (Visible while progress < 100) */}
                        {file.progress < 100 && (
                          <div className="h-1.5 bg-muted rounded-full overflow-hidden mt-2 max-w-xs">
                            <div className="h-full bg-primary animate-pulse" style={{ width: `${file.progress}%` }} />
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <Badge 
                        variant={
                          file.status === "Success" ? "success" :
                          file.status === "Duplicate" ? "warning" :
                          file.status === "Error" ? "error" : "default"
                        }
                      >
                        {file.status}
                      </Badge>
                      <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-error" onClick={() => handleDelete(file.id)} aria-label="Delete file from queue">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

          </div>

          {/* RIGHT SECTION: METADATA EDITOR & PIPELINE MAPS (Span 1) */}
          <div className="space-y-6">
            
            {/* Metadata verification */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-bold">Metadata Editor & Preview</CardTitle>
                <CardDescription>Verify clinical identifiers mapped by pipeline extraction</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                
                {/* Preview Box */}
                <div className="relative aspect-[3/4] w-full rounded-md border border-border bg-muted/20 flex items-center justify-center overflow-hidden">
                  <FileText className="h-12 w-12 text-muted-foreground/40" />
                  <span className="absolute bottom-2 right-2 text-[10px] text-muted-foreground/60 font-mono">PAGE 1 OF 3</span>
                </div>

                {/* Duplicate block warn */}
                <div className="flex items-start space-x-3 p-3 bg-warning/10 text-warning border border-warning/30 rounded-lg text-xs">
                  <AlertTriangle className="h-5 w-5 shrink-0" />
                  <div>
                    <p className="font-semibold">Duplicate Document Detected</p>
                    <p className="mt-1 text-muted-foreground">A document containing matching OCR hash variables was uploaded 3 hours ago.</p>
                  </div>
                </div>

                {/* Inputs */}
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
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Intake Source Channel</label>
                    <select
                      value={sourceChannel}
                      onChange={(e) => setSourceChannel(e.target.value)}
                      className="flex h-9 w-full rounded-md border border-border bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    >
                      <option value="FAX_UPLOAD">Fax Inbound</option>
                      <option value="EMAIL_ATTACHMENT">Email Attachment</option>
                      <option value="SCAN_UPLOAD">Scanned Document</option>
                      <option value="API_UPLOAD">API Upload</option>
                    </select>
                  </div>
                </div>

                {/* Processing phases */}
                <div className="border-t border-border pt-4 space-y-3">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Ingest Pipeline Progress</span>
                  
                  <div className="grid grid-cols-4 gap-1 text-center text-[10px] font-semibold">
                    <div className="bg-success/15 text-success rounded py-1.5 border border-success/30">Ingest</div>
                    <div className="bg-success/15 text-success rounded py-1.5 border border-success/30">OCR</div>
                    <div className="bg-primary/10 text-primary rounded py-1.5 border border-primary/20 animate-pulse">Extract</div>
                    <div className="bg-muted text-muted-foreground rounded py-1.5 border border-border">Export</div>
                  </div>
                </div>

                {/* Confirmations */}
                <div className="flex justify-end pt-4 space-x-2">
                  <Button variant="outline">Discard Document</Button>
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
