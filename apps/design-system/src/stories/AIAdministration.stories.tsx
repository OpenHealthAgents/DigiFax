import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import AIAdministrationPage from "../app/admin/ai/page";
import "../app/globals.css";

const meta: Meta<typeof AIAdministrationPage> = {
  title: "DigiFax/Administration/AIAdministration",
  component: AIAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof AIAdministrationPage>;

export const DefaultAIConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY STATS HIGHLIGHTS ---
    const activeHeader = canvas.getByText("4 / 5 ONLINE");
    await expect(activeHeader).toBeVisible();

    const spendSavings = canvas.getByText("$1,840 Saved");
    await expect(spendSavings).toBeVisible();

    // --- 2. EXECUTE CONNECTION HANDSHAKE CHECK ---
    // Validate OpenAI connection
    const validateOpenAiBtn = canvasElement.querySelector("#test-connection-openai") as HTMLButtonElement;
    await expect(validateOpenAiBtn).toBeVisible();
    await userEvent.click(validateOpenAiBtn);

    // Wait for mock ping delay to complete
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const verifyAlert = canvas.getByText("Connection to OpenAI verified successfully. Endpoint responding.");
    await expect(verifyAlert).toBeVisible();

    // --- 3. TEST SANDBOX PROMPT INGESTION & MODEL SELECTION ---
    const modelSelect = canvas.getByLabelText("Target Test Model");
    await userEvent.selectOptions(modelSelect, "OpenAI (gpt-4o)");
    await expect(modelSelect).toHaveValue("OpenAI (gpt-4o)");

    const systemInput = canvas.getByLabelText("System Instruction");
    await userEvent.clear(systemInput);
    await userEvent.type(systemInput, "Secure Medical Records Agent");
    await expect(systemInput).toHaveValue("Secure Medical Records Agent");

    const promptTextarea = canvas.getByLabelText("Test Prompt Input");
    await userEvent.clear(promptTextarea);
    await userEvent.type(promptTextarea, "Extract lab HbA1c values.");

    // --- 4. EXECUTE SANDBOX COMPLETION RUN ---
    const runBtn = canvasElement.querySelector("#run-sandbox-btn") as HTMLButtonElement;
    await userEvent.click(runBtn);

    // Wait for mock word-by-word streaming interval loops (around 20 words * 80ms = 1600ms + buffer)
    await new Promise((resolve) => setTimeout(resolve, 2500));

    const sandboxOutput = canvasElement.querySelector("#sandbox-output-text");
    await expect(sandboxOutput).toBeVisible();
    await expect(sandboxOutput).toHaveTextContent("Extracted Clinical Metric");
    await expect(sandboxOutput).toHaveTextContent("HbA1c");
  },
};
