# DigiFax Design System

The DigiFax Design System is a modern, clean, minimal design system built for enterprise healthcare SaaS platforms. It is optimized for high readability, WCAG AA compliance, dark/light mode responsiveness, and medical workspace reliability.

---

## 🎨 Color Tokens (WCAG AA Compliant)

All color pairings are selected to guarantee a minimum contrast ratio of 4.5:1.

| Token | Light Value | Dark Value | Purpose |
| :--- | :--- | :--- | :--- |
| **`background`** | `#ffffff` | `#0f172a` (Slate 900) | Primary workspace background |
| **`foreground`** | `#0f172a` | `#f8fafc` (Slate 50) | Primary text color |
| **`primary`** | `#0284c7` (Sky 600) | `#38bdf8` (Sky 400) | Primary brand / trust color |
| **`primary-foreground`**| `#ffffff` | `#0f172a` | Text on top of primary color |
| **`muted`** | `#f1f5f9` (Slate 100) | `#1e293b` (Slate 800) | Neutral card/tab background |
| **`muted-foreground`** | `#64748b` (Slate 500) | `#94a3b8` (Slate 400) | Secondary / explanatory text |
| **`success`** | `#16a34a` (Green 600) | `#4ade80` (Green 400) | Normal physiological values / approved status |
| **`warning`** | `#d97706` (Amber 600) | `#fbbf24` (Amber 400) | Borderline values / OCR warnings |
| **`error`** | `#dc2626` (Red 600) | `#f87171` (Red 400) | Out-of-bounds values / critical errors |

---

## 📐 Spacing & Layout (4px Grid)

DigiFax uses a 4px logical grid system to enforce spatial rhythm.

* **`2`** (8px) - Padding inside elements / labels.
* **`4`** (16px) - Standard padding for inputs, buttons, and alert cards.
* **`6`** (24px) - Default layout gutters / dialog content padding.
* **`8`** (32px) - Container margin spacers.

---

## 🔠 Typography Hierarchy

* **Font Family**: `Inter`, Sans-serif.
* **Scale**:
  * **`h1`**: `24px` / `line-height: 32px` / Semibold.
  * **`h2`**: `20px` / `line-height: 28px` / Semibold.
  * **`body`**: `14px` / `line-height: 20px` / Regular.
  * **`caption`**: `12px` / `line-height: 16px` / Medium.

---

## ♿ Accessibility Guidelines (WCAG 2.1 AA)

1. **Color Contrast**: Verify all body text contrast holds a minimum of 4.5:1 against the background.
2. **Keyboard Navigation**: All interactive elements must focus via standard `Tab` key, displaying a high-contrast focus ring (`outline-none ring-2 ring-primary`).
3. **Screen Readers**: Elements must provide descriptive labels (`aria-label`) and state tags (`aria-expanded`, `aria-checked`).

---

## 🧱 Reusable UI Primitives Specs

### 1. Button
* **Variants**: `default` (filled Sky), `outline`, `ghost`, `danger`.
* **State**: Focus states require visible rings. Disabled state must set opacity to `0.5` and set `pointer-events-none`.

### 2. Input
* **States**: Normal border Slate 200/800, Focus ring Sky 600/400.
* **Errors**: Red border with helper text below.

### 3. Alert
* **Types**: `info`, `warning`, `error`, `success`.
* **Layout**: Horizontal icon left, header and text description right.

### 4. Switch
* **Style**: Minimal pill toggle track with sliding thumb.
* **States**: Keyboard focus ring, transitions with ease-in-out.
