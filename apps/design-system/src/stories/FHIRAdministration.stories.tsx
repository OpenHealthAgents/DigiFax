import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import FHIRAdministrationPage from "../app/admin/fhir/page";
import "../app/globals.css";

const meta: Meta<typeof FHIRAdministrationPage> = {
  title: "DigiFax/Administration/FHIRAdministration",
  component: FHIRAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof FHIRAdministrationPage>;

export const DefaultFHIRConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY METRICS HIGHLIGHTS ---
    const activeHeader = canvas.getByText("6 Profiles");
    await expect(activeHeader).toBeVisible();

    const conformanceHeader = canvas.getByText("100% R4");
    await expect(conformanceHeader).toBeVisible();

    // --- 2. SWITCH TO INTERACTIVE VALIDATOR TAB ---
    const validatorTabTrigger = canvasElement.querySelector("#validator-tab-trigger") as HTMLButtonElement;
    await expect(validatorTabTrigger).toBeVisible();
    await userEvent.click(validatorTabTrigger);

    // Verify validator elements are visible
    const profileSelect = canvasElement.querySelector("#validator-profile-select") as HTMLSelectElement;
    await expect(profileSelect).toBeVisible();

    // --- 3. TRIGGER VALIDATION CHECKS (Conforms by default) ---
    const validateBtn = canvasElement.querySelector("#validate-btn") as HTMLButtonElement;
    await expect(validateBtn).toBeVisible();
    await userEvent.click(validateBtn);

    // Wait for mock validation check simulation timeout
    const successDiagnostic = await canvas.findByText("Conforms perfectly");
    await expect(successDiagnostic).toBeVisible();

    // --- 4. TOGGLE IMPLEMENTATION GUIDE CONTROLLER (Go back to IG tab) ---
    const igTabTrigger = canvas.getByText("Implementation Guides");
    await userEvent.click(igTabTrigger);

    const toggleUsCore = canvasElement.querySelector("#toggle-us-core") as HTMLButtonElement;
    await expect(toggleUsCore).toBeVisible();
    // Toggle US Core switch state
    await userEvent.click(toggleUsCore);
  },
};
