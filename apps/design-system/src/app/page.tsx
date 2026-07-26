"use client";

import React, { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Switch } from "../components/ui/switch";
import { Badge } from "../components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "../components/ui/alert";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../components/ui/table";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "../components/ui/dialog";
import { Sun, Moon, Info, CheckCircle2, AlertTriangle, AlertCircle, Terminal, HelpCircle } from "lucide-react";

export default function DesignSystemPage() {
  const [darkMode, setDarkMode] = useState(false);

  // Synchronize dark class on document element
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      {/* Header section */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-md">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
              DF
            </div>
            <div>
              <h1 className="text-lg font-bold leading-none">DigiFax Design System</h1>
              <span className="text-xs text-muted-foreground">Healthcare SaaS Core UI Specification</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Sun className="h-4 w-4 text-muted-foreground" />
              <Switch
                checked={darkMode}
                onCheckedChange={setDarkMode}
                aria-label="Toggle Dark Mode"
              />
              <Moon className="h-4 w-4 text-muted-foreground" />
            </div>
          </div>
        </div>
      </header>

      {/* Main content grid */}
      <main className="container mx-auto py-8 px-6">
        <Tabs defaultValue="components" className="space-y-8">
          <TabsList className="grid w-full max-w-md grid-cols-4">
            <TabsTrigger value="components">Components</TabsTrigger>
            <TabsTrigger value="colors">Colors</TabsTrigger>
            <TabsTrigger value="typography">Typography</TabsTrigger>
            <TabsTrigger value="spacing">Spacing</TabsTrigger>
          </TabsList>

          {/* COLOR PALETTES TAB */}
          <TabsContent value="colors" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Color Tokens</CardTitle>
                <CardDescription>
                  Enterprise trust color combinations holding a minimum contrast ratio of 4.5:1 (WCAG AA).
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Backgrounds */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Canvas Backgrounds</span>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-background border border-border shadow-sm" />
                    <div>
                      <p className="text-sm font-semibold">`background`</p>
                      <p className="text-xs text-muted-foreground">Default canvas container surface</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-muted border border-border" />
                    <div>
                      <p className="text-sm font-semibold">`muted`</p>
                      <p className="text-xs text-muted-foreground">Tabs, cards header, and sidebars</p>
                    </div>
                  </div>
                </div>

                {/* Brand Colors */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Primary Brand</span>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-primary shadow-sm" />
                    <div>
                      <p className="text-sm font-semibold">`primary`</p>
                      <p className="text-xs text-muted-foreground">Healthcare Trust Blue/Teal Action Colors</p>
                    </div>
                  </div>
                </div>

                {/* Status Colors */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">System Status</span>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-success" />
                    <div>
                      <p className="text-sm font-semibold text-success">`success`</p>
                      <p className="text-xs text-muted-foreground">Approved state / normal values</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-warning" />
                    <div>
                      <p className="text-sm font-semibold text-warning">`warning`</p>
                      <p className="text-xs text-muted-foreground">Pending checks / OCR thresholds</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 rounded-lg border border-border p-3">
                    <div className="h-10 w-10 rounded-md bg-error" />
                    <div>
                      <p className="text-sm font-semibold text-error">`error`</p>
                      <p className="text-xs text-muted-foreground">Critical boundaries / validation fails</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TYPOGRAPHY TAB */}
          <TabsContent value="typography" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Typography System</CardTitle>
                <CardDescription>
                  Highly legible system sans-serif scale designed for complex clinical charts.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="border-b border-border pb-4">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Header Level 1 (h1)</span>
                  <p className="text-2xl font-semibold tracking-tight mt-1">This is a 24px Headline (h1)</p>
                </div>
                <div className="border-b border-border pb-4">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Header Level 2 (h2)</span>
                  <p className="text-xl font-semibold tracking-tight mt-1">This is a 20px Headline (h2)</p>
                </div>
                <div className="border-b border-border pb-4">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Body Copy</span>
                  <p className="text-sm text-foreground mt-1">
                    This is standard body copy (14px). Optimized for reading laboratory results and demographics details at high density.
                  </p>
                </div>
                <div>
                  <span className="text-xs font-semibold uppercase text-muted-foreground">Caption / Labels</span>
                  <p className="text-xs text-muted-foreground mt-1">This is caption text (12px) for table headers and validation logs.</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* SPACING TAB */}
          <TabsContent value="spacing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Spacing Grid (4px)</CardTitle>
                <CardDescription>
                  A strict layout grid establishing visual hierarchy and spatial rhythm.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-6">
                  <span className="w-16 text-sm font-semibold">`8px`</span>
                  <div className="h-4 bg-primary rounded" style={{ width: "8px" }} />
                  <span className="text-xs text-muted-foreground">Labels, internal button paddings</span>
                </div>
                <div className="flex items-center space-x-6">
                  <span className="w-16 text-sm font-semibold">`16px`</span>
                  <div className="h-4 bg-primary rounded" style={{ width: "16px" }} />
                  <span className="text-xs text-muted-foreground">Standard paddings inside inputs, alert banners</span>
                </div>
                <div className="flex items-center space-x-6">
                  <span className="w-16 text-sm font-semibold">`24px`</span>
                  <div className="h-4 bg-primary rounded" style={{ width: "24px" }} />
                  <span className="text-xs text-muted-foreground">Default card paddings, gutters, container columns</span>
                </div>
                <div className="flex items-center space-x-6">
                  <span className="w-16 text-sm font-semibold">`32px`</span>
                  <div className="h-4 bg-primary rounded" style={{ width: "32px" }} />
                  <span className="text-xs text-muted-foreground">Section layouts and main page margins</span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* COMPONENTS SHOWCASE TAB */}
          <TabsContent value="components" className="space-y-8">
            {/* Primitives Section */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Buttons Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Buttons</CardTitle>
                  <CardDescription>Interactive trigger primitives.</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-3">
                  <Button variant="default">Default Sky</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost Trigger</Button>
                  <Button variant="danger">Danger Action</Button>
                  <Button variant="default" disabled>Disabled State</Button>
                </CardContent>
              </Card>

              {/* Inputs & Switch Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Form Elements</CardTitle>
                  <CardDescription>Controls for text input and binary states.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold">Standard Patient Input</label>
                    <Input placeholder="Enter patient full name..." />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-error">Field containing Validation Error</label>
                    <Input error defaultValue="invalid-date-format!!!" />
                    <span className="text-xs text-error font-medium">Please enter a valid ISO format date (YYYY-MM-DD)</span>
                  </div>
                  <div className="flex items-center space-x-4 border-t border-border pt-4">
                    <Switch id="showcase-switch" />
                    <label htmlFor="showcase-switch" className="text-sm font-medium">
                      Simulate Real-time Terminology Normalization
                    </label>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Badges & Alerts Section */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Badges Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Badges</CardTitle>
                  <CardDescription>Visual label status pills.</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  <Badge variant="default">Primary Status</Badge>
                  <Badge variant="secondary">Secondary Muted</Badge>
                  <Badge variant="success">Approved</Badge>
                  <Badge variant="warning">OCR Flag</Badge>
                  <Badge variant="error">Out of Bounds</Badge>
                </CardContent>
              </Card>

              {/* Alerts Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Alerts & Banners</CardTitle>
                  <CardDescription>Critical information boxes.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Alert variant="success">
                    <CheckCircle2 className="h-4 w-4" />
                    <AlertTitle>All Checkpoints Passed</AlertTitle>
                    <AlertDescription>
                      This laboratory report conforms 100% with US Core profiles.
                    </AlertDescription>
                  </Alert>

                  <Alert variant="warning">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>Low OCR Confidence Warning</AlertTitle>
                    <AlertDescription>
                      Certain characters in the patient name field had under 70% matching confidence.
                    </AlertDescription>
                  </Alert>

                  <Alert variant="error">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Critical Validation Fail</AlertTitle>
                    <AlertDescription>
                      Physiological values detected exceed human limit bounds.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </div>

            {/* Complex Components Section (Tables, Tabs, Dialogs) */}
            <Card>
              <CardHeader>
                <CardTitle>Composite Medical Primitives</CardTitle>
                <CardDescription>
                  Advanced layouts displaying clinical tables and confirmation modals.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Tables */}
                <div className="rounded-md border border-border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Analyte Name</TableHead>
                        <TableHead>LOINC Code</TableHead>
                        <TableHead>Value Result</TableHead>
                        <TableHead>Reference Interval</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell className="font-medium">Fasting Glucose</TableCell>
                        <TableCell className="text-muted-foreground">15074-8</TableCell>
                        <TableCell className="text-error font-semibold">145.0 mg/dL</TableCell>
                        <TableCell>70 - 100 mg/dL</TableCell>
                        <TableCell>
                          <Badge variant="error">High Value</Badge>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-medium">Total Cholesterol</TableCell>
                        <TableCell className="text-muted-foreground">2093-3</TableCell>
                        <TableCell>195.0 mg/dL</TableCell>
                        <TableCell>&lt; 200 mg/dL</TableCell>
                        <TableCell>
                          <Badge variant="success">Normal</Badge>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>

                {/* Dialog triggers */}
                <div className="flex justify-end pt-4">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="default">Open Patient Profile Settings</Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Configure Patient Profile</DialogTitle>
                        <DialogDescription>
                          Review extracted demographics details before approving integration exports.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                          <label className="text-xs font-semibold">Patient Full Name</label>
                          <Input defaultValue="Elizabeth Blackwell" />
                        </div>
                        <div className="grid gap-2">
                          <label className="text-xs font-semibold">Date of Birth</label>
                          <Input type="date" defaultValue="1988-05-12" />
                        </div>
                      </div>
                      <DialogFooter>
                        <DialogClose asChild>
                          <Button variant="outline">Discard Changes</Button>
                        </DialogClose>
                        <DialogClose asChild>
                          <Button variant="default">Save Demographics</Button>
                        </DialogClose>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
