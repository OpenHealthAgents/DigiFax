"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "../../components/ui/alert";
import { 
  Bell, CheckCircle2, AlertTriangle, AlertCircle, 
  Trash2, MailOpen, ShieldAlert, Cpu, UserCheck, Inbox 
} from "lucide-react";

export default function NotificationsPage() {
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "warning" | "error" | "default">("default");

  const [notifications, setNotifications] = useState([
    { id: 1, title: "Epic EHR export transaction failed", desc: "Server returned 401 Unauthorized for client JWT assertion.", category: "Export Failure", unread: true, time: "5m ago", type: "error" },
    { id: 2, title: "New Document Assigned for Review", desc: "DF-9011 (Elizabeth Blackwell) is awaiting clinical verification.", category: "Review Assignment", unread: true, time: "10m ago", type: "assignment" },
    { id: 3, title: "@mention: review signature node", desc: "Naveen Raj requested verification on patient signature bounding box in DF-9009.", category: "Mention", unread: true, time: "1h ago", type: "mention" },
    { id: 4, title: "Medplum validations approved", desc: "Schema conformity checks passed for Patient Resource bundle.", category: "Workflow Alert", unread: false, time: "3h ago", type: "success" },
    { id: 5, title: "NATS intake dispatch received", desc: "file doc-9011-fax.pdf ingested successfully in queue.", category: "Workflow Alert", unread: false, time: "4h ago", type: "success" }
  ]);

  const triggerToast = (title: string, type: "success" | "warning" | "error" | "default") => {
    setToastType(type);
    setToastMessage(title);
    setTimeout(() => setToastMessage(""), 4000);
  };

  const handleMarkAllRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, unread: false })));
  };

  const handleMarkRead = (id: number) => {
    setNotifications(notifications.map((n) => n.id === id ? { ...n, unread: false } : n));
  };

  const handleDelete = (id: number) => {
    setNotifications(notifications.filter((n) => n.id !== id));
  };

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* Title widget */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Notification Center</h2>
            <p className="text-sm text-muted-foreground">Manage real-time pipeline warnings, reviewer assignments, and user mentions.</p>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={handleMarkAllRead} className="flex items-center space-x-1">
              <MailOpen className="h-4 w-4" />
              <span>Mark All as Read</span>
            </Button>
            <Button variant="ghost" size="sm" className="text-error hover:bg-error/10" onClick={() => setNotifications([])}>
              <span>Clear Inbox</span>
            </Button>
          </div>
        </div>

        {/* Local Toast Simulator Banner */}
        {toastMessage && (
          <div className="fixed bottom-4 right-4 z-50 max-w-sm shadow-lg border animate-in slide-in-from-bottom-5">
            <Alert variant={toastType === "error" ? "error" : toastType === "warning" ? "warning" : "success"}>
              <Bell className="h-4 w-4 animate-bounce" />
              <AlertTitle className="text-xs font-bold">New Notification Alert</AlertTitle>
              <AlertDescription className="text-[11px] font-semibold">{toastMessage}</AlertDescription>
            </Alert>
          </div>
        )}

        {/* Action simulators panel */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase text-muted-foreground">Notification Simulator Controls</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2 pt-2">
            <Button variant="outline" size="sm" onClick={() => triggerToast("Medplum FHIR validation approved successfully", "success")}>
              Simulate Ingest Success
            </Button>
            <Button variant="outline" size="sm" className="text-warning border-warning/30 hover:bg-warning/10" onClick={() => triggerToast("OCR confidence value below 80% threshold", "warning")}>
              Simulate OCR Warning
            </Button>
            <Button variant="outline" size="sm" className="text-error border-error/30 hover:bg-error/10" onClick={() => triggerToast("Epic Sandbox gateway returned 401 Unauthorized", "error")}>
              Simulate Export Failure
            </Button>
          </CardContent>
        </Card>

        {/* Master columns layout */}
        <div className="grid gap-6 lg:grid-cols-4">
          
          {/* 1. SIDEBAR FILTERS (Span 1) */}
          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                  <Inbox className="h-4 w-4 text-primary" />
                  <span>Inbox Filters</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-xs">
                <div className="flex justify-between items-center p-2 rounded hover:bg-muted cursor-pointer font-semibold">
                  <span>All Notifications</span>
                  <Badge variant="default">{notifications.length}</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded hover:bg-muted cursor-pointer text-muted-foreground">
                  <span>Unread Messages</span>
                  <Badge variant="warning">{unreadCount}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 2. INBOX LISTS (Span 3) */}
          <div className="lg:col-span-3 space-y-4">
            
            {/* List */}
            <div className="space-y-3">
              {notifications.length > 0 ? (
                notifications.map((n) => (
                  <div 
                    key={n.id} 
                    className={`flex items-start justify-between p-4 border rounded-lg bg-background transition-shadow hover:shadow-sm ${
                      n.unread ? "border-primary/40 bg-primary/5" : "border-border"
                    }`}
                  >
                    <div className="flex items-start space-x-3 min-w-0 mr-4">
                      {/* Active Indicator blue dot */}
                      {n.unread ? (
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                      ) : (
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-muted-foreground/30 shrink-0" />
                      )}

                      {/* Icon type */}
                      <div className={`mt-0.5 p-1 rounded-full shrink-0 ${
                        n.type === "error" ? "bg-error/10 text-error" :
                        n.type === "assignment" ? "bg-primary/10 text-primary" :
                        n.type === "mention" ? "bg-warning/10 text-warning" : "bg-success/10 text-success"
                      }`}>
                        {n.type === "error" ? <ShieldAlert className="h-4 w-4" /> :
                         n.type === "assignment" ? <UserCheck className="h-4 w-4" /> :
                         n.type === "mention" ? <Bell className="h-4 w-4" /> : <Cpu className="h-4 w-4" />}
                      </div>

                      {/* Content */}
                      <div className="min-w-0 text-xs">
                        <div className="flex items-center space-x-2">
                          <p className="font-bold truncate">{n.title}</p>
                          <Badge variant="default" className="text-[9px] px-1 py-0">{n.category}</Badge>
                        </div>
                        <p className="text-muted-foreground mt-0.5 leading-relaxed">{n.desc}</p>
                        <span className="text-[10px] text-muted-foreground mt-1.5 block">{n.time}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2 shrink-0">
                      {n.unread && (
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleMarkRead(n.id)}
                          className="h-7 text-[10px] font-semibold"
                        >
                          Mark Read
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => handleDelete(n.id)}
                        className="h-7 w-7 text-muted-foreground hover:text-error"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                  </div>
                ))
              ) : (
                <div className="text-center p-12 border border-dashed border-border rounded-lg text-muted-foreground text-xs">
                  All clean! No active notifications found.
                </div>
              )}
            </div>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
