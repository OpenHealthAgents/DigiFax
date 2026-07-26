"use client";

import React, { useState, useEffect } from "react";
import { Search, Terminal, ArrowRight, User, Settings } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "../ui/dialog";
import { Input } from "../ui/input";

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");

  // Listen for Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const commands = [
    { title: "Reviewer Workspace", category: "Navigation", icon: Terminal, action: "Go to workspace..." },
    { title: "Search Patient Records", category: "OpenSearch", icon: Search, action: "Search index..." },
    { title: "Configure EHR Credentials", category: "Settings", icon: Settings, action: "Open settings..." },
    { title: "UserProfile Settings", category: "User", icon: User, action: "Manage account..." }
  ];

  const filteredCommands = commands.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      {/* Visual helper badge */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center space-x-2 rounded-md border border-border bg-muted px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted/80 transition-colors"
      >
        <Search className="h-3 w-3" />
        <span>Search actions...</span>
        <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium opacity-100">
          <span className="text-xs">Ctrl</span>K
        </kbd>
      </button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-md p-0 overflow-hidden">
          <DialogHeader className="p-4 border-b border-border bg-muted/30">
            <DialogTitle className="text-sm font-semibold flex items-center space-x-2">
              <Terminal className="h-4 w-4 text-primary" />
              <span>DigiFax Command Menu</span>
            </DialogTitle>
            <DialogDescription className="sr-only">
              Quick actions command palette.
            </DialogDescription>
          </DialogHeader>

          {/* Search Input bar */}
          <div className="flex items-center px-3 border-b border-border">
            <Search className="h-4 w-4 mr-2 shrink-0 text-muted-foreground" />
            <input
              type="text"
              placeholder="Type a command or search page..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex h-11 w-full bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          {/* Command list */}
          <div className="max-h-[300px] overflow-y-auto p-2">
            {filteredCommands.length > 0 ? (
              <div className="space-y-1">
                {filteredCommands.map((cmd, idx) => {
                  const Icon = cmd.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => setIsOpen(false)}
                      className="w-full flex items-center justify-between rounded-md px-3 py-2 text-sm text-left hover:bg-muted transition-colors focus:outline-none focus:bg-muted"
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{cmd.title}</p>
                          <p className="text-xs text-muted-foreground">{cmd.category}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <span>{cmd.action}</span>
                        <ArrowRight className="h-3 w-3" />
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <p className="p-4 text-sm text-muted-foreground text-center">No commands found matching "{search}"</p>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
export default CommandPalette;
