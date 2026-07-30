import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import TenantBrandingPage from "../app/admin/branding/page";
import "../app/globals.css";

const meta: Meta<typeof TenantBrandingPage> = {
  title: "DigiFax/Administration/TenantBranding",
  component: TenantBrandingPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof TenantBrandingPage>;

export const DefaultBrandingView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. GENERAL TAB AND DEMOGRAPHICS CHANGES ---
    // Test: verify default company name is loaded, then update it
    const companyInput = canvas.getByLabelText("Company Name");
    await expect(companyInput).toHaveValue("OpenHealth Medical Group");
    
    await userEvent.clear(companyInput);
    await userEvent.type(companyInput, "Mercy Hospital Network");
    await expect(companyInput).toHaveValue("Mercy Hospital Network");

    // Edit support contact details
    const supportEmailInput = canvas.getByLabelText("Support Email");
    await userEvent.clear(supportEmailInput);
    await userEvent.type(supportEmailInput, "support@mercy.org");

    // --- 2. SWITCH STYLING TAB & EDIT COLORS ---
    const styleTabTrigger = canvas.getByRole("tab", { name: "Styles & Logos" });
    await userEvent.click(styleTabTrigger);

    // Verify typography font can be selected
    const fontSelect = canvas.getByLabelText("Typography Font");
    await userEvent.selectOptions(fontSelect, "Outfit");
    await expect(fontSelect).toHaveValue("Outfit");

    // Edit primary styling color hex code
    const colorInput = canvas.getByLabelText("Primary Color");
    await userEvent.clear(colorInput);
    await userEvent.type(colorInput, "#059669"); // Emerald hex color

    // --- 3. TEST DRAFT TEMPLATES TAB ---
    const templatesTabTrigger = canvas.getByRole("tab", { name: "Templates" });
    await userEvent.click(templatesTabTrigger);

    const watermarkInput = canvas.getByLabelText("PDF Document Watermark Text");
    await userEvent.clear(watermarkInput);
    await userEvent.type(watermarkInput, "DRAFT COPY");

    // --- 4. PREVIEWS NAVIGATION & DARK MODE ---
    // Click on PDF tab in preview section
    const pdfPreviewTrigger = canvas.getByRole("tab", { name: "PDF Report" });
    await userEvent.click(pdfPreviewTrigger);

    // Verify PDF watermark overlay displays newly typed text
    const watermarkText = canvas.getByText("DRAFT COPY");
    await expect(watermarkText).toBeVisible();

    // Toggle dark mode switch
    const darkSwitch = canvas.getByLabelText("Dark Preview");
    await userEvent.click(darkSwitch);

    // --- 5. SAVE AND ROLLBACK HISTORY ---
    // Click save
    const saveBtn = canvas.getByRole("button", { name: "Save Configuration" });
    await userEvent.click(saveBtn);

    // Assert that version 2 is now added to the version logs
    const v2Cell = canvas.getByText("2");
    await expect(v2Cell).toBeVisible();

    // Revert styling using the Version 1 rollback button
    const rollbackBtn = canvasElement.querySelector("#rollback-btn-v1") as HTMLButtonElement;
    await userEvent.click(rollbackBtn);

    // Wait for async React state transitions to commit to DOM
    await new Promise((resolve) => setTimeout(resolve, 200));

    // Check company name reverted back to original (retrieve fresh input reference after remounting)
    const generalTabTrigger = canvas.getByRole("tab", { name: "General" });
    await userEvent.click(generalTabTrigger);

    const freshCompanyInput = canvas.getByLabelText("Company Name");
    await expect(freshCompanyInput).toHaveValue("OpenHealth Hospital Corp");
  },
};
