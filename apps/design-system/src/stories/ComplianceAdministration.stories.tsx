import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import ComplianceAdministrationPage from "../app/admin/compliance/page";
import "../app/globals.css";

const meta: Meta<typeof ComplianceAdministrationPage> = {
  title: "MedIngest/Administration/ComplianceAdministration",
  component: ComplianceAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof ComplianceAdministrationPage>;

export const DefaultComplianceConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY METRICS CARDS ---
    const regsHeader = canvas.getByText("HIPAA, GDPR");
    await expect(regsHeader).toBeVisible();

    const auditHeader = canvas.getByText("4,821 Logs");
    await expect(auditHeader).toBeVisible();

    // --- 2. SWITCH TO RIGHT TO DELETION TAB ---
    const deletionTabTrigger = canvasElement.querySelector("#tab-deletion") as HTMLButtonElement;
    await expect(deletionTabTrigger).toBeVisible();
    await userEvent.click(deletionTabTrigger);

    const deletePatientInput = canvasElement.querySelector("#delete-patient-input") as HTMLInputElement;
    await expect(deletePatientInput).toBeVisible();

    const deleteJustificationInput = canvasElement.querySelector("#delete-justification-input") as HTMLTextAreaElement;
    await expect(deleteJustificationInput).toBeVisible();

    // --- 3. TEST DELETION BLOCKED BY ACTIVE LEGAL HOLD (pat-101) ---
    await userEvent.type(deletePatientInput, "pat-101");
    await userEvent.type(deleteJustificationInput, "Clinical compliance check");

    const deleteSubmitBtn = canvasElement.querySelector("#delete-submit-btn") as HTMLButtonElement;
    await expect(deleteSubmitBtn).toBeVisible();
    await userEvent.click(deleteSubmitBtn);

    // Assert blocked diagnosis warning alert
    const blockedAlert = await canvas.findByText("Patient pat-101 has an active legal hold. Deletion blocked.");
    await expect(blockedAlert).toBeVisible();

    // --- 4. TEST DELETION SUCCEEDED FOR UNRESTRICTED ACCOUNT (pat-102) ---
    await userEvent.clear(deletePatientInput);
    await userEvent.type(deletePatientInput, "pat-102");

    await userEvent.click(deleteSubmitBtn);

    const successAlert = await canvas.findByText("Patient pat-102 data purged successfully. PURGE logged in audit.");
    await expect(successAlert).toBeVisible();

    // --- 5. SWITCH TO CONSENT REGISTRY TAB & TOGGLE LOCK ---
    const consentsTabTrigger = canvasElement.querySelector("#tab-consents") as HTMLButtonElement;
    await expect(consentsTabTrigger).toBeVisible();
    await userEvent.click(consentsTabTrigger);

    const toggleHoldPat102 = canvasElement.querySelector("#toggle-hold-pat-102") as HTMLButtonElement;
    await expect(toggleHoldPat102).toBeVisible();
    await userEvent.click(toggleHoldPat102);
  },
};
