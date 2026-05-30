# Implementation Plan: KWI-UI Interface Polish

**Branch**: `004-kwi-ui-polish` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-kwi-ui-polish/spec.md`

## Summary

Polish the existing kwi-ui Tauri/Svelte desktop application with seven
UI improvements: multi-select filter dropdowns with checkbox semantics,
form field reordering (Content moved below metadata), sensible create
form defaults (issue/open/S), a top-positioned Save button on the edit
form, a collapsible project details pane, refresh buttons for projects
and work items, and window size persistence across sessions via Tauri's
window state plugin.

## Technical Context

**Language/Version**: Rust 1.75+ (Tauri backend), TypeScript/Svelte 5 (frontend)  
**Primary Dependencies**: Tauri 2.x, tokio-postgres, deadpool-postgres, serde, marked.js, @tauri-apps/api 2.x  
**Storage**: PostgreSQL (existing `workitems` database); tauri-plugin-window-state for window persistence  
**Testing**: cargo test (Rust), vitest + @testing-library/svelte (frontend), svelte-check (types)  
**Target Platform**: Linux (x86_64) primary; Windows (x86_64) secondary  
**Project Type**: desktop-app (Tauri 2 + SvelteKit SPA)  
**Performance Goals**: Filter changes reflect in list within 200ms; no perceptible lag on checkbox toggle  
**Constraints**: Must not break existing CRUD/search/relationship workflows; backward-compatible with current database schema  
**Scale/Scope**: Single-user desktop app; changes limited to 6 Svelte components + Tauri window config  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| 1 | Spec-Driven Development | PASS | spec.md created and validated; all changes traced to FRs |
| 2 | Architecture First | PASS | No architectural changes—all work is within existing Tauri/Svelte structure |
| 3 | Test-Driven Development | PASS | vitest + @testing-library/svelte for component tests; cargo test unchanged |
| 4 | Code Standards Gate | PASS | prettier/eslint/svelte-check (Svelte); cargo fmt/clippy (Rust) |
| 5 | User Documentation Day One | PASS | quickstart.md updated for new UI behaviors |
| 6 | Quality & Accessibility | PASS | Checkbox dropdowns use proper ARIA; keyboard navigation preserved |
| 7 | Simplicity & Intentional Design | PASS | No new abstractions; changes are direct component edits |

## Project Structure

### Documentation (this feature)

```text
specs/004-kwi-ui-polish/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── tauri-commands.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files modified)

```text
kwi-ui/
├── src/
│   ├── lib/
│   │   ├── commands.ts             # No changes expected
│   │   ├── stores.svelte.ts        # No changes expected
│   │   └── types.ts                # No changes expected
│   │   └── components/
│   │       ├── MultiSelectFilter.svelte   # NEW — reusable multi-select checkbox dropdown
│   │       ├── ProjectDetails.svelte      # NEW — collapsible project details pane
│   │       ├── ProjectSelector.svelte     # MODIFIED — add refresh button
│   │       ├── WorkItemList.svelte        # MODIFIED — replace <select> with MultiSelectFilter, add refresh button, remove "Include archived"
│   │       └── WorkItemForm.svelte        # MODIFIED — reorder fields, change defaults, add top save button
│   └── routes/
│       └── +page.svelte                   # MODIFIED — insert ProjectDetails between search bar and content area
└── src-tauri/
    ├── tauri.conf.json                    # MODIFIED — add minimum window size
    └── src/
        └── lib.rs                         # MODIFIED — add window state persistence (if using Tauri plugin)
```

## Design Decisions

### D1: Multi-Select Filter Component

Create a reusable `MultiSelectFilter.svelte` component that replaces
all four single-select `<select>` dropdowns. This component:

- Renders as a button that shows the current selection summary (e.g., "3 of 9 types")
- Opens a dropdown panel with checkboxes on click
- Includes "Select All" and "Clear All" actions at the top of the dropdown
- Closes on outside click or Escape key
- Accepts props: `label`, `options[]`, `selected: Set<string>`, `onchange`
- Uses ARIA attributes: `role="listbox"`, `aria-multiselectable="true"`,
  individual `role="option"` with `aria-selected`

The Area filter will also be converted to multi-select for consistency.
Since the backend `listWorkItems` command accepts single optional filter
values, multi-select filtering will be handled client-side for all
dimensions (type, status, size, area). The backend call will omit
filter parameters, fetching all items for the project, and the component
will filter locally. This trades a slightly larger initial fetch for
full multi-select flexibility without backend changes.

Alternatively, for large item counts, we can make multiple backend calls
(one per selected value) and merge results. Starting with client-side
filtering and optimizing if needed.

