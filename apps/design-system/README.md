# DigiFax Design System & Frontend Shell

Next.js frontend application presenting user workspaces and the unified Tenant Administration console dashboard. Equipped with Storybook components workbench and Playwright E2E Story tests.

## Structure
* **`src/app/`**: Next.js App Router endpoints (e.g. `/admin`, `/review`, `/documents`).
* **`src/stories/`**: Storybook stories configuration and Vitest-browser E2E interaction playbooks (e.g. `TenantAdministration.stories.tsx`).

## Setup
Using standard `pnpm`:
```bash
pnpm install
```

## Running Dev Servers
* **Next.js Web App**: `pnpm dev`
* **Storybook Workbench**: `pnpm storybook`

## Running Tests
* **Vitest Story Tests**: `pnpm vitest run`
  * Executes the browser E2E interaction steps inside Chromium headless instances.
