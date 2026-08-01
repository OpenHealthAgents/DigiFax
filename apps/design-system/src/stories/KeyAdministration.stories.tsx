import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import KeyAdministrationPage from "../app/admin/keys/page";
import "../app/globals.css";

const meta: Meta<typeof KeyAdministrationPage> = {
  title: "MedIngest/Administration/KeyAdministration",
  component: KeyAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof KeyAdministrationPage>;

export const DefaultKeyConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY METRICS CARDS ---
    const engineHeader = canvas.getByText("Healthy");
    await expect(engineHeader).toBeVisible();

    const expirationHeader = canvas.getByText("82 Days Left");
    await expect(expirationHeader).toBeVisible();

    // --- 2. TRIGGER MANUAL KEY ROTATION ---
    const rotateKeysBtn = canvasElement.querySelector("#btn-rotate-keys") as HTMLButtonElement;
    await expect(rotateKeysBtn).toBeVisible();
    await userEvent.click(rotateKeysBtn);

    // Confirm rotation success notification alert banner triggers
    const successBanner = await canvas.findByText("Keys Rotated Successfully");
    await expect(successBanner).toBeVisible();

    // --- 3. NAVIGATE TO CRYPTOGRAPHIC PARITY VALIDATOR TAB ---
    const validatorTabTrigger = canvasElement.querySelector("#tab-validator") as HTMLButtonElement;
    await expect(validatorTabTrigger).toBeVisible();
    await userEvent.click(validatorTabTrigger);

    const validatorInput = canvasElement.querySelector("#validator-input") as HTMLInputElement;
    await expect(validatorInput).toBeVisible();

    const runValidationBtn = canvasElement.querySelector("#btn-run-validation") as HTMLButtonElement;
    await expect(runValidationBtn).toBeVisible();
    await userEvent.click(runValidationBtn);

    // Confirm parity verification logs and success diagnostic panel appears
    const parityResult = await canvas.findByText("100% Cryptographic Parity Validated");
    await expect(parityResult).toBeVisible();

    // --- 4. NAVIGATE TO AUDIT TRAILS TAB ---
    const auditTabTrigger = canvasElement.querySelector("#tab-audit") as HTMLButtonElement;
    await expect(auditTabTrigger).toBeVisible();
    await userEvent.click(auditTabTrigger);

    // Verify key access logs table is visible
    const auditHeader = canvas.getByText("Key Access Auditing logs");
    await expect(auditHeader).toBeVisible();
  },
};