### D2: Filter Defaults

Status filter defaults to all values selected except "archived". All
other filters default to all values selected. This replaces the current
"Include archived" checkbox—archived items are now controlled through
the Status filter's "archived" checkbox being unchecked by default.

### D3: Form Field Reordering

Move the Content textarea below the Type/Status/Size and
Area/Sprint/Parent ID rows. The new order:

1. Title (required text input)
2. Type / Status / Size (dropdown row)
3. Area / Sprint / Parent ID (dropdown row)
4. Content (required textarea)
5. Details (optional textarea)

This is a template-only change with no logic impact.

### D4: Create Form Defaults

Replace `types[0]` / `statuses[0]` / `tshirtSizes[0]` with explicit
lookups for "issue", "open", "S" respectively, falling back to `[0]`
if the preferred value isn't in the list.

### D5: Top Save Button (Edit Mode)

Add a "Save Changes" button in the header bar next to the existing
Cancel button, visible only in edit mode (`isEdit === true`). Both
buttons share the same `saving` state and call `handleSubmit()`.

### D6: Project Details Pane

New `ProjectDetails.svelte` component inserted in `+page.svelte`
between the SearchBar and the view content area. Uses an HTML
`<details>` element for native collapse/expand behavior (accessible,
zero-JS). Displays project fields conditionally—omits GitHub repo
and description if null/undefined.

### D7: Refresh Buttons

Add a refresh icon button (↻ or SVG icon) to:
- `ProjectSelector.svelte` header, next to the "Projects" heading
- `WorkItemList.svelte` header, next to the "New Work Item" button

Both call their respective data-loading functions. A brief loading
indicator (spinner or disabled state) shows during the fetch.

### D8: Window Size Persistence

Use the `tauri-plugin-window-state` Tauri 2 plugin to persist and
restore window size/position automatically. This plugin:

- Saves window state (size, position, maximized) on close
- Restores on next launch
- Handles multi-monitor edge cases
- Requires adding the plugin to `Cargo.toml` and registering in `lib.rs`

If the plugin approach is too heavy, a lighter alternative is saving
dimensions to `localStorage` on the `beforeunload` event and reading
them on app startup via `appWindow.setSize()`. Research will determine
the best approach.

Minimum window size will be set in `tauri.conf.json` to prevent
unusable layouts.

### D9: Project Justfile

Add a `justfile` at `kwi-ui/justfile` to consolidate common development
commands into short, memorable recipes. Key recipes:

- `dev` — start Tauri dev server
- `build` — build Svelte frontend
- `test` — run vitest component tests
- `check` — run svelte-check type checking
- `fmt` — format with prettier (Svelte plugin)
- `lint` — run eslint
- `clippy` — run cargo clippy on the Tauri backend
- `rustfmt` — run cargo fmt on the Tauri backend
- `winrelease` — cross-compile a Windows .exe release using
  `x86_64-pc-windows-gnu` target (already configured in
  `.cargo/config.toml` with mingw linker)
- `precommit` — run all checks in sequence (fmt, lint, check, test,
  rustfmt, clippy)

The justfile lives in `kwi-ui/` so all recipes run relative to the
frontend/Tauri project root.

## Implementation Phases

### Phase 1: Multi-Select Filters + Form Improvements (P1 stories)

**Scope**: FR-001 through FR-012 (Stories 1, 2, 3)

1. Create `MultiSelectFilter.svelte` component with tests
2. Replace all `<select>` filters in `WorkItemList.svelte` with `MultiSelectFilter`
3. Implement default selections (all selected; archived unchecked)
4. Remove "Include archived" checkbox
5. Switch to client-side filtering for all dimensions
6. Reorder form fields in `WorkItemForm.svelte`
7. Set create form defaults to issue/open/S
8. Write component tests for new filter behavior and form defaults

### Phase 2: Edit Form + Project Details + Refresh (P2 stories)

**Scope**: FR-013 through FR-023 (Stories 4, 5, 6)

1. Add top "Save Changes" button to `WorkItemForm.svelte` (edit mode)
2. Create `ProjectDetails.svelte` component
3. Insert project details pane in `+page.svelte`
4. Add refresh button to `ProjectSelector.svelte`
5. Add refresh button to `WorkItemList.svelte`
6. Write tests for save button sync, project details rendering, refresh behavior

### Phase 3: Window Size Persistence (P3 story)

**Scope**: FR-024 through FR-027 (Story 7)

1. Research and add window state plugin or localStorage approach
2. Configure minimum window size in `tauri.conf.json`
3. Test window size save/restore cycle
4. Handle edge cases (off-screen, minimized, invalid saved state)
