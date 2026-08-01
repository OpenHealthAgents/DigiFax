import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import PlatformOperationsPage from "../app/admin/operations/page";
import "../app/globals.css";

const meta: Meta<typeof PlatformOperationsPage> = {
  title: "MedIngest/Administration/OperationsAdministration",
  component: PlatformOperationsPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof PlatformOperationsPage>;

export const DefaultOperationsConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY HEALTH CARDS ---
    const dbCard = canvas.getByText("Clinical Database");
    await expect(dbCard).toBeVisible();

    const temporalCard = canvas.getByText("Temporal Engine Workflow");
    await expect(temporalCard).toBeVisible();

    // --- 2. TRIGGER SYSTEM MAINTENANCE MODE LOCK ---
    const switchMaintenance = canvasElement.querySelector("#switch-maintenance") as HTMLButtonElement;
    await expect(switchMaintenance).toBeVisible();
    await userEvent.click(switchMaintenance);

    // Check warning alert appears
    const maintenanceAlert = await canvas.findByText("Maintenance Mode Active");
    await expect(maintenanceAlert).toBeVisible();

    // --- 3. TOGGLE FEATURE FLAG SWITCH ---
    const switchLlmValidation = canvasElement.querySelector("#switch-llm-validation") as HTMLButtonElement;
    await expect(switchLlmValidation).toBeVisible();
    await userEvent.click(switchLlmValidation);

    // --- 4. REFRESH HEALTH METRICS ---
    const btnRefreshHealth = canvasElement.querySelector("#btn-refresh-health") as HTMLButtonElement;
    await expect(btnRefreshHealth).toBeVisible();
    await userEvent.click(btnRefreshHealth);

    const refreshAlert = await canvas.findByText("Refreshed components checks latency metrics successfully.");
    await expect(refreshAlert).toBeVisible();
  },
};
