# Research: KWI-UI Interface Polish

**Date**: 2026-03-22
**Feature**: 004-kwi-ui-polish

## R1: Multi-Select Filter Dropdown Pattern

### Decision: Custom Svelte Component

Build a reusable `MultiSelectFilter.svelte` component rather than
using a third-party library.

### Rationale

- The project has zero UI component library dependencies; adding one
  for a single component would violate Principle VII (Simplicity).
- The required behavior (checkboxes in a dropdown with Select All /
  Clear All) is straightforward to implement with native HTML elements.
- Full control over ARIA attributes (`role="listbox"`,
  `aria-multiselectable`, `aria-expanded`) is easier with a custom
  component than adapting a library.

### Alternatives Considered

- **svelte-multiselect**: Adds a runtime dependency for a single use
  case. Rejected for unnecessary complexity.
- **Native `<select multiple>`**: Poor UX—requires Ctrl+click for
  multi-select, no checkboxes, no Select All/Clear All. Rejected.
- **Headless UI library (e.g., Melt UI)**: Good accessibility defaults
  but adds a dependency and learning curve. Overkill for this use case.

### Implementation Notes

- Component accepts: `label: string`, `options: string[]`,
  `selected: Set<string>`, `onchange: (selected: Set<string>) => void`
- Dropdown opens on button click, closes on outside click or Escape
- Select All / Clear All as inline text buttons at top of dropdown
- Button text shows summary: "All types" when all selected, "bug, task"
  when few selected, "3 of 9 types" when many selected

---

## R2: Client-Side vs Server-Side Multi-Select Filtering

### Decision: Client-Side Filtering

Fetch all items for the selected project (with `showArchived=true`)
and filter entirely on the client.

### Rationale

- The current backend `listWorkItems` API accepts single optional
  filter values for `wiType`, `wiStatus`, and `areaId`. Supporting
  multi-select would require backend API changes (array parameters,
  SQL `IN` clauses) in both Rust commands and Python CLI.
- kwi is a single-user desktop app with low item counts per project
  (typically tens to low hundreds). Client-side filtering adds
  negligible overhead.
- T-shirt size filtering is already client-side, establishing the
  pattern.
- Avoids changes to the Rust backend, Python CLI, and MCP server,
  keeping the sprint scoped to UI-only changes.

### Alternatives Considered

- **Multiple backend calls (one per selected value), merge results**:
  Complex, race-condition-prone, and unnecessary for the expected data
  volume. Rejected.
- **Backend API change to accept arrays**: Correct long-term solution
  but broadens sprint scope to Rust + Python + MCP changes. Rejected
  for this sprint; could be a future optimization.

### Implementation Notes

- Call `listWorkItems(projectId)` with no filter arguments and
  `showArchived=true` to get all items
- Apply all filtering (type, status, size, area) client-side using
  `$derived` reactive expressions
- When any filter set is empty (all unchecked), show no items for that
  dimension (intersection semantics)

---

## R3: Window Size Persistence

### Decision: `tauri-plugin-window-state`

Use the official Tauri 2 window state plugin for automatic
save/restore of window dimensions and position.

### Rationale

- Official Tauri plugin with Tauri 2 support—well-maintained and
  handles edge cases (off-screen detection, multi-monitor).
- Saves window state (size, position, maximized/minimized) on close
  and restores on launch with no custom code.
- One-time setup: add Cargo dependency, register plugin in `lib.rs`,
  add permission to capabilities.

### Alternatives Considered

- **localStorage + `appWindow.setSize()`**: Would work but requires
  manual handling of `beforeunload` events, serialization, off-screen
  validation, and minimum size enforcement. More code to write and
  maintain. Rejected.
- **Config file approach (write to ~/.config/kwi/)**: Overcomplicates
  a simple preference. Rejected.

### Implementation Notes

- Add `tauri-plugin-window-state = "2"` to `Cargo.toml`
- Register `.plugin(tauri_plugin_window_state::Builder::new().build())`
  in `lib.rs`
- Add `"window-state:default"` to capabilities `default.json`
- Set minimum window size in `tauri.conf.json`:
  `"minWidth": 640, "minHeight": 480`
- The plugin handles all save/restore automatically; no frontend
  code needed

