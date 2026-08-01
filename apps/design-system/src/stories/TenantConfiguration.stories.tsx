import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import SettingsPage from "../app/settings/page";
import "../app/globals.css";

const meta: Meta<typeof SettingsPage> = {
  title: "MedIngest/Administration/TenantConfiguration",
  component: SettingsPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof SettingsPage>;

export const DefaultConfigurationView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. TEST LOCALE TAB SELECTIONS ---
    const dateFormatSelect = canvas.getByLabelText("Date Layout Format");
    await expect(dateFormatSelect).toHaveValue("YYYY-MM-DD");

    await userEvent.selectOptions(dateFormatSelect, "DD/MM/YYYY");
    await expect(dateFormatSelect).toHaveValue("DD/MM/YYYY");

    const timezoneSelect = canvas.getByLabelText("System Timezone");
    await userEvent.selectOptions(timezoneSelect, "America/Chicago");
    await expect(timezoneSelect).toHaveValue("America/Chicago");

    const currencySelect = canvas.getByLabelText("Currency");
    await userEvent.selectOptions(currencySelect, "EUR");
    await expect(currencySelect).toHaveValue("EUR");

    // --- 2. SWITCH TO CLINICAL FORMATS TAB ---
    const clinicalTabTrigger = canvas.getByRole("tab", { name: "Clinical Formats" });
    await userEvent.click(clinicalTabTrigger);

    const patientIdInput = canvas.getByLabelText("Patient Identifier Regex Layout");
    await expect(patientIdInput).toHaveValue("PAT-\\d{6}");

    await userEvent.clear(patientIdInput);
    await userEvent.type(patientIdInput, "MERCY-PAT-\\d{{4}");
    await expect(patientIdInput).toHaveValue("MERCY-PAT-\\d{4}");

    // --- 3. SWITCH TO RETENTION LIFECYCLE TAB ---
    const lifecycleTabTrigger = canvas.getByRole("tab", { name: "Data Lifecycle" });
    await userEvent.click(lifecycleTabTrigger);

    const retentionInput = canvas.getByLabelText("Default Archive Retention Duration (Days)");
    await expect(retentionInput).toHaveValue(365);

    await userEvent.clear(retentionInput);
    await userEvent.type(retentionInput, "180");
    await expect(retentionInput).toHaveValue(180);

    // --- 4. PREVIEWS UPDATE CHECK ---
    const datePreview = canvasElement.querySelector("#date-preview-text");
    await expect(datePreview).toHaveTextContent("30/07/2026 14:35:10");

    const numberPreview = canvasElement.querySelector("#number-preview-text");
    await expect(numberPreview).toHaveTextContent("EUR 1,234.56");

    const retentionPreview = canvasElement.querySelector("#retention-preview-text");
    await expect(retentionPreview).toHaveTextContent("180 days");

    // --- 5. SAVE SETTINGS AND ASSERT BANNER ---
    const saveBtn = canvas.getByRole("button", { name: "Save System Settings" });
    await userEvent.click(saveBtn);

    // Wait for DOM state transitions
    await new Promise((resolve) => setTimeout(resolve, 200));

    const alertBanner = canvas.getByText("Settings Saved");
    await expect(alertBanner).toBeVisible();

    const versionBadge = canvas.getByText("Config Version: v2");
    await expect(versionBadge).toBeVisible();
  },
};
