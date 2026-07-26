"use client";

import React, { useState } from "react";
import { 
  Menu, Bell, ChevronDown, User, Settings, LogOut, LayoutDashboard, 
  FileText, Activity, Server, Shield, Layers, HelpCircle, Sun, Moon
} from "lucide-react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { CommandPalette } from "./command-palette";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedOrg, setSelectedOrg] = useState("OpenHealth Hospital");
  const [notificationsCount, setNotificationsCount] = useState(3);
  const [darkMode, setDarkMode] = useState(false);

  // Sync theme
  const toggleTheme = () => {
    const nextDark = !darkMode;
    setDarkMode(nextDark);
    const root = window.document.documentElement;
    if (nextDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  };

  const navItems = [
    { title: "Dashboard", icon: LayoutDashboard, path: "#dashboard" },
    { title: "Document Intake", icon: FileText, path: "#intake", badge: "New" },
    { title: "Reviewer Workspace", icon: Layers, path: "#reviewer" },
    { title: "EHR Export Queue", icon: Server, path: "#ehr" },
    { title: "Observability Metrics", icon: Activity, path: "#metrics" },
    { title: "Security & Settings", icon: Settings, path: "#settings" },
  ];

  return (
    <div className="flex min-h-screen bg-background text-foreground transition-colors duration-200">
      
      {/* 1. LEFT SIDEBAR PANEL (Collapsible) */}
      <aside 
        className={`fixed inset-y-0 left-0 z-30 flex flex-col border-r border-border bg-muted/30 transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-16"
        }`}
      >
        {/* Brand header */}
        <div className="flex h-16 items-center px-4 border-b border-border space-x-3 overflow-hidden">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
            DF
          </div>
          {sidebarOpen && (
            <span className="font-bold text-lg tracking-tight whitespace-nowrap">DigiFax Portal</span>
          )}
        </div>

        {/* Navigation list */}
        <nav className="flex-1 space-y-1 p-2">
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <a
                key={idx}
                href={item.path}
                className="flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-muted transition-colors relative"
              >
                <Icon className="h-5 w-5 text-muted-foreground shrink-0" />
                {sidebarOpen && (
                  <span className="ml-3 truncate">{item.title}</span>
                )}
                {sidebarOpen && item.badge && (
                  <Badge variant="warning" className="absolute right-2 px-1.5 py-0">
                    {item.badge}
                  </Badge>
                )}
              </a>
            );
          })}
        </nav>

        {/* Sidebar Footer info */}
        <div className="p-3 border-t border-border flex items-center space-x-3 overflow-hidden">
          <HelpCircle className="h-5 w-5 text-muted-foreground shrink-0" />
          {sidebarOpen && (
            <span className="text-xs text-muted-foreground whitespace-nowrap">v1.2.0 (US-Core R4)</span>
          )}
        </div>
      </aside>

      {/* Main container area wrapper offset by sidebar */}
      <div className={`flex flex-col flex-1 min-h-screen transition-all duration-300 ${
        sidebarOpen ? "pl-64" : "pl-16"
      }`}>
        
        {/* 2. TOP NAVIGATION BAR */}
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-border bg-background/95 backdrop-blur-md px-6">
          <div className="flex items-center space-x-4">
            {/* Sidebar toggle button */}
            <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle Sidebar">
              <Menu className="h-5 w-5" />
            </Button>

            {/* Breadcrumbs Path */}
            <div className="flex items-center space-x-1.5 text-sm font-medium text-muted-foreground">
              <span>DigiFax</span>
              <span>/</span>
              <span className="text-foreground">Reviewer Workspace</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Command Palette */}
            <CommandPalette />

            {/* Theme Toggle */}
            <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle Theme">
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* Organization Switcher */}
            <div className="relative">
              <button className="flex items-center space-x-1 rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-muted transition-colors">
                <span>{selectedOrg}</span>
                <ChevronDown className="h-3 w-3 text-muted-foreground" />
              </button>
            </div>

            {/* Notifications Trigger */}
            <div className="relative">
              <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
                <Bell className="h-5 w-5" />
                {notificationsCount > 0 && (
                  <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-error text-[10px] font-bold text-error-foreground">
                    {notificationsCount}
                  </span>
                )}
              </Button>
            </div>

            {/* User Dropdown Profile Profile */}
            <div className="h-8 w-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-sm cursor-pointer border border-primary/30">
              KK
            </div>
          </div>
        </header>

        {/* Page children contents */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
export default AppShell;
