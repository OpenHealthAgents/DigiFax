import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import MeteringAdministrationPage from "../app/admin/metering/page";
import "../app/globals.css";

const meta: Meta<typeof MeteringAdministrationPage> = {
  title: "DigiFax/Administration/UsageAdministration",
  component: MeteringAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof MeteringAdministrationPage>;

export const DefaultUsageConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY METRICS CARDS ---
    const costMetric = canvasElement.querySelector("#metric-accrued-cost") as HTMLElement;
    await expect(costMetric).toHaveTextContent("$1240.50");

    const ocrMetric = canvasElement.querySelector("#metric-ocr-quota") as HTMLElement;
    await expect(ocrMetric).toHaveTextContent("2,450 pages");

    // --- 2. SWITCH TO CHARTS & FORECAST TAB ---
    const chartsTabTrigger = canvasElement.querySelector("#tab-charts") as HTMLButtonElement;
    await expect(chartsTabTrigger).toBeVisible();
    await userEvent.click(chartsTabTrigger);

    const forecastHeader = canvas.getByText("Usage Forecast");
    await expect(forecastHeader).toBeVisible();

    // --- 3. SWITCH TO BREAKDOWN TAB ---
    const breakdownTabTrigger = canvasElement.querySelector("#tab-breakdown") as HTMLButtonElement;
    await expect(breakdownTabTrigger).toBeVisible();
    await userEvent.click(breakdownTabTrigger);

    const cardiologyRow = canvas.getByText("Cardiology Unit");
    await expect(cardiologyRow).toBeVisible();

    // --- 4. SWITCH TO QUOTAS & EXECUTE RESET BILLING CYCLE ---
    const quotasTabTrigger = canvasElement.querySelector("#tab-quotas") as HTMLButtonElement;
    await expect(quotasTabTrigger).toBeVisible();
    await userEvent.click(quotasTabTrigger);

    const resetBillingBtn = canvasElement.querySelector("#btn-reset-billing") as HTMLButtonElement;
    await expect(resetBillingBtn).toBeVisible();
    await userEvent.click(resetBillingBtn);

    // Confirm stats reset to zeroed values
    const resetCostMetric = await canvas.findByText("$0.00");
    await expect(resetCostMetric).toBeVisible();

    const resetOcrMetric = canvas.getByText("10,000 pages");
    await expect(resetOcrMetric).toBeVisible();
  },
};
