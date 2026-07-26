/**
 * @file page.tsx
 * @description DigiFax Administration Console. Handles configurations of organization users, roles, 
 * LLM model/OCR selection profiles, FHIR target URL connections, and diagnostic health heartbeats.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { Switch } from "../../components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/ui/table";
import { 
  Users, Key, Settings2, ShieldCheck, Heart, Database, 
  Cpu, HardDrive, RefreshCw, Terminal, Eye, EyeOff, Activity 
} from "lucide-react";

export default function AdminPage() {
  // state hooks managing password field visibility state
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [activeTab, setActiveTab] = useState("access");

  // Mock list of user profiles within this directory
  const usersList = [
    { name: "Kalyan Kalwa", email: "kalyan@openhealthagents.org", role: "Super Admin", status: "Active" },
    { name: "Arthur Conan Doyle", email: "arthur@openhealthagents.org", role: "Clinical Reviewer", status: "Active" },
    { name: "Naveen Raj", email: "naveen@openhealthagents.org", role: "Developer", status: "Active" }
  ];

  // API credentials keys mapping table
  const apiKeys = [
    { name: "Primary Medplum Connector", prefix: "df_live_8a92...", created: "2026-07-01", status: "Active" },
    { name: "OCR Ingestion webhook", prefix: "df_live_901c...", created: "2026-07-15", status: "Active" }
  ];

  // Pipeline execution switches
  const featureFlags = [
    { flag: "realtime-ocr-indexing", description: "Trigger baseline OCR parsing immediately on NATS ingest queue", status: true },
    { flag: "automatic-fhir-export", description: "Directly dispatch validated resources to EHR servers without review step", status: false }
  ];

  // Services heartbeats status array
  const systemHealth = [
    { name: "PostgreSQL Database", status: "Healthy", detail: "Active connection count: 24" },
    { name: "NATS Broker", status: "Healthy", detail: "Queued dispatches: 0 pending" },
    { name: "Medplum Sandbox", status: "Healthy", detail: "US-Core R4 profile responses: 100%" }
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* TITLE WIDGET CONTAINER */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Admin Console</h2>
            <p className="text-sm text-muted-foreground">Configure medical directories, pipeline providers, keys, and view cluster diagnostics.</p>
          </div>
          <Button variant="outline" className="flex items-center space-x-1">
            <RefreshCw className="h-4 w-4" />
            <span>Sync System Settings</span>
          </Button>
        </div>

        {/* Dynamic Tab Layout containing core admin configs */}
        <Tabs defaultValue="access" className="space-y-6">
          <TabsList className="grid w-full max-w-lg grid-cols-4">
            <TabsTrigger value="access">Access</TabsTrigger>
            <TabsTrigger value="providers">Providers</TabsTrigger>
            <TabsTrigger value="keys">Keys & Flags</TabsTrigger>
            <TabsTrigger value="health">System Diagnostics</TabsTrigger>
          </TabsList>

          {/* TAB 1: ACCESS DIRECTORY CONFIG */}
          <TabsContent value="access" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Users & Access Credentials</CardTitle>
                <CardDescription>Configure user accounts and clinical roles directories.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User Profile</TableHead>
                      <TableHead>Email Address</TableHead>
                      <TableHead>Assigned Role</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersList.map((usr, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-semibold text-sm">{usr.name}</TableCell>
                        <TableCell className="font-mono text-xs">{usr.email}</TableCell>
                        <TableCell>
                          <Badge variant="default">{usr.role}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="success">{usr.status}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: AI & EHR PROVIDERS */}
          <TabsContent value="providers" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Primary extraction models */}
              <Card>
                <CardHeader>
                  <CardTitle>AI Providers & LLMs</CardTitle>
                  <CardDescription>LLM/OCR extraction settings</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Primary OCR Engine</label>
                    <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                      <option>Google Document AI OCR</option>
                      <option>AWS Textract</option>
                      <option>Baseline Tesseract</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Extraction LLM model</label>
                    <select className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none">
                      <option>Gemini 1.5 Pro</option>
                      <option>Claude 3.5 Sonnet</option>
                      <option>GPT-4o</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">Provider Credentials Key</label>
                    <div className="relative">
                      <Input type={apiKeyVisible ? "text" : "password"} defaultValue="api_secret_key_google_gemini_pro" />
                      <button 
                        onClick={() => setApiKeyVisible(!apiKeyVisible)}
                        className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground"
                      >
                        {apiKeyVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* FHIR server URL endpoints */}
              <Card>
                <CardHeader>
                  <CardTitle>FHIR Targets</CardTitle>
                  <CardDescription>Clinical endpoints connection setups</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">FHIR Server Base URL</label>
                    <Input defaultValue="https://api.medplum.com/fhir/R4" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase text-muted-foreground">EHR OAuth Issuer</label>
                    <Input defaultValue="https://auth.medplum.com/oauth/token" />
                  </div>
                  <div className="flex justify-end pt-2">
                    <Button variant="outline" size="sm">Test Endpoint Connection</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* TAB 3: API KEYS & DYNAMIC SYSTEM FLAGS */}
          <TabsContent value="keys" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              
              {/* Credentials list */}
              <Card>
                <CardHeader>
                  <CardTitle>API Access Tokens</CardTitle>
                  <CardDescription>Manage credentials for automated ingress scripts</CardDescription>
                </CardHeader>
                <CardContent className="pt-2">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Key Name</TableHead>
                        <TableHead>Prefix</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {apiKeys.map((key, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-semibold text-xs">{key.name}</TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">{key.prefix}</TableCell>
                          <TableCell>
                            <Badge variant="success">{key.status}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <div className="flex justify-end pt-4">
                    <Button variant="default" size="sm">Generate New API Key</Button>
                  </div>
                </CardContent>
              </Card>

              {/* Feature flags toggles */}
              <Card>
                <CardHeader>
                  <CardTitle>Feature Flags</CardTitle>
                  <CardDescription>Toggle beta extraction features in real-time</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-2 text-xs">
                  {featureFlags.map((flag, idx) => (
                    <div key={idx} className="flex items-start justify-between p-3 border border-border rounded bg-muted/20">
                      <div className="space-y-1 mr-4">
                        <p className="font-bold font-mono text-primary">{flag.flag}</p>
                        <p className="text-[11px] text-muted-foreground leading-relaxed">{flag.description}</p>
                      </div>
                      <Switch defaultChecked={flag.status} />
                    </div>
                  ))}
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 4: SYSTEM HEALTHE & DIAGNOSTICS */}
          <TabsContent value="health" className="space-y-6">
            
            {/* Cluster metric cards */}
            <div className="grid gap-6 sm:grid-cols-3">
              
              {/* CPU utilization */}
              <Card>
                <CardContent className="p-6 text-xs space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold uppercase text-[10px] text-muted-foreground">Cluster CPU</span>
                    <Cpu className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-xl font-bold">14.6%</span>
                    <span className="text-success font-semibold text-[10px]">Normal</span>
                  </div>
                  <p className="text-muted-foreground text-[10px]">Active threads: 12 nodes</p>
                </CardContent>
              </Card>

              {/* RAM allocations */}
              <Card>
                <CardContent className="p-6 text-xs space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold uppercase text-[10px] text-muted-foreground">Cluster RAM</span>
                    <Activity className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-xl font-bold">4.2 GB</span>
                    <span className="text-muted-foreground">/ 16 GB</span>
                  </div>
                  <p className="text-muted-foreground text-[10px]">Buffers: 1.2 GB cached</p>
                </CardContent>
              </Card>

              {/* Storage threshold */}
              <Card>
                <CardContent className="p-6 text-xs space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold uppercase text-[10px] text-muted-foreground">Storage Volume</span>
                    <HardDrive className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-xl font-bold">84%</span>
                    <span className="text-warning font-semibold text-[10px]">Warning threshold</span>
                  </div>
                  <p className="text-muted-foreground text-[10px]">Free space: 16 GB remaining</p>
                </CardContent>
              </Card>

            </div>

            {/* Microservice checklists */}
            <Card>
              <CardHeader>
                <CardTitle>Core System Health Diagnostics</CardTitle>
                <CardDescription>Heartbeat alerts from clinical network nodes</CardDescription>
              </CardHeader>
              <CardContent className="pt-2 text-xs">
                {systemHealth.map((health, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border-b border-border last:border-b-0">
                    <div className="space-y-0.5">
                      <p className="font-bold">{health.name}</p>
                      <p className="text-[10px] text-muted-foreground">{health.detail}</p>
                    </div>
                    <Badge variant="success">{health.status}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

          </TabsContent>
        </Tabs>

      </div>
    </AppShell>
  );
}
