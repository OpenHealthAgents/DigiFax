import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import AnalyticsAdministrationPage from "../app/admin/analytics/page";
import "../app/globals.css";

const meta: Meta<typeof AnalyticsAdministrationPage> = {
  title: "MedIngest/Administration/ExecutiveAnalytics",
  component: AnalyticsAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof AnalyticsAdministrationPage>;

export const DefaultAnalyticsConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY METRICS CARDS ---
    const orgCostHeader = canvas.getByText("$12,410.50");
    await expect(orgCostHeader).toBeVisible();

    const ingessionsHeader = canvas.getByText("142,500 faxes");
    await expect(ingessionsHeader).toBeVisible();

    // --- 2. SWITCH TO OPERATIONS TAB ---
    const opsTabTrigger = canvasElement.querySelector("#tab-ops") as HTMLButtonElement;
    await expect(opsTabTrigger).toBeVisible();
    await userEvent.click(opsTabTrigger);

    const timeHeader = canvas.getByText("12.8s avg");
    await expect(timeHeader).toBeVisible();

    // --- 3. SWITCH TO REVENUE TAB ---
    const revTabTrigger = canvasElement.querySelector("#tab-rev") as HTMLButtonElement;
    await expect(revTabTrigger).toBeVisible();
    await userEvent.click(revTabTrigger);

    const cardCost = canvas.getByText("$4,500.00");
    await expect(cardCost).toBeVisible();

    // --- 4. INTERACT WITH FILTERS ---
    const dateSelect = canvasElement.querySelector("#select-date-range") as HTMLSelectElement;
    await expect(dateSelect).toBeVisible();
    await userEvent.selectOptions(dateSelect, "last-7");

    const deptSelect = canvasElement.querySelector("#select-department") as HTMLSelectElement;
    await expect(deptSelect).toBeVisible();
    await userEvent.selectOptions(deptSelect, "cardiology");

    // --- 5. SAVE CURRENT LAYOUT CONFIGURATION ---
    const inputSaveName = canvasElement.querySelector("#input-save-name") as HTMLInputElement;
    await expect(inputSaveName).toBeVisible();
    await userEvent.type(inputSaveName, "Custom Cardiology Summary");

    const btnSaveDashboard = canvasElement.querySelector("#btn-save-dashboard") as HTMLButtonElement;
    await expect(btnSaveDashboard).toBeVisible();
    await userEvent.click(btnSaveDashboard);

    // Verify it added to sidebar list
    const savedItem = await canvas.findByText("Custom Cardiology Summary");
    await expect(savedItem).toBeVisible();

    // --- 6. TRIGGER SHARING LINK DISPATCH ---
    const btnShareDashboard = canvasElement.querySelector("#btn-share-dashboard") as HTMLButtonElement;
    await expect(btnShareDashboard).toBeVisible();
    await userEvent.click(btnShareDashboard);

    const shareFeedback = await canvas.findByText("Copied Link!");
    await expect(shareFeedback).toBeVisible();
  },
};
