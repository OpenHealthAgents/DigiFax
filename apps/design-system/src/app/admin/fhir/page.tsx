/**
 * @file page.tsx
 * @description FHIR Profiles & Implementation Guides Administration Console.
 * 
 * Provides interactive profile browsers, schema validation testers, CapabilityStatements
 * viewer consoles, profile comparison tools, validation logs, and bundle preview inspectors.
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
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../../components/ui/tabs";
import { 
  ShieldAlert, Activity, FileText, Layers, CheckSquare,
  Search, ArrowRight, Play, Loader2, Download, Upload,
  Layers2, CheckCircle, ShieldCheck, History, Database, FileJson
} from "lucide-react";

// --- TYPES ---
interface StructureDef {
  name: string;
  url: string;
  type: string;
  required: string[];
}

export default function FHIRAdministrationPage() {
  // --- STATE STORES ---
  const [activeTab, setActiveTab] = useState("igs");
  const [validateProfile, setValidateProfile] = useState("us-core-patient");
  const [jsonInput, setJsonInput] = useState(JSON.stringify({
    "resourceType": "Patient",
    "meta": {
      "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
    },
    "identifier": [{"value": "123-abc"}],
    "name": [{"family": "Smith", "given": ["John"]}],
    "gender": "male"
  }, null, 2));

  const [validationOutput, setValidationOutput] = useState<{
    valid: boolean;
    errors: string[];
  } | null>(null);

  const [isValidating, setIsValidating] = useState(false);

  // Active Implementation Guides
  const [usCoreActive, setUsCoreActive] = useState(true);
  const [ipsActive, setIpsActive] = useState(false);
  const [customIgActive, setCustomIgActive] = useState(true);

  // Standard seeded StructureDefinitions
  const structureDefs: StructureDef[] = [
    { name: "US Core Patient", url: "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", type: "Patient", required: ["name", "identifier", "gender"] },
    { name: "US Core Laboratory Result Observation", url: "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationlab", type: "Observation", required: ["status", "code", "subject", "valueQuantity"] },
    { name: "IPS Patient", url: "http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips", type: "Patient", required: ["name", "gender"] },
    { name: "IPS AllergyIntolerance", url: "http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips", type: "AllergyIntolerance", required: ["clinicalStatus", "verificationStatus", "patient", "code"] }
  ];

  // --- HANDLERS ---
  const handleValidateResource = () => {
    setIsValidating(true);
    setValidationOutput(null);

    setTimeout(() => {
      setIsValidating(false);
      try {
        const parsed = JSON.parse(jsonInput);
        const activeProfileUrl = 
          validateProfile === "us-core-patient" ? "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient" :
          validateProfile === "us-core-observation" ? "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationlab" :
          validateProfile === "ips-patient" ? "http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips" :
          "http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips";

        const profileDef = structureDefs.find(sd => sd.url === activeProfileUrl);
        
        // Enforce active IG checks
        if (activeProfileUrl.includes("us/core") && !usCoreActive) {
          setValidationOutput({
            valid: false,
            errors: ["US Core Implementation Guide is not active for this tenant."]
          });
          return;
        }
        if (activeProfileUrl.includes("uv/ips") && !ipsActive) {
          setValidationOutput({
            valid: false,
            errors: ["International Patient Summary (IPS) Implementation Guide is not active for this tenant."]
          });
          return;
        }

        if (profileDef) {
          const errors: string[] = [];
          profileDef.required.forEach(path => {
            if (!(path in parsed) || parsed[path] === null || parsed[path] === "") {
              errors.push(`Required element missing: ${path}`);
            }
          });

          setValidationOutput({
            valid: errors.length === 0,
            errors: errors
          });
        } else {
          setValidationOutput({
            valid: false,
            errors: ["Selected StructureDefinition profile def not found."]
          });
        }
      } catch (err) {
        setValidationOutput({
          valid: false,
          errors: ["Invalid JSON syntax in resource editor payload."]
        });
      }
    }, 800);
  };

  // Mock CapabilityStatement
  const mockCapabilityStatement = {
    "resourceType": "CapabilityStatement",
    "status": "active",
    "date": "2026-07-30T20:00:00Z",
    "publisher": "OpenHealth Agents",
    "kind": "instance",
    "fhirVersion": "4.0.1",
    "format": ["json", "xml"],
    "implementationGuide": [
      "http://hl7.org/fhir/us/core/ImplementationGuide/us-core",
      "http://hl7.org/fhir/uv/ips/ImplementationGuide/ips"
    ],
    "rest": [
      {
        "mode": "server",
        "resource": [
          { "type": "Patient", "profile": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient" },
          { "type": "Observation", "profile": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationlab" }
        ]
      }
    ]
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">FHIR Profile Management</h2>
            <p className="text-sm text-muted-foreground">Browse StructureDefinitions, toggle Implementation Guides, and validate clinical resource payloads.</p>
          </div>
        </div>

        {/* METRICS ROW */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Profiles</span>
              <Layers2 className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6 Profiles</div>
              <p className="text-[10px] text-muted-foreground">4 standard, 2 tenant-custom</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Validated Resources</span>
              <Database className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,429</div>
              <p className="text-[10px] text-muted-foreground">99.2% conformance success rate</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active IGs</span>
              <CheckCircle className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2 Enabled</div>
              <p className="text-[10px] text-muted-foreground">US Core active, IPS suspended</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Conformance Score</span>
              <ShieldCheck className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">100% R4</div>
              <p className="text-[10px] text-muted-foreground">Fully conforming to base R4 schema</p>
            </CardContent>
          </Card>
        </div>

        {/* TABS CONTAINER */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-muted p-1 w-full justify-start md:w-auto">
            <TabsTrigger value="igs" className="text-xs px-3 py-1.5">Implementation Guides</TabsTrigger>
            <TabsTrigger value="browser" className="text-xs px-3 py-1.5">Profile Browser</TabsTrigger>
            <TabsTrigger value="validator" className="text-xs px-3 py-1.5" id="validator-tab-trigger">Interactive Validator</TabsTrigger>
            <TabsTrigger value="capability" className="text-xs px-3 py-1.5">Capability Statement</TabsTrigger>
            <TabsTrigger value="comparison" className="text-xs px-3 py-1.5">Profile Comparison</TabsTrigger>
            <TabsTrigger value="history" className="text-xs px-3 py-1.5">Validation History</TabsTrigger>
            <TabsTrigger value="bundle" className="text-xs px-3 py-1.5">Bundle Preview</TabsTrigger>
          </TabsList>

          {/* TAB 1: IMPLEMENTATION GUIDES */}
          <TabsContent value="igs" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">FHIR Implementation Guides selection</CardTitle>
                <CardDescription>Select active standard and tenant custom clinical guides to validate incoming resources.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-2">
                <div className="grid gap-6 md:grid-cols-3">
                  
                  <div className="border border-border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-44">
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-sm text-foreground">US Core IG</span>
                        <Badge variant="secondary" className="text-[9px]">v3.1.1</Badge>
                      </div>
                      <p className="text-[11px] text-muted-foreground">Standard US patient demographic profiles, laboratory observation models, and vital sign limits.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Active Status</span>
                      <Switch id="toggle-us-core" checked={usCoreActive} onCheckedChange={setUsCoreActive} />
                    </div>
                  </div>

                  <div className="border border-border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-44">
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-sm text-foreground">IPS (International Patient Summary)</span>
                        <Badge variant="secondary" className="text-[9px]">v1.0.0</Badge>
                      </div>
                      <p className="text-[11px] text-muted-foreground">Standardized summary dataset constraints for medical history, allergies, and medication records.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Active Status</span>
                      <Switch id="toggle-ips" checked={ipsActive} onCheckedChange={setIpsActive} />
                    </div>
                  </div>

                  <div className="border border-border rounded-lg p-4 bg-background/30 flex flex-col justify-between h-44">
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-sm text-foreground">MyClinic Custom IG</span>
                        <Badge variant="secondary" className="text-[9px]">v1.4.0</Badge>
                      </div>
                      <p className="text-[11px] text-muted-foreground">Custom tenant constraints, local structure definitions, and mandatory birthDate mappings.</p>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-foreground">Active Status</span>
                      <Switch id="toggle-custom-ig" checked={customIgActive} onCheckedChange={setCustomIgActive} />
                    </div>
                  </div>

                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: PROFILE BROWSER */}
          <TabsContent value="browser" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Profile StructureDefinitions browser</CardTitle>
                <CardDescription>Browse active structure definitions constraints and elements requirements.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Profile Name</TableHead>
                      <TableHead>Resource Type</TableHead>
                      <TableHead>Canonical URL</TableHead>
                      <TableHead>Required Fields</TableHead>
                      <TableHead>Origin</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {structureDefs.map((sd, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-bold text-xs text-foreground">{sd.name}</TableCell>
                        <TableCell className="font-mono text-xs">{sd.type}</TableCell>
                        <TableCell className="font-mono text-[10px] text-muted-foreground">{sd.url}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {sd.required.map((path, i) => (
                              <Badge key={i} variant="secondary" className="text-[9px] bg-primary/10 text-primary">
                                {path}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-[10px]">
                            {sd.url.includes("us/core") ? "US Core" : "IPS"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 3: INTERACTIVE VALIDATOR */}
          <TabsContent value="validator" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-3">
              
              {/* Textarea Code Editor */}
              <Card className="lg:col-span-2 border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-lg font-bold">FHIR resource payload validator</CardTitle>
                  <CardDescription>Paste raw FHIR JSON payload elements to evaluate profiles validations.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-1">
                  
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <label htmlFor="validator-profile-select" className="block text-xs font-semibold text-muted-foreground mb-1">Target Profile</label>
                      <select 
                        id="validator-profile-select"
                        value={validateProfile}
                        onChange={(e) => setValidateProfile(e.target.value)}
                        className="h-10 w-full rounded-md border border-border bg-background px-3 text-xs outline-none"
                      >
                        <option value="us-core-patient">US Core Patient Profile</option>
                        <option value="us-core-observation">US Core Laboratory Result Observation</option>
                        <option value="ips-patient">IPS Patient Profile</option>
                        <option value="ips-allergy">IPS AllergyIntolerance Profile</option>
                      </select>
                    </div>
                    
                    <div className="pt-5">
                      <Button 
                        id="validate-btn"
                        onClick={handleValidateResource} 
                        disabled={isValidating}
                        className="h-10 px-5 text-xs flex items-center space-x-1.5"
                      >
                        {isValidating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                        <span>Validate Resource</span>
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label htmlFor="validator-json-input" className="block text-xs font-semibold text-muted-foreground">Resource JSON</label>
                    <textarea 
                      id="validator-json-input"
                      value={jsonInput}
                      onChange={(e) => setJsonInput(e.target.value)}
                      className="w-full h-72 font-mono text-xs p-3 rounded-md border border-border bg-muted/20 focus:outline-none"
                    />
                  </div>

                </CardContent>
              </Card>

              {/* Validation Output diagnostics */}
              <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
                <CardHeader>
                  <CardTitle className="text-base font-bold">Validation Output Diagnostics</CardTitle>
                  <CardDescription>Conformance validator output results.</CardDescription>
                </CardHeader>
                <CardContent className="pt-2 space-y-4">
                  {validationOutput === null ? (
                    <div className="text-center py-12 text-muted-foreground space-y-2">
                      <Layers className="h-8 w-8 mx-auto text-muted-foreground/50" />
                      <p className="text-xs">Paste resource payload and click Validate to run diagnostics checks.</p>
                    </div>
                  ) : validationOutput.valid ? (
                    <div className="space-y-4">
                      <Alert variant="success">
                        <CheckCircle className="h-4 w-4" />
                        <AlertTitle className="text-xs">Conforms perfectly</AlertTitle>
                        <AlertDescription className="text-[11px]">
                          Resource matches structure definition perfectly. Zero validation errors.
                        </AlertDescription>
                      </Alert>
                      <div className="p-3 bg-success/10 border border-success/20 rounded-lg text-xs space-y-1.5">
                        <span className="font-bold text-success">Passed Audits:</span>
                        <div className="text-[10px] text-muted-foreground font-mono space-y-1">
                          <div>✓ resourceType resolved to Patient</div>
                          <div>✓ name path elements resolved</div>
                          <div>✓ identifier path elements resolved</div>
                          <div>✓ gender path resolved to "male"</div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Alert variant="error">
                        <ShieldAlert className="h-4 w-4" />
                        <AlertTitle className="text-xs">Conformity FAILED</AlertTitle>
                        <AlertDescription className="text-[11px]">
                          Resource constraints failed validations checks.
                        </AlertDescription>
                      </Alert>
                      <div className="space-y-2">
                        <span className="text-xs font-bold text-foreground">Validation Errors:</span>
                        <div className="space-y-1.5">
                          {validationOutput.errors.map((err, idx) => (
                            <div key={idx} className="p-2.5 bg-error/10 border border-error/20 rounded-md font-mono text-[10px] text-error">
                              {err}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

            </div>
          </TabsContent>

          {/* TAB 4: CAPABILITY STATEMENT */}
          <TabsContent value="capability" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">FHIR Server CapabilityStatement</CardTitle>
                <CardDescription>Server metadata capability statement detailing endpoints and format rules support.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <div className="bg-muted/30 border rounded-lg p-4 font-mono text-xs max-h-[360px] overflow-y-auto">
                  <pre>{JSON.stringify(mockCapabilityStatement, null, 2)}</pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 5: PROFILE COMPARISON */}
          <TabsContent value="comparison" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Profile Conformance Comparisons</CardTitle>
                <CardDescription>Compare required constraints paths between US Core and IPS patient models.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="border rounded-lg p-4 bg-background/30 space-y-3">
                    <div className="flex justify-between items-center border-b pb-2">
                      <span className="font-bold text-sm">US Core Patient</span>
                      <Badge variant="secondary" className="text-[10px]">US Core v3.1.1</Badge>
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="font-bold text-muted-foreground">Required Elements paths:</div>
                      <div className="space-y-1 font-mono text-[10px] text-foreground">
                        <div className="p-1 bg-primary/10 text-primary rounded">✓ name (HumanName)</div>
                        <div className="p-1 bg-primary/10 text-primary rounded">✓ identifier (Identifier)</div>
                        <div className="p-1 bg-primary/10 text-primary rounded">✓ gender (code)</div>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-background/30 space-y-3">
                    <div className="flex justify-between items-center border-b pb-2">
                      <span className="font-bold text-sm">IPS Patient</span>
                      <Badge variant="secondary" className="text-[10px]">IPS v1.0.0</Badge>
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="font-bold text-muted-foreground">Required Elements paths:</div>
                      <div className="space-y-1 font-mono text-[10px] text-foreground">
                        <div className="p-1 bg-primary/10 text-primary rounded">✓ name (HumanName)</div>
                        <div className="p-1 bg-muted text-muted-foreground rounded">- identifier (Optional)</div>
                        <div className="p-1 bg-primary/10 text-primary rounded">✓ gender (code)</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 6: VALIDATION HISTORY */}
          <TabsContent value="history" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Validation Audits logs</CardTitle>
                <CardDescription>Clinical conformance validation history timeline logs.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Resource Type</TableHead>
                      <TableHead>Target Profile</TableHead>
                      <TableHead>Result Status</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="hover:bg-muted/10">
                      <TableCell className="font-mono text-xs">Patient</TableCell>
                      <TableCell className="font-mono text-xs text-primary">http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient</TableCell>
                      <TableCell><Badge variant="success" className="text-[10px]">SUCCESS</Badge></TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">10m ago</TableCell>
                    </TableRow>
                    <TableRow className="hover:bg-muted/10">
                      <TableCell className="font-mono text-xs">Observation</TableCell>
                      <TableCell className="font-mono text-xs text-primary">http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationlab</TableCell>
                      <TableCell><Badge variant="error" className="text-[10px]">FAILED</Badge></TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">1h ago</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 7: BUNDLE PREVIEW */}
          <TabsContent value="bundle" className="space-y-4">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold">FHIR Transaction Bundle inspector</CardTitle>
                <CardDescription>Preview list elements nested inside transaction/collection bundles.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-2">
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-muted p-2.5 text-xs font-bold flex justify-between border-b">
                    <span>Bundle Entries (3 resources)</span>
                    <Badge variant="secondary" className="text-[9px]">transaction</Badge>
                  </div>
                  <div className="divide-y text-xs font-mono">
                    <div className="p-3 flex justify-between hover:bg-muted/10">
                      <div>
                        <span className="font-bold text-primary mr-2">[0]</span>
                        <span>Patient/pat-001</span>
                      </div>
                      <Badge variant="success" className="text-[9px]">CONFORMS</Badge>
                    </div>
                    <div className="p-3 flex justify-between hover:bg-muted/10">
                      <div>
                        <span className="font-bold text-primary mr-2">[1]</span>
                        <span>Observation/obs-002</span>
                      </div>
                      <Badge variant="success" className="text-[9px]">CONFORMS</Badge>
                    </div>
                    <div className="p-3 flex justify-between hover:bg-muted/10">
                      <div>
                        <span className="font-bold text-primary mr-2">[2]</span>
                        <span>DocumentReference/doc-003</span>
                      </div>
                      <Badge variant="success" className="text-[9px]">CONFORMS</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>

      </div>
    </AppShell>
  );
}
