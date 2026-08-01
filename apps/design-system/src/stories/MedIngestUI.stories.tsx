import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Switch } from "../components/ui/switch";
import { Badge } from "../components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "../components/ui/alert";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Terminal, CheckCircle2, AlertTriangle, AlertCircle } from "lucide-react";
import "../app/globals.css";

const meta: Meta = {
  title: "MedIngest/Primitives",
  parameters: {
    layout: "centered",
  },
};

export default meta;

export const Buttons: StoryObj = {
  render: () => (
    <div className="flex flex-wrap gap-4 p-6 bg-background rounded-lg border border-border">
      <Button variant="default">Default Sky</Button>
      <Button variant="outline">Outline Button</Button>
      <Button variant="ghost">Ghost Trigger</Button>
      <Button variant="danger">Danger Action</Button>
      <Button variant="default" disabled>Disabled State</Button>
    </div>
  ),
};

export const FormsAndInputs: StoryObj = {
  render: () => (
    <div className="space-y-6 w-96 p-6 bg-background rounded-lg border border-border">
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase text-muted-foreground">Standard Text Input</label>
        <Input placeholder="Enter patient name..." />
      </div>
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase text-error">Input with Field Error</label>
        <Input error defaultValue="invalid-date-format!!!" />
        <span className="text-xs text-error font-medium">Please enter a valid ISO format date (YYYY-MM-DD)</span>
      </div>
      <div className="flex items-center space-x-3 border-t border-border pt-4">
        <Switch id="toggle-opt" />
        <label htmlFor="toggle-opt" className="text-sm font-medium">
          Enable realtime OCR parsing
        </label>
      </div>
    </div>
  ),
};

export const Badges: StoryObj = {
  render: () => (
    <div className="flex flex-wrap gap-2 p-6 bg-background rounded-lg border border-border">
      <Badge variant="default">Primary Sky</Badge>
      <Badge variant="secondary">Muted Slate</Badge>
      <Badge variant="success">Approved</Badge>
      <Badge variant="warning">OCR Warning</Badge>
      <Badge variant="error">Critical Value</Badge>
    </div>
  ),
};

export const BannersAndAlerts: StoryObj = {
  render: () => (
    <div className="space-y-4 w-128 p-6 bg-background rounded-lg border border-border">
      <Alert variant="default">
        <Terminal className="h-4 w-4" />
        <AlertTitle>System Alert</AlertTitle>
        <AlertDescription>The OCR indexing task is queuing in background.</AlertDescription>
      </Alert>

      <Alert variant="success">
        <CheckCircle2 className="h-4 w-4" />
        <AlertTitle>Conforms to US Core Profiles</AlertTitle>
        <AlertDescription>HAPI validation checks successfully approved the diagnostic report bundle.</AlertDescription>
      </Alert>

      <Alert variant="warning">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Low Extraction Accuracy Warning</AlertTitle>
        <AlertDescription>AI terminology normalization returned code maps below 80% confidence thresholds.</AlertDescription>
      </Alert>

      <Alert variant="error">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Epic Integration Dispatch Failed</AlertTitle>
        <AlertDescription>Signed client JWT assertion expired. Re-triggering oauth session key.</AlertDescription>
      </Alert>
    </div>
  ),
};
