/**
 * @file page.tsx
 * @description Tenant Configuration Settings Console.
 * 
 * Clinical settings dashboard managing locale formats, currency standards, number templates,
 * regular expressions for patient identifiers / MRNs / document numbers, and retention policies.
 * Incorporates dynamic formatted previews, live regex validation, and state versioning.
 */

"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Switch } from "../../components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/tabs";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  Settings, RefreshCw, CheckCircle2, AlertTriangle, Calendar, 
  Clock, Globe, DollarSign, Binary, ShieldAlert, FileText, CheckCircle
} from "lucide-react";

export default function SettingsPage() {
  // --- STATE STORES ---
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Locale Settings
  const [dateFormat, setDateFormat] = useState("YYYY-MM-DD");
  const [timeFormat, setTimeFormat] = useState("HH:mm:ss");
  const [timezone, setTimezone] = useState("America/New_York");
  const [language, setLanguage] = useState("en");
  const [currency, setCurrency] = useState("USD");
  const [locale, setLocale] = useState("en-US");
  const [numberFormat, setNumberFormat] = useState("1,234.56");

  // Clinical Identifiers Regex Templates
  const [patientIdFormat, setPatientIdFormat] = useState("PAT-\\d{6}");
  const [medicalRecordFormat, setMedicalRecordFormat] = useState("MRN-\\d{8}");
  const [documentNumberFormat, setDocumentNumberFormat] = useState("DOC-\\d{10}");

  // Retention Period (Days)
  const [defaultRetentionDays, setDefaultRetentionDays] = useState(365);

  // Live Previews Outputs
  const [formattedDatePreview, setFormattedDatePreview] = useState("");
  const [formattedNumberPreview, setFormattedNumberPreview] = useState("");

  // Validation States
  const [isPatientRegexValid, setIsPatientRegexValid] = useState(true);
  const [isMrnRegexValid, setIsMrnRegexValid] = useState(true);
  const [isDocRegexValid, setIsDocRegexValid] = useState(true);

  // Configuration version tracker
  const [configVersion, setConfigVersion] = useState(1);

  // --- CONTROLLER HANDLERS & PREVIEWS ---

  // Check regex validity on user keypress
  useEffect(() => {
    try {
      new RegExp(patientIdFormat);
      setIsPatientRegexValid(true);
    } catch {
      setIsPatientRegexValid(false);
    }
  }, [patientIdFormat]);

  useEffect(() => {
    try {
      new RegExp(medicalRecordFormat);
      setIsMrnRegexValid(true);
    } catch {
      setIsMrnRegexValid(false);
    }
  }, [medicalRecordFormat]);

  useEffect(() => {
    try {
      new RegExp(documentNumberFormat);
      setIsDocRegexValid(true);
    } catch {
      setIsDocRegexValid(false);
    }
  }, [documentNumberFormat]);

  // Update live date & number format preview displays
  useEffect(() => {
    const date = new Date();
    let dStr = "";
    if (dateFormat === "YYYY-MM-DD") {
      dStr = "2026-07-30";
    } else if (dateFormat === "DD/MM/YYYY") {
      dStr = "30/07/2026";
    } else {
      dStr = "07/30/2026";
    }

    let tStr = "";
    if (timeFormat === "HH:mm:ss") {
      tStr = "14:35:10";
    } else {
      tStr = "02:35 PM";
    }

    setFormattedDatePreview(`${dStr} ${tStr}`);

    let numStr = "1234.56";
    if (numberFormat === "1,234.56") {
      numStr = "1,234.56";
    } else if (numberFormat === "1.234,56") {
      numStr = "1.234,56";
    } else {
      numStr = "1 234,56";
    }
    setFormattedNumberPreview(`${currency} ${numStr}`);
  }, [dateFormat, timeFormat, numberFormat, currency]);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isPatientRegexValid || !isMrnRegexValid || !isDocRegexValid) {
      setErrorMessage("Please fix regex validation errors prior to saving.");
      setTimeout(() => setErrorMessage(""), 4000);
      return;
    }
    if (defaultRetentionDays < 1) {
      setErrorMessage("Retention days must be positive.");
      setTimeout(() => setErrorMessage(""), 4000);
      return;
    }

    setSaveSuccess(true);
    setConfigVersion(prev => prev + 1);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* HEADER CONTROLS BAR */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">System Settings</h2>
            <p className="text-sm text-muted-foreground">Manage organization layouts, formatting standards, clinical identifier regex configurations, and document lifecycles.</p>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="secondary" className="text-xs px-2.5 py-1">
              Config Version: v{configVersion}
            </Badge>
            <Button id="save-settings-top-btn" variant="default" onClick={handleSaveSettings} className="flex items-center space-x-1.5">
              <RefreshCw className="h-4 w-4" />
              <span>Save System Settings</span>
            </Button>
          </div>
        </div>

        {/* Global Save Success feedback */}
        {saveSuccess && (
          <Alert variant="success" className="py-2.5">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">Settings Saved</AlertTitle>
            <AlertDescription className="text-[11px]">Tenant system configuration parameters updated to Version {configVersion} successfully.</AlertDescription>
          </Alert>
        )}

        {/* Global Error Banner */}
        {errorMessage && (
          <Alert variant="error" className="py-2.5">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle className="text-xs">Validation Failure</AlertTitle>
            <AlertDescription className="text-[11px]">{errorMessage}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT/MID: CONFIGURATION CONTROLS */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardContent className="pt-6">
                
                <Tabs defaultValue="locale" className="space-y-6">
                  <TabsList className="grid w-full grid-cols-3 bg-muted/60 p-1 rounded-md">
                    <TabsTrigger value="locale" className="text-xs flex items-center space-x-1">
                      <Globe className="h-3.5 w-3.5" />
                      <span>Locale & Time</span>
                    </TabsTrigger>
                    <TabsTrigger value="clinical" className="text-xs flex items-center space-x-1">
                      <Binary className="h-3.5 w-3.5" />
                      <span>Clinical Formats</span>
                    </TabsTrigger>
                    <TabsTrigger value="lifecycle" className="text-xs flex items-center space-x-1">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      <span>Data Lifecycle</span>
                    </TabsTrigger>
                  </TabsList>

                  {/* TAB 1: LOCALE & FORMATTING PARAMETERS */}
                  <TabsContent value="locale" className="space-y-6 pt-2">
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="space-y-1.5">
                        <label htmlFor="date-format-select" className="text-xs font-semibold uppercase text-muted-foreground">Date Layout Format</label>
                        <select 
                          id="date-format-select"
                          value={dateFormat} 
                          onChange={(e) => setDateFormat(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="YYYY-MM-DD">YYYY-MM-DD (e.g. 2026-07-30)</option>
                          <option value="DD/MM/YYYY">DD/MM/YYYY (e.g. 30/07/2026)</option>
                          <option value="MM/DD/YYYY">MM/DD/YYYY (e.g. 07/30/2026)</option>
                        </select>
                      </div>
                      <div className="space-y-1.5">
                        <label htmlFor="time-format-select" className="text-xs font-semibold uppercase text-muted-foreground">Time Layout Format</label>
                        <select 
                          id="time-format-select"
                          value={timeFormat} 
                          onChange={(e) => setTimeFormat(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="HH:mm:ss">24-Hour (HH:mm:ss)</option>
                          <option value="hh:mm A">12-Hour (hh:mm A)</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="space-y-1.5">
                        <label htmlFor="timezone-select" className="text-xs font-semibold uppercase text-muted-foreground">System Timezone</label>
                        <select 
                          id="timezone-select"
                          value={timezone} 
                          onChange={(e) => setTimezone(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="America/New_York">Eastern Time (America/New_York)</option>
                          <option value="America/Chicago">Central Time (America/Chicago)</option>
                          <option value="America/Los_Angeles">Pacific Time (America/Los_Angeles)</option>
                          <option value="UTC">Coordinated Universal Time (UTC)</option>
                        </select>
                      </div>
                      <div className="space-y-1.5">
                        <label htmlFor="language-select" className="text-xs font-semibold uppercase text-muted-foreground">Default Language</label>
                        <select 
                          id="language-select"
                          value={language} 
                          onChange={(e) => setLanguage(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="en">English (en)</option>
                          <option value="es">Español (es)</option>
                          <option value="fr">Français (fr)</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-3">
                      <div className="space-y-1.5">
                        <label htmlFor="currency-select" className="text-xs font-semibold uppercase text-muted-foreground">Currency</label>
                        <select 
                          id="currency-select"
                          value={currency} 
                          onChange={(e) => setCurrency(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="USD">USD ($)</option>
                          <option value="EUR">EUR (€)</option>
                          <option value="GBP">GBP (£)</option>
                        </select>
                      </div>
                      <div className="space-y-1.5">
                        <label htmlFor="locale-input" className="text-xs font-semibold uppercase text-muted-foreground">System Locale Tag</label>
                        <Input id="locale-input" value={locale} onChange={(e) => setLocale(e.target.value)} placeholder="e.g. en-US" />
                      </div>
                      <div className="space-y-1.5">
                        <label htmlFor="number-format-select" className="text-xs font-semibold uppercase text-muted-foreground">Number Format</label>
                        <select 
                          id="number-format-select"
                          value={numberFormat} 
                          onChange={(e) => setNumberFormat(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option value="1,234.56">1,234.56 (Dot Decimal)</option>
                          <option value="1.234,56">1.234,56 (Comma Decimal)</option>
                          <option value="1 234,56">1 234,56 (Space Separator)</option>
                        </select>
                      </div>
                    </div>
                  </TabsContent>

                  {/* TAB 2: CLINICAL IDENTIFIER REGEX FIELDS */}
                  <TabsContent value="clinical" className="space-y-6 pt-2">
                    
                    <div className="space-y-4">
                      
                      {/* Patient ID Regex format */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between items-center">
                          <label htmlFor="patient-regex-input" className="text-xs font-semibold uppercase text-muted-foreground">Patient Identifier Regex Layout</label>
                          <Badge variant={isPatientRegexValid ? "success" : "error"} className="text-[10px] py-0 px-2 font-mono">
                            {isPatientRegexValid ? "Valid Regex" : "Invalid Regex"}
                          </Badge>
                        </div>
                        <Input 
                          id="patient-regex-input"
                          value={patientIdFormat} 
                          onChange={(e) => setPatientIdFormat(e.target.value)} 
                          className="font-mono text-xs" 
                        />
                        <p className="text-[10px] text-muted-foreground">Regex matching incoming Patient Identifiers (e.g. `PAT-\d{6}`).</p>
                      </div>

                      {/* MRN Regex format */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between items-center">
                          <label htmlFor="mrn-regex-input" className="text-xs font-semibold uppercase text-muted-foreground">Medical Record Number (MRN) Regex Layout</label>
                          <Badge variant={isMrnRegexValid ? "success" : "error"} className="text-[10px] py-0 px-2 font-mono">
                            {isMrnRegexValid ? "Valid Regex" : "Invalid Regex"}
                          </Badge>
                        </div>
                        <Input 
                          id="mrn-regex-input"
                          value={medicalRecordFormat} 
                          onChange={(e) => setMedicalRecordFormat(e.target.value)} 
                          className="font-mono text-xs" 
                        />
                        <p className="text-[10px] text-muted-foreground">Regex matching Patient MRNs (e.g. `MRN-\d{8}`).</p>
                      </div>

                      {/* Document numbering regex format */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between items-center">
                          <label htmlFor="doc-regex-input" className="text-xs font-semibold uppercase text-muted-foreground">Document ID Numbering Regex Layout</label>
                          <Badge variant={isDocRegexValid ? "success" : "error"} className="text-[10px] py-0 px-2 font-mono">
                            {isDocRegexValid ? "Valid Regex" : "Invalid Regex"}
                          </Badge>
                        </div>
                        <Input 
                          id="doc-regex-input"
                          value={documentNumberFormat} 
                          onChange={(e) => setDocumentNumberFormat(e.target.value)} 
                          className="font-mono text-xs" 
                        />
                        <p className="text-[10px] text-muted-foreground">Regex layout validating incoming secure faxes (e.g. `DOC-\d{10}`).</p>
                      </div>

                    </div>
                  </TabsContent>

                  {/* TAB 3: STORAGE RETENTION LIFECYCLE */}
                  <TabsContent value="lifecycle" className="space-y-6 pt-2">
                    <div className="space-y-4">
                      <div className="space-y-1.5">
                        <label htmlFor="retention-input" className="text-xs font-semibold uppercase text-muted-foreground">Default Archive Retention Duration (Days)</label>
                        <Input 
                          id="retention-input"
                          type="number" 
                          value={defaultRetentionDays} 
                          onChange={(e) => setDefaultRetentionDays(parseInt(e.target.value) || 0)} 
                        />
                        <p className="text-[10px] text-muted-foreground">Document storage duration inside S3 before triggering automated deletion workflows.</p>
                      </div>

                      <div className="p-4 border border-warning/30 bg-warning/5 rounded-lg flex items-start space-x-3 text-xs">
                        <AlertTriangle className="h-5 w-5 text-warning shrink-0 mt-0.5" />
                        <div className="space-y-1">
                          <p className="font-bold text-warning">HIPAA Compliance Retention Policy Gate</p>
                          <p className="text-muted-foreground text-[10px]">Medical institutions are legally required to retain clinical analysis summaries for at least 180 days. Reducing this configuration below 180 days triggers automated warnings inside user audits.</p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>

              </CardContent>
            </Card>
          </div>

          {/* RIGHT: CONFIGURATION PREVIEWS SUMMARY */}
          <div className="space-y-6">
            
            {/* Live Outputs summary */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold">Dynamic Configuration Previews</CardTitle>
                <CardDescription>Verify formatting and parsing details in real-time.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-1">
                
                {/* Locale rendering previews */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground border-b pb-1.5">Locale & Formatted Outputs</h4>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="flex items-center space-x-1.5 text-muted-foreground">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>Date/Time:</span>
                    </div>
                    <div id="date-preview-text" className="col-span-2 font-mono font-bold text-right text-foreground">
                      {formattedDatePreview}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="flex items-center space-x-1.5 text-muted-foreground">
                      <DollarSign className="h-3.5 w-3.5" />
                      <span>Currency:</span>
                    </div>
                    <div id="number-preview-text" className="col-span-2 font-mono font-bold text-right text-foreground">
                      {formattedNumberPreview}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="flex items-center space-x-1.5 text-muted-foreground">
                      <FileText className="h-3.5 w-3.5" />
                      <span>Retention:</span>
                    </div>
                    <div id="retention-preview-text" className="col-span-2 font-mono font-bold text-right text-foreground">
                      {defaultRetentionDays} days
                    </div>
                  </div>
                </div>

                {/* Previews parsing status checks */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground border-b pb-1.5">Regex Parser Templates</h4>
                  
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Patient ID Layout:</span>
                    {isPatientRegexValid ? (
                      <Badge variant="success" className="text-[10px] font-mono">/ {patientIdFormat} /</Badge>
                    ) : (
                      <Badge variant="error" className="text-[10px] font-mono">Invalid</Badge>
                    )}
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">MRN Layout:</span>
                    {isMrnRegexValid ? (
                      <Badge variant="success" className="text-[10px] font-mono">/ {medicalRecordFormat} /</Badge>
                    ) : (
                      <Badge variant="error" className="text-[10px] font-mono">Invalid</Badge>
                    )}
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Document ID Layout:</span>
                    {isDocRegexValid ? (
                      <Badge variant="success" className="text-[10px] font-mono">/ {documentNumberFormat} /</Badge>
                    ) : (
                      <Badge variant="error" className="text-[10px] font-mono">Invalid</Badge>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t flex justify-end">
                  <Button id="save-settings-bottom-btn" onClick={handleSaveSettings} disabled={!isPatientRegexValid || !isMrnRegexValid || !isDocRegexValid} className="w-full">
                    Save Configurations
                  </Button>
                </div>

              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
