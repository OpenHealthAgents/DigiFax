import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "storybook/test";
import OCRAdministrationPage from "../app/admin/ocr/page";
import "../app/globals.css";

const meta: Meta<typeof OCRAdministrationPage> = {
  title: "DigiFax/Administration/OCRAdministration",
  component: OCRAdministrationPage,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof OCRAdministrationPage>;

export const DefaultOCRConsoleView: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // --- 1. VERIFY STATS HIGHLIGHTS ---
    const activeHeader = canvas.getByText("96.8% Avg");
    await expect(activeHeader).toBeVisible();

    const processingAvg = canvas.getByText("240ms / doc");
    await expect(processingAvg).toBeVisible();

    // --- 2. RUN COMPARISON SANDBOX INGESTION ---
    const compareBtn = canvasElement.querySelector("#compare-btn") as HTMLButtonElement;
    await expect(compareBtn).toBeVisible();
    await userEvent.click(compareBtn);

    // Wait for mock index processing delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // --- 3. VERIFY COMPARATIVE RESULTS TAB BARS ---
    const tesseractTab = canvasElement.querySelector("#tab-btn-tesseract") as HTMLButtonElement;
    const paddleTab = canvasElement.querySelector("#tab-btn-paddleocr") as HTMLButtonElement;
    const suryaTab = canvasElement.querySelector("#tab-btn-suryaocr") as HTMLButtonElement;

    await expect(tesseractTab).toBeVisible();
    await expect(paddleTab).toBeVisible();
    await expect(suryaTab).toBeVisible();

    // --- 4. SWITCH TABS & VERIFY RENDERED VALUES ---
    // Select Tesseract default view
    const outputContainer = canvasElement.querySelector("#extracted-text-output");
    await expect(outputContainer).toBeVisible();
    await expect(outputContainer).toHaveTextContent("PATIENT: JOHN DOE");

    // Click PaddleOCR Tab
    await userEvent.click(paddleTab);
    await expect(canvas.getByText("410ms")).toBeVisible(); // PaddleOCR latency check

    // Click Surya OCR Tab
    await userEvent.click(suryaTab);
    await expect(canvas.getByText("920ms")).toBeVisible(); // Surya OCR latency check
    await expect(outputContainer).toHaveTextContent("sugar index remains elevated");
  },
};