---

## R4: Form Field Reordering Approach

### Decision: Template-Only Change

Reorder the Svelte template blocks in `WorkItemForm.svelte`. No logic
changes required.

### Rationale

- The form fields are independent—Content does not depend on
  Type/Status/Size being set first, and vice versa.
- The existing validation logic validates all fields regardless of
  DOM order.
- Moving the Content textarea block below the metadata row blocks is
  sufficient.

### Implementation Notes

- Current order: Title → Content → Type/Status/Size → Area/Sprint/Parent → Details
- New order: Title → Type/Status/Size → Area/Sprint/Parent → Content → Details
- Move the Content `<div class="form-group">` block to just before the
  Details `<div class="form-group">` block

---

## R5: Create Form Default Values

### Decision: Explicit Named Defaults with Fallback

Use explicit string matching to find "issue", "open", "S" in the
reference data arrays, falling back to `[0]` if the preferred value
is missing.

### Rationale

- Hardcoded fallback values like `types[0]` depend on alphabetical
  database ordering, which is fragile and currently results in poor
  defaults ("bug", "active", "XS").
- Using `.find()` with fallback is explicit, self-documenting, and
  resilient to ref-data changes.

### Implementation Notes

```typescript
if (!isEdit) {
  wiType = types.find(t => t === "issue") ?? types[0] ?? "";
  wiStatus = statuses.find(s => s === "open") ?? statuses[0] ?? "";
  wiTshirt = tshirtSizes.find(s => s === "S") ?? tshirtSizes[0] ?? "";
}
```

---

## R6: Collapsible Project Details

### Decision: Native HTML `<details>` Element

Use the native `<details>`/`<summary>` HTML elements for the
collapsible project details pane.

### Rationale

- Zero JavaScript required for expand/collapse behavior.
- Built-in accessibility: keyboard navigable, screen reader
  compatible, proper ARIA semantics by default.
- The `<details>` element defaults to closed (collapsed), matching
  FR-018.
- Styled with CSS to match the application theme.

### Alternatives Considered

- **Custom expand/collapse with state variable**: More code, requires
  manual ARIA attributes and keyboard handling. Rejected per
  Principle VII (Simplicity).

### Implementation Notes

- New `ProjectDetails.svelte` component accepting a `Project` prop
- Renders short name, CN path, and conditionally renders GitHub repo
  and description
- Inserted in `+page.svelte` between SearchBar and the view area

---

## R7: Refresh Button Design

### Decision: Unicode Icon Button with Loading State

Use a simple button with ↻ (U+21BB) character as the refresh icon,
with a CSS spin animation during loading.

### Rationale

- No icon library dependency needed.
- Consistent with the existing minimal UI style (the app uses + and ◆
  characters for other icon buttons).
- Loading state communicated via CSS animation (spin) and
  `aria-busy="true"`.

### Alternatives Considered

- **SVG icon**: Better visual quality but adds asset management
  overhead for a single icon. Can upgrade later if an icon system
  is adopted.

### Implementation Notes

- `ProjectSelector.svelte`: Add ↻ button next to "Projects" heading,
  calls existing `loadProjects()` function
- `WorkItemList.svelte`: Add ↻ button next to "New Work Item" button,
  calls existing `loadItems()` function
- Both buttons: `disabled` + spinning animation during fetch,
  `aria-label="Refresh"`, `aria-busy` during load

---

## R8: Test Strategy

### Decision: Component Tests with vitest + @testing-library/svelte

### Rationale

- vitest and @testing-library/svelte are already installed as dev
  dependencies.
- No vitest config or test files exist yet — this sprint establishes
  the pattern.
- Component-level tests validate rendering, user interaction, and
  reactive behavior without requiring the Tauri runtime.

### Implementation Notes

- Create `vitest.config.ts` with jsdom environment
- Test files alongside components: `*.test.ts` in `src/lib/components/`
- Key tests:
  - `MultiSelectFilter.test.ts`: render, toggle, select all, clear all, close on outside click
  - `WorkItemForm.test.ts`: field order, create defaults, edit saves button visibility
  - `ProjectDetails.test.ts`: render with/without optional fields, collapse/expand
- Mock Tauri `invoke` calls using vitest mocks
