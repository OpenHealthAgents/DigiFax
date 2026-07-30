/**
 * @file page.tsx
 * @description DigiFax Tenant Branding Console.
 * 
 * Provides style configuration forms allowing tenants to white-label portals: custom themes,
 * typography, support contact channels, email layouts, PDF reports headers/footers, and watermarks.
 * Implements live client-side WCAG contrast ratio validators and stateful version rollback history.
 */

"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "../../../components/shell/app-shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Badge } from "../../../components/ui/badge";
import { Switch } from "../../../components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../../components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/ui/table";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { 
  Palette, FileText, Mail, Info, RefreshCw, CheckCircle2, 
  AlertTriangle, Eye, EyeOff, Layout, Globe, Phone, MailQuestion,
  FileSpreadsheet, Image as ImageIcon, History, ShieldCheck
} from "lucide-react";

// --- TYPES ---

interface BrandingVersion {
  version: number;
  timestamp: string;
  user: string;
  companyName: string;
  primaryColor: string;
  fontFamily: string;
  watermarkText: string;
}

export default function TenantBrandingPage() {
  // --- STATE STORES ---

  // Demographics
  const [companyName, setCompanyName] = useState("OpenHealth Medical Group");
  const [footerText, setFooterText] = useState("© 2026 OpenHealth Medical Group. All rights reserved.");

  // Styling Elements
  const [primaryColor, setPrimaryColor] = useState("#3B82F6");
  const [secondaryColor, setSecondaryColor] = useState("#10B981");
  const [accentColor, setAccentColor] = useState("#F59E0B");
  const [backgroundColor, setBackgroundColor] = useState("#FFFFFF");
  const [fontFamily, setFontFamily] = useState("Inter");
  const [fontSizeBase, setFontSizeBase] = useState("14px");

  // Logo URLs
  const [lightLogoUrl, setLightLogoUrl] = useState("https://openhealth.org/assets/light_logo.png");
  const [darkLogoUrl, setDarkLogoUrl] = useState("https://openhealth.org/assets/dark_logo.png");
  const [favIconUrl, setFavIconUrl] = useState("https://openhealth.org/assets/favicon.ico");

  // Support Contacts
  const [supportEmail, setSupportEmail] = useState("support@openhealthagents.org");
  const [supportPhone, setSupportPhone] = useState("+1 (555) 0199");
  const [supportWebsite, setSupportWebsite] = useState("https://openhealthagents.org/support");

  // Custom Backdrop Assets
  const [loginBackgroundUrl, setLoginBackgroundUrl] = useState("https://openhealth.org/assets/bg.jpg");
  const [dashboardBannerUrl, setDashboardBannerUrl] = useState("https://openhealth.org/assets/banner.jpg");

  // Email Templates branding
  const [emailPrimaryColor, setEmailPrimaryColor] = useState("#3B82F6");
  const [emailHeaderHtml, setEmailHeaderHtml] = useState("<div><h2>OpenHealth Alert</h2></div>");
  const [emailFooterHtml, setEmailFooterHtml] = useState("<div><p>This is a secure transmission.</p></div>");

  // Document PDF report templates
  const [watermarkText, setWatermarkText] = useState("CONFIDENTIAL PHI");
  const [reportHeaderHtml, setReportHeaderHtml] = useState("<div><h3>OpenHealth Clinical Analysis Summary</h3></div>");
  const [reportFooterHtml, setReportFooterHtml] = useState("<div><p>Page 1 of 1 • System verified</p></div>");

  // Live Previews Settings
  const [previewTab, setPreviewTab] = useState<"ui" | "email" | "pdf">("ui");
  const [previewDarkMode, setPreviewDarkMode] = useState(false);

  // Validation Checkers
  const [contrastRatio, setContrastRatio] = useState(4.5);
  const [isContrastValid, setIsContrastValid] = useState(true);

  // Version history records
  const [versions, setVersions] = useState<BrandingVersion[]>([
    {
      version: 1,
      timestamp: "2026-07-29T14:20:10Z",
      user: "kalyan@openhealthagents.org",
      companyName: "OpenHealth Hospital Corp",
      primaryColor: "#2563EB",
      fontFamily: "Outfit",
      watermarkText: "DRAFT ONLY"
    }
  ]);

  // Notifications banner feedback
  const [feedbackBanner, setFeedbackBanner] = useState("");
  const [feedbackType, setFeedbackType] = useState<"success" | "warning" | "error">("success");

  // --- CONTROLLER HANDLERS & COMPUTATIONS ---

  /**
   * Calculates relative sRGB luminance matching the backend validator formula.
   */
  const calculateLuminance = (hex: string): number => {
    const color = hex.replace("#", "");
    if (color.length !== 6) return 0;
    const r = parseInt(color.substring(0, 2), 16) / 255;
    const g = parseInt(color.substring(2, 4), 16) / 255;
    const b = parseInt(color.substring(4, 6), 16) / 255;

    const expand = (c: number) => {
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    };

    return 0.2126 * expand(r) + 0.7152 * expand(g) + 0.0722 * expand(b);
  };

  // Re-calculate WCAG AA contrast ratio dynamically on style color updates
  useEffect(() => {
    try {
      const l_primary = calculateLuminance(primaryColor);
      const l_background = calculateLuminance(backgroundColor);

      const l1 = Math.max(l_primary, l_background);
      const l2 = Math.min(l_primary, l_background);

      const ratio = (l1 + 0.05) / (l2 + 0.05);
      setContrastRatio(parseFloat(ratio.toFixed(2)));
      setIsContrastValid(ratio >= 3.0);
    } catch (e) {
      setIsContrastValid(false);
    }
  }, [primaryColor, backgroundColor]);

  const triggerFeedback = (msg: string, type: "success" | "warning" | "error" = "success") => {
    setFeedbackBanner(msg);
    setFeedbackType(type);
    setTimeout(() => setFeedbackBanner(""), 4000);
  };

  /**
   * Persists visual configuration state, generating a new version log index.
   */
  const handleSaveBranding = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isContrastValid) {
      triggerFeedback("Color palette fails WCAG AA minimum accessibility rules.", "error");
      return;
    }

    const nextVer = versions.length + 1;
    const newRecord: BrandingVersion = {
      version: nextVer,
      timestamp: new Date().toISOString(),
      user: "kalyan@openhealthagents.org",
      companyName: companyName,
      primaryColor: primaryColor,
      fontFamily: fontFamily,
      watermarkText: watermarkText
    };

    setVersions([newRecord, ...versions]);
    triggerFeedback(`Branding version ${nextVer} generated and applied successfully.`);
  };

  /**
   * Reverts current configuration states to a targeted version snapshot.
   */
  const handleRollback = (targetVer: BrandingVersion) => {
    setCompanyName(targetVer.companyName);
    setPrimaryColor(targetVer.primaryColor);
    setFontFamily(targetVer.fontFamily);
    setWatermarkText(targetVer.watermarkText);
    
    triggerFeedback(`Reverted portal branding settings to Version ${targetVer.version}.`, "warning");
  };

  return (
    <AppShell>
      <div className="space-y-6">
        
        {/* PANEL HEADER */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Portal Customizer</h2>
          <p className="text-sm text-muted-foreground">White-label your DigiFax portal. Configure styles, domain parameters, support channels, and PDF layouts.</p>
        </div>

        {/* Global actions banner */}
        {feedbackBanner && (
          <Alert variant={feedbackType === "success" ? "success" : feedbackType === "warning" ? "warning" : "error"}>
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle className="text-xs">System Alert</AlertTitle>
            <AlertDescription className="text-xs">{feedbackBanner}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          
          {/* LEFT: THEME EDITOR AND FORM CONTROLS */}
          <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="text-lg font-bold flex items-center space-x-2">
                <Palette className="h-5 w-5 text-primary" />
                <span>Theme Editor Customizer</span>
              </CardTitle>
              <CardDescription>Onboard style metrics and check contrast ratios.</CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <form onSubmit={handleSaveBranding} className="space-y-6">
                
                <Tabs defaultValue="demographics" className="space-y-4">
                  <TabsList className="grid w-full grid-cols-3 bg-muted/60 p-1 rounded-md">
                    <TabsTrigger value="demographics" className="text-xs">General</TabsTrigger>
                    <TabsTrigger value="styling" className="text-xs">Styles & Logos</TabsTrigger>
                    <TabsTrigger value="templates" className="text-xs">Templates</TabsTrigger>
                  </TabsList>

                  {/* FORM PANEL 1: DEMOGRAPHICS & CONTACTS */}
                  <TabsContent value="demographics" className="space-y-4 pt-2">
                    <div className="space-y-1">
                      <label htmlFor="company-name-input" className="text-xs font-semibold uppercase text-muted-foreground">Company Name</label>
                      <Input id="company-name-input" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="footer-text-input" className="text-xs font-semibold uppercase text-muted-foreground">Footer Text</label>
                      <Input id="footer-text-input" value={footerText} onChange={(e) => setFooterText(e.target.value)} />
                    </div>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="space-y-1">
                        <label htmlFor="support-email-input" className="text-xs font-semibold uppercase text-muted-foreground">Support Email</label>
                        <Input id="support-email-input" type="email" value={supportEmail} onChange={(e) => setSupportEmail(e.target.value)} />
                      </div>
                      <div className="space-y-1">
                        <label htmlFor="support-phone-input" className="text-xs font-semibold uppercase text-muted-foreground">Support Phone</label>
                        <Input id="support-phone-input" value={supportPhone} onChange={(e) => setSupportPhone(e.target.value)} />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="support-website-input" className="text-xs font-semibold uppercase text-muted-foreground">Support Website</label>
                      <Input id="support-website-input" value={supportWebsite} onChange={(e) => setSupportWebsite(e.target.value)} />
                    </div>
                  </TabsContent>

                  {/* FORM PANEL 2: STYLINGS & LOGO PATHS */}
                  <TabsContent value="styling" className="space-y-4 pt-2">
                    
                    {/* Theme Colors hex picker inputs */}
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="space-y-1">
                        <label htmlFor="primary-color-input" className="text-xs font-semibold uppercase text-muted-foreground">Primary Color</label>
                        <div className="flex space-x-2">
                          <Input id="primary-color-input" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} className="font-mono text-xs" />
                          <input type="color" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} className="w-10 h-10 border border-border rounded cursor-pointer" />
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label htmlFor="background-color-input" className="text-xs font-semibold uppercase text-muted-foreground">Background Color</label>
                        <div className="flex space-x-2">
                          <Input id="background-color-input" value={backgroundColor} onChange={(e) => setBackgroundColor(e.target.value)} className="font-mono text-xs" />
                          <input type="color" value={backgroundColor} onChange={(e) => setBackgroundColor(e.target.value)} className="w-10 h-10 border border-border rounded cursor-pointer" />
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="space-y-1">
                        <label htmlFor="font-family-select" className="text-xs font-semibold uppercase text-muted-foreground">Typography Font</label>
                        <select 
                          id="font-family-select"
                          value={fontFamily} 
                          onChange={(e) => setFontFamily(e.target.value)}
                          className="w-full h-10 rounded-md border border-border bg-background px-3 text-xs outline-none"
                        >
                          <option>Inter</option>
                          <option>Outfit</option>
                          <option>Roboto</option>
                          <option>Geist</option>
                        </select>
                      </div>
                      <div className="space-y-1">
                        <label htmlFor="font-size-input" className="text-xs font-semibold uppercase text-muted-foreground">Base Font Size</label>
                        <Input id="font-size-input" value={fontSizeBase} onChange={(e) => setFontSizeBase(e.target.value)} />
                      </div>
                    </div>

                    {/* Logo assets URLs */}
                    <div className="space-y-1">
                      <label htmlFor="light-logo-input" className="text-xs font-semibold uppercase text-muted-foreground">Light Mode Header Logo URL</label>
                      <Input id="light-logo-input" value={lightLogoUrl} onChange={(e) => setLightLogoUrl(e.target.value)} />
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="dark-logo-input" className="text-xs font-semibold uppercase text-muted-foreground">Dark Mode Header Logo URL</label>
                      <Input id="dark-logo-input" value={darkLogoUrl} onChange={(e) => setDarkLogoUrl(e.target.value)} />
                    </div>

                  </TabsContent>

                  {/* FORM PANEL 3: ASSET HTML TEMPLATES */}
                  <TabsContent value="templates" className="space-y-4 pt-2">
                    <div className="space-y-1">
                      <label htmlFor="watermark-input" className="text-xs font-semibold uppercase text-muted-foreground">PDF Document Watermark Text</label>
                      <Input id="watermark-input" value={watermarkText} onChange={(e) => setWatermarkText(e.target.value)} />
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="email-header-input" className="text-xs font-semibold uppercase text-muted-foreground">Email Header template HTML</label>
                      <textarea 
                        id="email-header-input"
                        value={emailHeaderHtml} 
                        onChange={(e) => setEmailHeaderHtml(e.target.value)}
                        className="w-full min-h-[60px] rounded-md border border-border bg-background p-2 font-mono text-xs outline-none"
                      />
                    </div>
                    <div className="space-y-1">
                      <label htmlFor="report-header-input" className="text-xs font-semibold uppercase text-muted-foreground">PDF Report Header template HTML</label>
                      <textarea 
                        id="report-header-input"
                        value={reportHeaderHtml} 
                        onChange={(e) => setReportHeaderHtml(e.target.value)}
                        className="w-full min-h-[60px] rounded-md border border-border bg-background p-2 font-mono text-xs outline-none"
                      />
                    </div>
                  </TabsContent>
                </Tabs>

                {/* WCAG Live accessibility contrast check badge */}
                <div className={`p-3 border rounded-lg flex items-center justify-between text-xs transition-colors ${isContrastValid ? "border-success/30 bg-success/5" : "border-error/30 bg-error/5"}`}>
                  <div className="space-y-0.5">
                    <p className="font-bold flex items-center space-x-1.5">
                      {isContrastValid ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-success" />
                          <span className="text-success">Contrast Ratio Compliant</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="h-4 w-4 text-error" />
                          <span className="text-error">Contrast Ratio Too Low</span>
                        </>
                      )}
                    </p>
                    <p className="text-muted-foreground text-[10px]">Calculated WCAG AA Ratio between primary theme and backdrop colors.</p>
                  </div>
                  <Badge variant={isContrastValid ? "success" : "error"} className="text-xs font-mono px-2.5 py-0.5">
                    {contrastRatio}:1
                  </Badge>
                </div>

                <div className="flex justify-end pt-2">
                  <Button id="save-branding-btn" type="submit" disabled={!isContrastValid}>Save Configuration</Button>
                </div>

              </form>
            </CardContent>
          </Card>

          {/* RIGHT: INTERACTIVE BRANDING LIVE PREVIEWS */}
          <div className="space-y-6">
            
            {/* Preview controls and tabs */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
                  <div>
                    <CardTitle className="text-base font-bold">Interactive Live Previews</CardTitle>
                    <CardDescription>Verify visual layouts under target environments.</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <label htmlFor="dark-preview-switch" className="text-xs text-muted-foreground uppercase font-semibold cursor-pointer">Dark Preview</label>
                    <Switch 
                      id="dark-preview-switch"
                      checked={previewDarkMode} 
                      onCheckedChange={setPreviewDarkMode} 
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-1">
                
                <Tabs value={previewTab} onValueChange={(v) => setPreviewTab(v as any)} className="space-y-4">
                  <TabsList className="grid w-full grid-cols-3 bg-muted/65 p-1 rounded-md">
                    <TabsTrigger value="ui" className="text-xs">App UI</TabsTrigger>
                    <TabsTrigger value="email" className="text-xs">Email</TabsTrigger>
                    <TabsTrigger value="pdf" className="text-xs">PDF Report</TabsTrigger>
                  </TabsList>

                  {/* PREVIEW CONTAINER 1: APP LIVE VIEW */}
                  <TabsContent value="ui">
                    <div 
                      id="app-preview-container"
                      className="border border-border/60 rounded-xl p-6 min-h-[220px] flex flex-col justify-between transition-colors duration-300"
                      style={{ 
                        backgroundColor: previewDarkMode ? "#0F172A" : "#FFFFFF", 
                        fontFamily: fontFamily,
                        color: previewDarkMode ? "#F8FAFC" : "#0F172A"
                      }}
                    >
                      <div className="flex justify-between items-center pb-4 border-b border-border/20">
                        <div className="flex items-center space-x-2">
                          <img 
                            id="preview-logo-img"
                            src={previewDarkMode ? darkLogoUrl : lightLogoUrl} 
                            alt="Logo" 
                            className="h-6 max-w-[120px] object-contain"
                            onError={(e) => {
                              // Fallback display if URL not loaded
                              (e.target as HTMLElement).style.display = "none";
                            }}
                          />
                          <span className="text-sm font-bold">{companyName}</span>
                        </div>
                        <Badge style={{ backgroundColor: primaryColor, color: "#FFF" }}>Active Workspace</Badge>
                      </div>

                      <div className="py-6 space-y-3">
                        <h4 className="text-xs font-semibold uppercase text-muted-foreground">Simulated Actions</h4>
                        <div className="flex space-x-2">
                          <Button style={{ backgroundColor: primaryColor, color: "#FFF" }} size="sm">Primary Button</Button>
                          <Button style={{ backgroundColor: secondaryColor, color: "#FFF" }} size="sm">Secondary</Button>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-border/20 flex justify-between items-center text-[10px] text-muted-foreground">
                        <span>{footerText}</span>
                        <span className="font-mono">{supportPhone}</span>
                      </div>
                    </div>
                  </TabsContent>

                  {/* PREVIEW CONTAINER 2: OUTBOUND EMAIL VIEW */}
                  <TabsContent value="email">
                    <div className="border border-border/60 rounded-xl p-4 bg-muted/10 font-sans text-xs space-y-4">
                      {/* Render mock html header */}
                      <div 
                        id="email-preview-header"
                        className="p-3 border-b border-border/30 font-bold"
                        style={{ color: emailPrimaryColor }}
                        dangerouslySetInnerHTML={{ __html: emailHeaderHtml }}
                      />
                      
                      <div className="p-3 space-y-2">
                        <p className="font-semibold">Subject: Secure Inbound Fax Ingestion Notification</p>
                        <p>A new electronic health record fax payload has been verified and delivered to your Athena EHR endpoint.</p>
                        <Button style={{ backgroundColor: emailPrimaryColor, color: "#FFF" }} className="h-8 text-[11px] px-3">View Record</Button>
                      </div>

                      {/* Render mock html footer */}
                      <div 
                        id="email-preview-footer"
                        className="p-3 border-t border-border/30 text-[10px] text-muted-foreground"
                        dangerouslySetInnerHTML={{ __html: emailFooterHtml }}
                      />
                    </div>
                  </TabsContent>

                  {/* PREVIEW CONTAINER 3: DIAGNOSTIC REPORT PDF VIEW */}
                  <TabsContent value="pdf">
                    <div className="border border-border/60 rounded-xl p-6 bg-white text-slate-900 font-serif text-xs min-h-[240px] flex flex-col justify-between relative overflow-hidden select-none shadow-sm">
                      
                      {/* Watermark layer overlay */}
                      <div 
                        id="pdf-watermark-overlay"
                        className="absolute inset-0 flex items-center justify-center text-red-500/10 font-bold text-3xl tracking-widest uppercase select-none pointer-events-none rotate-12"
                      >
                        {watermarkText}
                      </div>

                      {/* Header block template */}
                      <div 
                        id="pdf-preview-header"
                        className="pb-3 border-b border-slate-200 text-[11px]"
                        dangerouslySetInnerHTML={{ __html: reportHeaderHtml }}
                      />

                      {/* PHI chart mockup data */}
                      <div className="py-6 space-y-3 z-10">
                        <div className="flex justify-between font-bold">
                          <span>Patient: John Doe</span>
                          <span>DOB: 10/12/1984</span>
                        </div>
                        <Table>
                          <TableHeader>
                            <TableRow className="border-b border-slate-200 hover:bg-transparent">
                              <TableHead className="h-6 text-slate-900 text-[10px]">Test Panel</TableHead>
                              <TableHead className="h-6 text-slate-900 text-[10px] text-right">Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow className="border-b border-slate-100 hover:bg-transparent">
                              <TableCell className="py-1 text-[10px]">Luminance Contrast</TableCell>
                              <TableCell className="py-1 text-[10px] text-right font-bold text-slate-900">{contrastRatio}:1</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </div>

                      {/* Footer block template */}
                      <div 
                        id="pdf-preview-footer"
                        className="pt-3 border-t border-slate-200 text-[9px] text-slate-400 flex justify-between"
                        dangerouslySetInnerHTML={{ __html: reportFooterHtml }}
                      />

                    </div>
                  </TabsContent>
                </Tabs>

              </CardContent>
            </Card>

            {/* VERSION HISTORY LOGS AND ROLLBACKS */}
            <Card className="border border-border/80 bg-background/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-base font-bold flex items-center space-x-2">
                  <History className="h-4.5 w-4.5 text-primary" />
                  <span>Version History Logs</span>
                </CardTitle>
                <CardDescription>Revert visual styles to previous configurations.</CardDescription>
              </CardHeader>
              <CardContent className="pt-1">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Ver</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Company Name</TableHead>
                      <TableHead>Color</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {versions.map((ver, idx) => (
                      <TableRow key={idx} className="hover:bg-muted/10">
                        <TableCell className="font-bold text-xs">{ver.version}</TableCell>
                        <TableCell className="text-[10px] font-mono text-muted-foreground">
                          {new Date(ver.timestamp).toLocaleTimeString()}
                        </TableCell>
                        <TableCell className="font-semibold text-xs">{ver.companyName}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-1">
                            <span 
                              className="w-3 h-3 rounded-full border border-border/50 shrink-0" 
                              style={{ backgroundColor: ver.primaryColor }}
                            />
                            <span className="font-mono text-[10px]">{ver.primaryColor}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button 
                            id={`rollback-btn-v${ver.version}`}
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleRollback(ver)}
                            className="text-xs text-primary hover:bg-primary/10 h-7 px-2"
                          >
                            Revert
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

          </div>

        </div>

      </div>
    </AppShell>
  );
}
