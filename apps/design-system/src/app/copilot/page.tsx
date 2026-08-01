/**
 * @file page.tsx
 * @description DigiFax Clinical AI Copilot Workspace. Implements a multi-column chat helper
 * for explaining terminology mappings, summarizing documents, and detailing US Core validation failures.
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Badge } from "../../components/ui/badge";
import { 
  Sparkles, Send, FileText, CheckCircle2, AlertTriangle, 
  HelpCircle, Terminal, Bot, User, Bookmark 
} from "lucide-react";

export default function CopilotPage() {
  // state hooks tracking input boxes and conversation arrays
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "AI",
      text: "Hello! I am your MedIngest Clinical Copilot. How can I assist you with **DF-9011 (Elizabeth Blackwell)** today?",
      time: "10m ago"
    }
  ]);

  // Demographic context parameters for the active analyzed patient
  const activeDocContext = {
    id: "DF-9011",
    patient: "Elizabeth Blackwell",
    dob: "1988-05-12",
    type: "Lab Report",
    ocrAcc: "96.4%",
    validationStatus: "Warning"
  };

  // Preset quick prompt chips
  const quickPrompts = [
    { title: "Explain Code Maps", prompt: "Explain the LOINC concept mappings identified in this laboratory report." },
    { title: "Summarize Blood Panel", prompt: "Provide a clinical summary of the patient values extracted from the document." },
    { title: "Check US Core Errors", prompt: "Explain the US Core schema validation warnings identified for this Observation." }
  ];

  // Handles client message updates and queries simulated matching outputs
  const handleSendMessage = (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    // Append the user's message to the session logs
    const userMsg = { sender: "User", text: query, time: "Just now" };
    
    // Default reply when keywords are not hit
    let responseText = "I am auditing the active clinical context. Let me know if you would like me to explain validation thresholds or schema structures.";
    
    // Evaluate message against target concepts
    const normalized = query.toLowerCase();
    if (normalized.includes("code") || normalized.includes("loinc")) {
      responseText = "This document identifies **LOINC code 15074-8 (Glucose [Mass/volume] in Blood)**. LOINC is the international standard for identifying laboratory observations. The extracted result of **145.0 mg/dL** matches the 'High' reference boundary.";
    } else if (normalized.includes("summarize") || normalized.includes("blood")) {
      responseText = "### Clinical Summary: DF-9011\n* **Patient**: Elizabeth Blackwell (DOB: 1988-05-12)\n* **Extracted Result**: Fasting Glucose **145.0 mg/dL**\n* **Status**: **High** (Reference interval: 70-100 mg/dL)\n* **Compliance**: Conforms to US Core Patient Profile v3.1.1.";
    } else if (normalized.includes("us core") || normalized.includes("validation") || normalized.includes("error")) {
      responseText = "There is **1 validation warning** flagged:\n* **Observation.effectiveDateTime is missing**: US Core recommend this property to establish the chronological history of the analyte result. You can edit this field in the Metadata editor.";
    }

    const aiMsg = { sender: "AI", text: responseText, time: "Just now" };

    setMessages((prev) => [...prev, userMsg, aiMsg]);
    if (!textToSend) setInputText("");
  };

  return (
    <AppShell>
      <div className="space-y-6 flex flex-col h-[calc(100vh-8rem)]">
        
        {/* HEADER AREA */}
        <div className="shrink-0">
          <h2 className="text-3xl font-bold tracking-tight flex items-center space-x-2">
            <Sparkles className="h-7 w-7 text-primary" />
            <span>AI Copilot Workspace</span>
          </h2>
          <p className="text-sm text-muted-foreground">Ask questions, explain terminology maps, and request summaries of ingested documents.</p>
        </div>

        {/* Master columns grids */}
        <div className="grid gap-6 lg:grid-cols-4 flex-1 min-h-0 overflow-hidden">
          
          {/* LEFT COLUMN: INTERACTIVE CHAT PANEL */}
          <div className="lg:col-span-3 flex flex-col border border-border rounded-lg bg-background overflow-hidden min-h-0">
            
            {/* Session status banner */}
            <div className="flex items-center justify-between p-3 border-b border-border bg-muted/30 shrink-0">
              <span className="text-xs font-bold flex items-center space-x-2">
                <Bot className="h-4 w-4 text-primary" />
                <span>Active Chat Session</span>
              </span>
              <Badge variant="success">Online</Badge>
            </div>

            {/* Conversation list with vertical scroll */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`flex space-x-3 text-xs max-w-2xl ${
                    msg.sender === "AI" ? "mr-auto" : "ml-auto flex-row-reverse space-x-reverse"
                  }`}
                >
                  {/* Sender Icons */}
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center font-bold text-xs border shrink-0 ${
                    msg.sender === "AI" ? "bg-primary/20 border-primary/30 text-primary" : "bg-muted border-border"
                  }`}>
                    {msg.sender === "AI" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>

                  {/* Message container */}
                  <div className={`rounded-lg p-3 leading-relaxed border ${
                    msg.sender === "AI" 
                      ? "bg-muted/30 border-border text-foreground" 
                      : "bg-primary text-primary-foreground border-primary"
                  }`}>
                    {/* Render markdown lines */}
                    <div className="space-y-1">
                      {msg.text.split("\n").map((line, lineIdx) => {
                        if (line.startsWith("* ")) {
                          return <li key={lineIdx} className="ml-4 list-disc">{line.replace("* ", "")}</li>;
                        }
                        return <p key={lineIdx}>{line}</p>;
                      })}
                    </div>
                    <span className={`text-[9px] mt-1.5 block ${
                      msg.sender === "AI" ? "text-muted-foreground" : "text-primary-foreground/70"
                    }`}>
                      {msg.time}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Prompts shortcuts */}
            <div className="p-3 border-t border-border bg-muted/10 flex flex-wrap gap-2 shrink-0">
              {quickPrompts.map((qp, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(qp.prompt)}
                  className="flex items-center space-x-1.5 rounded-full border border-border bg-background px-3 py-1 text-[11px] font-medium hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                  aria-label={`Select prompt: ${qp.title}`}
                >
                  <Bookmark className="h-3 w-3 text-primary" />
                  <span>{qp.title}</span>
                </button>
              ))}
            </div>

            {/* Input form */}
            <div className="p-3 border-t border-border bg-background flex items-center space-x-2 shrink-0">
              <input
                type="text"
                placeholder="Ask about LOINC codes, validation warnings, or summarize..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-xs outline-none"
              />
              <Button size="icon" variant="default" onClick={() => handleSendMessage()} aria-label="Send Message">
                <Send className="h-4 w-4" />
              </Button>
            </div>

          </div>

          {/* RIGHT COLUMN: ACTIVE CONTEXT SUMMARY */}
          <div className="space-y-6">
            
            {/* Active patient metrics */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-primary" />
                  <span>Active Context</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase">Patient Profile</p>
                  <p className="font-bold text-sm">{activeDocContext.patient}</p>
                  <p className="text-muted-foreground text-[10px]">DOB: {activeDocContext.dob}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase">Active Document</p>
                  <p className="font-semibold">{activeDocContext.id} ({activeDocContext.type})</p>
                </div>
                <div className="pt-2 border-t border-border space-y-1">
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="font-semibold text-muted-foreground">OCR Accuracy</span>
                    <span className="font-bold text-primary">{activeDocContext.ocrAcc}</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="font-semibold text-muted-foreground">Validations</span>
                    <Badge variant="warning">{activeDocContext.validationStatus}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Capability parameters list */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <HelpCircle className="h-4 w-4 text-primary" />
                  <span>Copilot Capabilities</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 pt-2 text-xs text-muted-foreground leading-relaxed">
                <p>• **Explain terminology**: LOINC mapping references.</p>
                <p>• **Explain failures**: Detail US Core validation issues.</p>
                <p>• **Natural language search**: Query documents by patient demographics.</p>
              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
