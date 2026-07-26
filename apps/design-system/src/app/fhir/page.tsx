"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { 
  FileCode, Copy, Download, Code, CheckCircle, AlertTriangle, 
  Terminal, ShieldCheck, Layers, GitFork, ArrowRight, Save 
} from "lucide-react";

export default function FhirExplorerPage() {
  const [selectedResource, setSelectedResource] = useState("Patient/df-pat-blackwell");
  const [copySuccess, setCopySuccess] = useState(false);

  const resourceTree = [
    {
      group: "Bundle Metadata",
      items: [{ id: "Bundle/df-bundle-9011", type: "Bundle", label: "Ingest Bundle 9011" }]
    },
    {
      group: "Clinical Resources",
      items: [
        { id: "Patient/df-pat-blackwell", type: "Patient", label: "Elizabeth Blackwell (Demographics)" },
        { id: "Observation/df-obs-glucose", type: "Observation", label: "Glucose Value: 145.0 mg/dL" },
        { id: "Organization/df-org-openhealth", type: "Organization", label: "OpenHealth Facility" }
      ]
    }
  ];

  const mockJson: Record<string, any> = {
    "Patient/df-pat-blackwell": {
      "resourceType": "Patient",
      "id": "df-pat-blackwell",
      "meta": {
        "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
      },
      "active": true,
      "name": [
        {
          "use": "official",
          "family": "Blackwell",
          "given": ["Elizabeth"]
        }
      ],
      "gender": "female",
      "birthDate": "1988-05-12"
    },
    "Observation/df-obs-glucose": {
      "resourceType": "Observation",
      "id": "df-obs-glucose",
      "meta": {
        "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"]
      },
      "status": "final",
      "category": [
        {
          "coding": [
            { "system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory" }
          ]
        }
      ],
      "code": {
        "coding": [
          { "system": "http://loinc.org", "code": "15074-8", "display": "Glucose [Mass/volume] in Blood" }
        ]
      },
      "subject": { "reference": "Patient/df-pat-blackwell" },
      "valueQuantity": {
        "value": 145.0,
        "unit": "mg/dL",
        "system": "http://unitsofmeasure.org",
        "code": "mg/dL"
      }
    },
    "Organization/df-org-openhealth": {
      "resourceType": "Organization",
      "id": "df-org-openhealth",
      "meta": {
        "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"]
      },
      "active": true,
      "name": "OpenHealth Hospital",
      "telecom": [{ "system": "phone", "value": "555-019-2831" }]
    },
    "Bundle/df-bundle-9011": {
      "resourceType": "Bundle",
      "id": "df-bundle-9011",
      "type": "transaction",
      "entry": [
        { "fullUrl": "urn:uuid:pat", "resource": { "resourceType": "Patient" } },
        { "fullUrl": "urn:uuid:obs", "resource": { "resourceType": "Observation" } }
      ]
    }
  };

  const validationRules = [
    { profile: "US Core Patient Profile v3.1.1", status: "Valid", rulesPassed: 14, issues: 0 },
    { profile: "US Core Laboratory Observation Profile", status: "Warning", rulesPassed: 8, issues: 1 }
  ];

  const validationLogs = [
    { severity: "warning", message: "Observation.effectiveDateTime is missing (Recommended field for clinical chronology)" }
  ];

  const handleCopy = () => {
    if (typeof navigator !== "undefined") {
      navigator.clipboard.writeText(JSON.stringify(mockJson[selectedResource], null, 2));
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">FHIR Resource Explorer</h2>
            <p className="text-sm text-muted-foreground">Inspect, validate, and download FHIR resources conforming with US Core profiles.</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={handleCopy} className="flex items-center space-x-1">
              <Copy className="h-4 w-4" />
              <span>{copySuccess ? "Copied!" : "Copy Active JSON"}</span>
            </Button>
            <Button variant="default" size="sm" className="flex items-center space-x-1">
              <Download className="h-4 w-4" />
              <span>Download FHIR Bundle</span>
            </Button>
          </div>
        </div>

        {/* Master columns layout */}
        <div className="grid gap-6 lg:grid-cols-4">
          
          {/* 1. LEFT SIDEBAR: NESTED RESOURCE TREE (Span 1) */}
          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <Layers className="h-4 w-4 text-primary" />
                  <span>Bundle Resources</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-2">
                {resourceTree.map((group, idx) => (
                  <div key={idx} className="space-y-2">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">{group.group}</span>
                    <div className="space-y-1">
                      {group.items.map((item, itemIdx) => (
                        <button
                          key={itemIdx}
                          onClick={() => setSelectedResource(item.id)}
                          className={`w-full text-left rounded p-2 text-xs flex items-center justify-between transition-colors ${
                            selectedResource === item.id 
                              ? "bg-primary text-primary-foreground font-semibold" 
                              : "hover:bg-muted"
                          }`}
                        >
                          <span className="truncate mr-2">{item.id}</span>
                          <Badge variant={selectedResource === item.id ? "secondary" : "default"} className="text-[9px] px-1 shrink-0">
                            {item.type}
                          </Badge>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* 2. MIDDLE AREA: CODE EDITOR & REFERENCE GRAPH (Span 2) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* JSON Code Editor */}
            <Card className="overflow-hidden">
              <CardHeader className="p-3 border-b border-border bg-muted/30 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-xs font-mono">{selectedResource}.json</CardTitle>
                <Badge variant="success" className="text-[9px]">FHIR R4</Badge>
              </CardHeader>
              <CardContent className="p-0">
                {/* Syntax highlighted JSON code block */}
                <pre className="p-4 bg-zinc-950 text-emerald-400 text-xs font-mono overflow-auto max-h-[350px] leading-relaxed select-all">
                  {JSON.stringify(mockJson[selectedResource], null, 2)}
                </pre>
              </CardContent>
            </Card>

            {/* Reference Graph connection diagram */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <GitFork className="h-4 w-4 text-primary" />
                  <span>FHIR Reference Map</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-2 flex items-center justify-center">
                {/* Visual SVG node connections */}
                <div className="flex items-center space-x-4 bg-muted/20 p-4 rounded border border-border text-xs font-mono w-full justify-around">
                  <div className="border border-border p-2 rounded bg-background shadow-sm text-center">
                    <p className="font-bold">df-obs-glucose</p>
                    <p className="text-[10px] text-muted-foreground">Observation</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <div className="border border-primary/30 p-2 rounded bg-primary/5 text-primary text-center">
                    <p className="font-bold">df-pat-blackwell</p>
                    <p className="text-[10px] text-primary/80">Patient</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <div className="border border-border p-2 rounded bg-background shadow-sm text-center">
                    <p className="font-bold">df-org-openhealth</p>
                    <p className="text-[10px] text-muted-foreground">Organization</p>
                  </div>
                </div>
              </CardContent>
            </Card>

          </div>

          {/* 3. RIGHT AREA: US CORE VALIDATOR & REPORTS (Span 1) */}
          <div className="space-y-6">
            
            {/* US Core Profile Checklist */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <ShieldCheck className="h-4 w-4 text-success" />
                  <span>US Core Compliance</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                {validationRules.map((rule, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold">{rule.profile}</span>
                      <Badge variant={rule.status === "Valid" ? "success" : "warning"}>{rule.status}</Badge>
                    </div>
                    <p className="text-muted-foreground text-[10px]">{rule.rulesPassed} validations passed • {rule.issues} issues</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Validation Issues Logger */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span>Validation Log</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                {validationLogs.map((log, idx) => (
                  <div key={idx} className="p-3 bg-warning/10 text-warning border border-warning/20 rounded-lg text-xs leading-relaxed">
                    <span className="font-bold uppercase text-[9px] block text-warning/90">{log.severity}</span>
                    <p className="mt-1">{log.message}</p>
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
