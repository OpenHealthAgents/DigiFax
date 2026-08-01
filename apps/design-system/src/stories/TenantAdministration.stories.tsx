/**
 * @file TenantAdministration.stories.tsx
 * @description Storybook story mapping and Playwright/Vitest end-to-end browser test definitions
 * for the Tenant Administration Console page component.
 * 
 * Enables verification of interactive clinical settings workflows (General profile adjustments,
 * facility registration, workspace additions, role mappings, API token generation, usage meters,
 * compliance logging) inside virtual chromium runner environments.
 */

import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import TenantAdminPage from "../app/admin/page";
import "../app/globals.css";

const meta: Meta<typeof TenantAdminPage> = {
  title: "MedIngest/Administration/TenantAdminConsole",
  component: TenantAdminPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof TenantAdminPage>;

/**
 * Standard preview story showing the complete reactive Tenant Administration Console,
 * with preset active Professional billing tiers and mocked clinical personnel rosters.
 */
export const DefaultConsoleView: Story = {
  render: () => <TenantAdminPage />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. GENERAL TAB AND DEMOGRAPHICS CHANGES ---
    // Test: verify tenant settings, input modification, and save response banner
    const tenantNameInput = canvas.getByLabelText("Tenant Name");
    await expect(tenantNameInput).toHaveValue("OpenHealth Hospital Network");
    await userEvent.clear(tenantNameInput);
    await userEvent.type(tenantNameInput, "OpenHealth Hospital Group");
    
    const saveDemographicsBtn = canvas.getByText("Save Demographics");
    await userEvent.click(saveDemographicsBtn);
    await expect(canvas.getByText("Tenant parameters and retention rules saved successfully.")).toBeInTheDocument();

    // --- 2. CLINICAL FACILITIES AND WORKSPACES MANAGEMENT ---
    // Test: switch tabs, create new facility card, and insert departmental workspaces
    const facilitiesTabTrigger = canvas.getByRole("tab", { name: /facilities/i });
    await userEvent.click(facilitiesTabTrigger);

    const orgNameInput = canvas.getByLabelText("Organization Name");
    const orgNpiInput = canvas.getByLabelText("NPI Identifier Code");
    const registerOrgBtn = canvas.getByRole("button", { name: "Register Facility" });

    await userEvent.type(orgNameInput, "OpenHealth West Outpost");
    await userEvent.type(orgNpiInput, "9876543210");
    await userEvent.click(registerOrgBtn);

    // Verify card is registered and listed
    await expect(canvas.getByText("OpenHealth West Outpost")).toBeInTheDocument();
    await expect(canvas.getByText("NPI ID: 9876543210")).toBeInTheDocument();

    // Add new departmental workspace
    const newOrgWsInput = canvasElement.querySelector("#ws-input-org-3") as HTMLInputElement;
    const newOrgWsAddBtn = canvasElement.querySelector("#ws-add-btn-org-3") as HTMLButtonElement;
    await userEvent.type(newOrgWsInput, "Radiology Division");
    await userEvent.click(newOrgWsAddBtn);
    await expect(canvas.getByText("Radiology Division")).toBeInTheDocument();

    // --- 3. ROSTER AND INVITATIONS PIPELINE ---
    // Test: suspend active operators and generate/dispatch pending invites
    const rosterTabTrigger = canvas.getByRole("tab", { name: /roster & invites/i });
    await userEvent.click(rosterTabTrigger);

    const suspendJaneBtn = canvasElement.querySelector("#toggle-user-btn-usr-3") as HTMLButtonElement;
    await userEvent.click(suspendJaneBtn);
    await expect(canvas.getByText("User security status modified.")).toBeInTheDocument();

    const inviteEmailInput = canvas.getByLabelText("Recipient Email");
    const sendInviteBtn = canvas.getByRole("button", { name: "Dispatch Invite Link" });
    await userEvent.type(inviteEmailInput, "new-reviewer@openhealthagents.org");
    await userEvent.click(sendInviteBtn);
    await expect(canvas.getByText("Invitation sent to new-reviewer@openhealthagents.org.")).toBeInTheDocument();

    // --- 4. RBAC ROLES AND API GATEWAYS KEYS ---
    // Test: create custom security roles, assign permissions, and generate secret credentials
    const rbacTabTrigger = canvas.getByRole("tab", { name: /roles & keys/i });
    await userEvent.click(rbacTabTrigger);

    const keyLabelInput = canvas.getByLabelText("API Token Label");
    const generateKeyBtn = canvas.getByRole("button", { name: "Generate Integration Key" });
    await userEvent.type(keyLabelInput, "Diagnostic Gateway Test Key");
    await userEvent.click(generateKeyBtn);
    await expect(canvas.getByText('API Key "Diagnostic Gateway Test Key" generated successfully.')).toBeInTheDocument();

    // --- 5. PLANS AND COMPUTING QUOTAS ---
    // Test: verify allocation progress meters and plan upgrades enabling restricted switches
    const plansTabTrigger = canvas.getByRole("tab", { name: /plans & quotas/i });
    await userEvent.click(plansTabTrigger);

    const storageBar = canvasElement.querySelector("#storage-quota-bar") as HTMLDivElement;
    await expect(storageBar).toBeInTheDocument();

    const enterpriseCard = canvas.getByText("Enterprise System");
    await userEvent.click(enterpriseCard);
    
    // Enterprise tier should enable the advanced analytics flag switch
    const advancedAnalyticsSwitch = canvasElement.querySelector("#flag-advanced-analytics-switch") as HTMLButtonElement;
    await expect(advancedAnalyticsSwitch).toBeEnabled();

    // --- 6. SECURE AUDIT TRAILS ---
    // Test: search logs and confirm log data matches filters
    const auditTabTrigger = canvas.getByRole("tab", { name: /audit trail/i });
    await userEvent.click(auditTabTrigger);

    const auditSearch = canvasElement.querySelector("#audit-search-input") as HTMLInputElement;
    await userEvent.type(auditSearch, "API_KEY_GENERATED");
    await expect(canvas.getByText("corr-8a92a01")).toBeInTheDocument();
  }
};
