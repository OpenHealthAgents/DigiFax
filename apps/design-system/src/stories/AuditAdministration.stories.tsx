import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import AuditAdministrationPage from "../app/admin/audit/page";
import "../app/globals.css";

const meta: Meta<typeof AuditAdministrationPage> = {
  title: "DigiFax/Administration/AuditAdministration",
  component: AuditAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof AuditAdministrationPage>;

export const DefaultAuditConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY INITIAL LOG ENTRIES ---
    const kalyanRows = await canvas.findAllByText("usr-kalyan", { exact: false });
    await expect(kalyanRows[0]).toBeVisible();

    const vaultRow = await canvas.findByText("VAULT", { exact: false });
    await expect(vaultRow).toBeVisible();

    // --- 2. FILTER BY INITIATOR ACTOR ---
    const inputActorSearch = canvasElement.querySelector("#input-actor-search") as HTMLInputElement;
    await expect(inputActorSearch).toBeVisible();
    await userEvent.type(inputActorSearch, "usr-admin");

    // Kalyan row should be filtered out
    await expect(canvas.queryByText("usr-kalyan", { exact: false })).toBeNull();
    const adminRow = canvas.getByText("usr-admin", { exact: false });
    await expect(adminRow).toBeVisible();

    // Clear filter
    await userEvent.clear(inputActorSearch);
    const restoredRows = await canvas.findAllByText("usr-kalyan", { exact: false });
    await expect(restoredRows[0]).toBeVisible();

    // --- 3. RUN CRYPTOGRAPHIC TAMPER VALIDATION CHECK ---
    const btnVerifyIntegrity = canvasElement.querySelector("#btn-verify-integrity") as HTMLButtonElement;
    await expect(btnVerifyIntegrity).toBeVisible();
    await userEvent.click(btnVerifyIntegrity);

    // Verify alert message pops up
    const successAlert = await canvas.findByText("Audit Sequence Verified");
    await expect(successAlert).toBeVisible();
  },
};
