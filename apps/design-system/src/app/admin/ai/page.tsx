/**
 * @file page.tsx
 * @description AI Provider Administration Console.
 * 
 * Provides system dashboards tracking LLM provider health status, latency speeds,
 * token metrics, cost summaries, fallback execution chains, and prompt sandboxes.
 */

"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Badge } from "../../../components/ui/badge";
import { Switch } from "../../../components/ui/switch";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/ui/table";
import { 
  Cpu, Activity, Zap, Coins, CheckCircle, AlertTriangle, ArrowRight,
  Play, ShieldCheck, PlayCircle, Loader2, RefreshCw, BarChart2
} from "lucide-react";

// --- TYPES ---
interface ProviderHealth {
  name: string;
  type: string;
  status: "ONLINE" | "OFFLINE" | "DEGRADED";
  latency: string;
  tokens: string;
  cost: string;
}

export default function AIAdministrationPage() {
  // --- STATE STORES ---
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState("");
  const [testResultType, setTestResultType] = useState<"success" | "error">("success");

  // Sandbox testing parameters
  const [selectedModel, setSelectedModel] = useState("Ollama (llama3)");
  const [systemInstruction, setSystemInstruction] = useState("You are a medical records extraction agent.");
  const [promptText, setPromptText] = useState("Extract patient HbA1c from: Patient John Doe presents with HbA1c of 7.4% on clinical analysis.");
  const [isStreaming, setIsStreaming] = useState(false);
  const [sandboxOutput, setSandboxOutput] = useState("");
  const [sandboxLatency, setSandboxLatency] = useState("");

  // Providers health registry
  const [providers, setProviders] = useState<ProviderHealth[]>([
    { name: "Ollama", type: "Local (llama3)", status: "ONLINE", latency: "84ms", tokens: "854k", cost: "$0.00 (Local)" },
    { name: "vLLM", type: "GPU Cluster (mistral)", status: "ONLINE", latency: "112ms", tokens: "1,204k", cost: "$0.00 (Local)" },
    { name: "OpenAI", type: "API (gpt-4o)", status: "ONLINE", latency: "1,150ms", tokens: "450k", cost: "$6.75" },
    { name: "llama.cpp", type: "Local (phi3)", status: "DEGRADED", latency: "250ms", tokens: "20k", cost: "$0.00 (Local)" },
    { name: "OpenRouter", type: "Gateway (claude-3)", status: "ONLINE", latency: "1,450ms", tokens: "80k", cost: "$2.40" }
  ]);

  // Fallback chains configurations
  const fallbackChain = [
    { step: 1, name: "Ollama", desc: "Local low-latency check", fallbackOn: "Timeout / Socket Err" },
    { step: 2, name: "vLLM", desc: "GPU Cluster secondary check", fallbackOn: "Out of memory" },
    { step: 3, name: "OpenAI", desc: "Cloud API high-quality fallback", fallbackOn: "Rate limit / Outage" }
  ];

  // --- CONTROLLER HANDLERS ---

  /**
   * Simulates connection verification of a provider.
   */
  const handleValidateConnection = (providerName: string) => {
    setIsTesting(true);
    setTestResult(`Pinging ${providerName} endpoint...`);
    setTestResultType("success");

    setTimeout(() => {
      setIsTesting(false);
      // Simulate status mutations
      setProviders(prev => prev.map(p => {
        if (p.name === providerName) {
          return { ...p, status: "ONLINE", latency: p.name === "OpenAI" ? "920ms" : "75ms" };
        }
        return p;
      }));
      setTestResult(`Connection to ${providerName} verified successfully. Endpoint responding.`);
      setTimeout(() => setTestResult(""), 4000);
    }, 1200);
  };

  /**
   * Simulates prompt testing sandboxes with streaming.
   */
  const handleRunSandbox = (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptText.trim()) return;

    setIsStreaming(true);
    setSandboxOutput("");
    setSandboxLatency("Computing...");

    const fullResponse = "Extracted Clinical Metric:\n- Patient: John Doe\n- Metric: HbA1c\n- Value: 7.4%\n- Validation Status: Compliant (exceeds base levels)";
    const words = fullResponse.split(" ");
    let currentWordIndex = 0;
    let outputAcc = "";

    // Simulate word-by-word streaming intervals
    const interval = setInterval(() => {
      if (currentWordIndex < words.length) {
        outputAcc += (currentWordIndex === 0 ? "" : " ") + words[currentWordIndex];
        setSandboxOutput(outputAcc);
        currentWordIndex++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
        setSandboxLatency("410ms (110 tokens/sec)");
      }
    }, 80);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">AI Provider Administration</h2>
          <p className="text-sm text-muted-foreground">Manage and validate local and cloud LLM inference engines. Configure retry strategies and review failover chains.</p>
        </div>

        {/* Global Connection Checker notification */}
        {testResult && (
          <Alert variant={testResultType === "success" ? "success" : "error"} className="py-2.5">
            <CheckCircle className="h-4 w-4" />
            <AlertTitle className="text-xs">Connection Verification</AlertTitle>
            <AlertDescription className="text-[11px]">{testResult}</AlertDescription>
          </Alert>
        )}

        {/* STATS HIGHLIGHTS */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Active Providers</span>
              <Cpu className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4 / 5 ONLINE</div>
              <p className="text-[10px] text-muted-foreground">Ollama, vLLM, OpenAI, OpenRouter</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Average Latency</span>
              <Activity className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">98ms (Local)</div>
              <p className="text-[10px] text-muted-foreground">Cloud endpoints average: 1.3s</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Token Volume</span>
              <Zap className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2.6M Tokens</div>
              <p className="text-[10px] text-muted-foreground">Ingested in the last 30 days</p>
            </CardContent>
          </Card>

          <Card className="border border-border/80 bg-background/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Local Savings</span>
              <Coins className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$1,840 Saved</div>
              <p className="text-[10px] text-success">85% of traffic routed to free models</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* LEFT: PROVIDERS DIRECTORY & CONNECTION VERIFIER */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <Activity className="h-5 w-5 text-primary" />
                  <span>AI Inference Providers Directory</span>
                </CardTitle>
                <CardDescription>Verify live latency metrics and run port handshakes.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Provider</TableHead>
                      <TableHead>Type/Model</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Latency</TableHead>
                      <TableHead>Spend</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {providers.map((p, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-bold text-xs">{p.name}</TableCell>
                        <TableCell className="text-xs font-semibold text-muted-foreground">{p.type}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={p.status === "ONLINE" ? "success" : p.status === "DEGRADED" ? "warning" : "error"}
                            className="text-[10px] px-2 py-0.5"
                          >
                            {p.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs text-foreground font-bold">{p.latency}</TableCell>
                        <TableCell className="font-mono text-[10px] text-muted-foreground">{p.cost}</TableCell>
                        <TableCell className="text-right">
                          <Button 
                            id={`test-connection-${p.name.toLowerCase()}`}
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleValidateConnection(p.name)}
                            disabled={isTesting}
                            className="text-xs text-primary hover:bg-primary/10 h-7 px-2"
                          >
                            {isTesting ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : "Validate"}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* MODEL & PROMPT TESTING SANDBOX */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-lg font-bold flex items-center space-x-2">
                  <PlayCircle className="h-5 w-5 text-primary" />
                  <span>Model & Prompt testing Sandbox</span>
                </CardTitle>
                <CardDescription>Simulate token streaming extractions directly on clinical inputs.</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <form onSubmit={handleRunSandbox} className="space-y-4">
                  
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <label htmlFor="model-select" className="text-xs font-semibold uppercase text-muted-foreground">Target Test Model</label>
                      <select 
                        id="model-select"
                        value={selectedModel} 
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                      >
                        <option>Ollama (llama3)</option>
                        <option>vLLM (mistral)</option>
                        <option>OpenAI (gpt-4o)</option>
                        <option>llama.cpp (phi3)</option>
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <label htmlFor="system-instruction-input" className="text-xs font-semibold uppercase text-muted-foreground">System Instruction</label>
                      <Input id="system-instruction-input" value={systemInstruction} onChange={(e) => setSystemInstruction(e.target.value)} />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label htmlFor="sandbox-prompt-textarea" className="text-xs font-semibold uppercase text-muted-foreground">Test Prompt Input</label>
                    <textarea 
                      id="sandbox-prompt-textarea"
                      value={promptText} 
                      onChange={(e) => setPromptText(e.target.value)}
                      className="w-full min-h-[80px] rounded-md border border-border bg-background p-2 text-xs outline-none focus:border-primary"
                    />
                  </div>

                  <div className="flex justify-between items-center pt-2">
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      <Zap className="h-3.5 w-3.5" />
                      <span>Speed: {sandboxLatency}</span>
                    </div>
                    <Button id="run-sandbox-btn" type="submit" disabled={isStreaming} className="flex items-center space-x-1.5">
                      {isStreaming ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>Streaming Output...</span>
                        </>
                      ) : (
                        <>
                          <Play className="h-3.5 w-3.5" />
                          <span>Run Extraction Test</span>
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Sandbox completion results display */}
                  {sandboxOutput && (
                    <div className="p-4 border border-border/80 bg-muted/20 rounded-lg space-y-2">
                      <div className="flex justify-between items-center text-[10px] text-muted-foreground border-b pb-1.5 uppercase font-semibold">
                        <span>Streaming Result Completion</span>
                        <span>Token Output Stream</span>
                      </div>
                      <pre id="sandbox-output-text" className="font-mono text-xs text-foreground whitespace-pre-wrap leading-relaxed select-all">
                        {sandboxOutput}
                      </pre>
                    </div>
                  )}

                </form>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT COLUMN: FALLBACK CHAIN VISUALIZATION & ANALYTICS */}
          <div className="space-y-6">
            
            {/* Fallback chain visual mapping */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <RefreshCw className="h-4.5 w-4.5 text-primary" />
                  <span>Prioritized Fallback Chain</span>
                </CardTitle>
                <CardDescription>Sequential routing flow resolved for secure faxes.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1">
                <div className="relative pl-6 space-y-6 border-l border-border/60">
                  {fallbackChain.map((step, idx) => (
                    <div key={idx} className="relative space-y-1">
                      
                      {/* Step Number Dot indicator */}
                      <span className="absolute -left-[31px] top-1 h-5 w-5 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white border border-background">
                        {step.step}
                      </span>
                      
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-xs text-foreground">{step.name}</span>
                        <Badge variant="secondary" className="text-[9px] text-muted-foreground font-mono">
                          {step.step === 1 ? "Primary" : "Failover"}
                        </Badge>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{step.desc}</p>
                      
                      {/* Fallback error indicator */}
                      {idx < fallbackChain.length - 1 && (
                        <div className="pt-1 flex items-center space-x-1.5 text-[9px] text-warning bg-warning/5 border border-warning/10 rounded px-1.5 py-0.5 w-max">
                          <AlertTriangle className="h-3 w-3" />
                          <span>Failover trigger: {step.fallbackOn}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Cost Estimation / Latency metrics charts mockup */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <BarChart2 className="h-4.5 w-4.5 text-primary" />
                  <span>Inbound Token Traffic Summary</span>
                </CardTitle>
                <CardDescription>Model queries distributions and spend rates.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1 text-xs">
                
                {/* Spend limits slider card bar indicators */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Ollama (Free)</span>
                    <span className="font-bold">1.8M tokens (69%)</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div className="bg-primary h-1.5 rounded-full" style={{ width: "69%" }} />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">OpenAI (Paid)</span>
                    <span className="font-bold">450k tokens (17%)</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div className="bg-warning h-1.5 rounded-full" style={{ width: "17%" }} />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">vLLM (Free)</span>
                    <span className="font-bold">350k tokens (14%)</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div className="bg-success h-1.5 rounded-full" style={{ width: "14%" }} />
                  </div>
                </div>

                <div className="pt-4 border-t flex justify-between items-center text-[10px] text-muted-foreground">
                  <span className="flex items-center space-x-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-success" />
                    <span>HIPAA Compliant routing</span>
                  </span>
                  <span>Spend Limit: 12%</span>
                </div>

              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
