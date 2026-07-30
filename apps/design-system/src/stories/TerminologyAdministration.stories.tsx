import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import TerminologyAdministrationPage from "../app/admin/terminology/page";
import "../app/globals.css";

const meta: Meta<typeof TerminologyAdministrationPage> = {
  title: "DigiFax/Administration/TerminologyAdministration",
  component: TerminologyAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof TerminologyAdministrationPage>;

export const DefaultTerminologyConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY STATS HIGHLIGHTS ---
    const mappedHeader = canvas.getByText("1,248 Rules");
    await expect(mappedHeader).toBeVisible();

    const activeVersion = canvas.getAllByText(/v4/i)[0];
    await expect(activeVersion).toBeVisible();

    // --- 2. EXECUTE SEARCH QUERY ---
    const searchBar = canvasElement.querySelector("#search-input") as HTMLInputElement;
    await expect(searchBar).toBeVisible();
    await userEvent.type(searchBar, "Digoxin");
    await expect(searchBar).toHaveValue("Digoxin");

    // Clear search
    await userEvent.clear(searchBar);
    await userEvent.type(searchBar, " ");
    await userEvent.clear(searchBar);

    // --- 3. APPROVE INDIVIDUAL MAPPING RULE ---
    const approveDigoxinBtn = canvasElement.querySelector("#approve-serum-digoxin-level") as HTMLButtonElement;
    await expect(approveDigoxinBtn).toBeVisible();
    await userEvent.click(approveDigoxinBtn);

    // Assert success banner appears
    const successAlert = canvas.getByText("Mapping rule approved. Concepts resolved successfully.");
    await expect(successAlert).toBeVisible();

    // --- 4. BULK APPROVE WORKFLOWS ---
    // Wait for alert banner to unmount or just find checkboxes
    const checkboxes = canvasElement.querySelectorAll('input[type="checkbox"]');
    // Select TSH Level checkbox (which is index 4 in mappings, first select is row index)
    const tshCheckbox = checkboxes[4] as HTMLInputElement;
    await userEvent.click(tshCheckbox);

    const bulkBtn = canvasElement.querySelector("#bulk-approve-btn") as HTMLButtonElement;
    await expect(bulkBtn).toBeVisible();
    await userEvent.click(bulkBtn);

    const bulkSuccess = canvas.getByText("Successfully approved 1 mappings in bulk.");
    await expect(bulkSuccess).toBeVisible();
  },
};
