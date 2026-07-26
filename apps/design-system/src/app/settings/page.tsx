"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Switch } from "../../components/ui/switch";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/tabs";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  Settings, Shield, Bell, HardDrive, Cpu, 
  Database, RefreshCw, CheckCircle2, Server, Eye, EyeOff 
} from "lucide-react";

export default function SettingsPage() {
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [llmKeyVisible, setLlmKeyVisible] = useState(false);

  // Form states
  const [orgName, setOrgName] = useState("OpenHealth Hospital");
  const [orgEmail, setOrgEmail] = useState("admin@openhealthagents.org");
  const [mfaEnabled, setMfaEnabled] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);

  const handleSaveSettings = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">System Settings</h2>
            <p className="text-sm text-muted-foreground">Manage organization layouts, security authentication, model keys, and EHR targets.</p>
          </div>
          <Button variant="default" onClick={handleSaveSettings} className="flex items-center space-x-1">
            <RefreshCw className="h-4 w-4" />
            <span>Save Settings Changes</span>
          </Button>
        </div>

        {saveSuccess && (
          <Alert variant="success" className="py-2.5">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">Settings Saved</AlertTitle>
            <AlertDescription className="text-[11px]">System configurations updated successfully.</AlertDescription>
          </Alert>
        )}

        {/* Setting categories Tabs */}
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full max-w-lg grid-cols-4">
            <TabsTrigger value="general">Branding</TabsTrigger>
            <TabsTrigger value="auth">Auth & Alerts</TabsTrigger>
            <TabsTrigger value="models">AI & Storage</TabsTrigger>
            <TabsTrigger value="fhir">FHIR & Export</TabsTrigger>
          </TabsList>

          {/* TAB 1: GENERAL & BRANDING */}
          <TabsContent value="general" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Organization details */}
              <Card>
                <CardHeader>
                  <CardTitle>Organization Profiles</CardTitle>
                  <CardDescription>Configure clinic demographics identifiers</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Facility Name</label>
                    <Input value={orgName} onChange={(e) => setOrgName(e.target.value)} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Billing email address</label>
                    <Input value={orgEmail} onChange={(e) => setOrgEmail(e.target.value)} />
                  </div>
                </CardContent>
              </Card>

              {/* Branding and styling */}
              <Card>
                <CardHeader>
                  <CardTitle>Portal Branding Customization</CardTitle>
                  <CardDescription>Configure custom workspace themes</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Primary Canvas Color</label>
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded bg-primary border border-border" />
                      <select className="rounded-md border border-border bg-background p-1.5 text-xs outline-none flex-1">
                        <option>Trust Blue (Default)</option>
                        <option>Clinical Green</option>
                        <option>Muted Teal</option>
                      </select>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Clinic Logo File Path</label>
                    <Input defaultValue="/assets/logos/openhealth_main.png" />
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 2: AUTH & NOTIFICATIONS */}
          <TabsContent value="auth" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Authentication */}
              <Card>
                <CardHeader>
                  <CardTitle>Authentication & Identity</CardTitle>
                  <CardDescription>Configure user sign-in configurations</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="flex items-center justify-between p-3 border border-border rounded bg-muted/20 text-xs">
                    <div className="space-y-1 mr-4">
                      <p className="font-bold">Require Multi-Factor Authentication (MFA)</p>
                      <p className="text-muted-foreground">Enforces login authentication codes from Reviewer user profiles</p>
                    </div>
                    <Switch checked={mfaEnabled} onCheckedChange={setMfaEnabled} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Session Timeout Slider (Minutes)</label>
                    <Input type="number" defaultValue="60" />
                  </div>
                </CardContent>
              </Card>

              {/* Notifications */}
              <Card>
                <CardHeader>
                  <CardTitle>Notification Alert Channels</CardTitle>
                  <CardDescription>Configure system event notify webhooks</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="flex items-center justify-between p-3 border border-border rounded bg-muted/20 text-xs">
                    <div className="space-y-1 mr-4">
                      <p className="font-bold">Email Notifications</p>
                      <p className="text-muted-foreground">Send audit summaries directly to reviewer logs</p>
                    </div>
                    <Switch checked={emailAlerts} onCheckedChange={setEmailAlerts} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Slack Integration Webhook URL</label>
                    <Input defaultValue="https://hooks.slack.com/services/T00/B00/X00" />
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 3: AI & STORAGE CONFIG */}
          <TabsContent value="models" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* AI Config */}
              <Card>
                <CardHeader>
                  <CardTitle>LLM & OCR Model Configuration</CardTitle>
                  <CardDescription>Configure backend parsing settings</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">OCR Engine Provider</label>
                    <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                      <option>Google Document AI OCR</option>
                      <option>AWS Textract</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Baseline LLM Model</label>
                    <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                      <option>Gemini 1.5 Pro</option>
                      <option>Claude 3.5 Sonnet</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">LLM Key Credentials</label>
                    <div className="relative">
                      <Input type={llmKeyVisible ? "text" : "password"} defaultValue="api_secret_key_google_gemini_pro" />
                      <button 
                        onClick={() => setLlmKeyVisible(!llmKeyVisible)}
                        className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground"
                      >
                        {llmKeyVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Storage config */}
              <Card>
                <CardHeader>
                  <CardTitle>Storage & Archives Configuration</CardTitle>
                  <CardDescription>Configure S3 buckets and local backups</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Active Storage Bucket URL</label>
                    <Input defaultValue="s3://digifax-clinical-archives-prod" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Local Backup Path</label>
                    <Input defaultValue="D:/Kalyan/DigiFax/backups/archives" />
                  </div>
                  <div className="flex items-center justify-between p-3 border border-border rounded bg-muted/20 text-xs">
                    <div className="space-y-0.5">
                      <p className="font-bold">Compress Archive Files</p>
                      <p className="text-muted-foreground">Gzip files prior to backup dispatch</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 4: FHIR & EXPORT CONFIG */}
          <TabsContent value="fhir" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* FHIR Setup */}
              <Card>
                <CardHeader>
                  <CardTitle>EHR Target Setup</CardTitle>
                  <CardDescription>Setup EHR integrations and profiles</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Medplum FHIR Server endpoint URL</label>
                    <Input defaultValue="https://api.medplum.com/fhir/R4" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">US Core profiles Version</label>
                    <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                      <option>US Core v3.1.1 (Conforming)</option>
                      <option>US Core v4.0.0</option>
                    </select>
                  </div>
                </CardContent>
              </Card>

              {/* Export Setup */}
              <Card>
                <CardHeader>
                  <CardTitle>Export Mappings Configuration</CardTitle>
                  <CardDescription>Automatic exports triggers settings</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="flex items-center justify-between p-3 border border-border rounded bg-muted/20 text-xs">
                    <div className="space-y-1 mr-4">
                      <p className="font-bold">Auto-dispatch Clean Documents</p>
                      <p className="text-muted-foreground">Automatically export faxes if validations pass and confidence is &gt; 95%</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Outbound Queue limits</label>
                    <Input type="number" defaultValue="25" />
                  </div>
                </CardContent>
              </Card>

            </div>
          </TabsContent>
        </Tabs>

      </div>
    </AppShell>
  );
}
