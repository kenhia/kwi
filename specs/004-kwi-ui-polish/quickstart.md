# Quickstart: KWI-UI Interface Polish

**Feature**: 004-kwi-ui-polish

## Prerequisites

- Existing kwi-ui development environment set up (see `specs/003-kwi-ui/quickstart.md`)
- Node.js and npm installed
- Rust toolchain installed
- PostgreSQL database running with kwi schema

## Development Setup

```bash
cd kwi-ui

# Install frontend dependencies (if not already done)
npm install

# Install the new Tauri plugin (Rust side)
cd src-tauri
cargo add tauri-plugin-window-state@2
cd ..

# Start dev server
cargo tauri dev
```

## What Changed

### Multi-Select Filters

The work item list filters (Type, Status, Size, Area) now use
multi-select checkbox dropdowns instead of single-select dropdowns.
Click a filter button to open the dropdown, check/uncheck items, and
use "Select All" / "Clear All" for bulk selection.

**Default behavior**: All values are selected except "archived" in the
Status filter. The "Include archived" checkbox has been removed.

### Form Field Order

The create/edit work item forms now show fields in this order:
Title → Type/Status/Size → Area/Sprint/Parent → Content → Details.
Content has moved below the metadata fields.

### Create Defaults

New work items default to Type: "issue", Status: "open", Size: "S".

### Top Save Button

When editing a work item, a "Save Changes" button now appears at the
top of the form next to Cancel, so you don't need to scroll down.

### Project Details

After selecting a project, a collapsible "Project Details" bar appears
below the search box. Click it to see the project's CN path, GitHub
repo, and description.

### Refresh Buttons

Both the Projects sidebar and the Work Items list have refresh buttons
(↻) to manually reload data from the database.

### Window Size

The application remembers your window size between sessions. Minimum
window size is 640×480.

## Testing

```bash
cd kwi-ui

# Run component tests
npx vitest run

# Type checking
npx svelte-check

# Lint and format
npx prettier --check .
npx eslint .
```

## Justfile

A `justfile` in `kwi-ui/` provides shorthand for all common commands:

```bash
cd kwi-ui

just dev          # Start Tauri dev server
just test         # Run vitest component tests
just check        # Run svelte-check
just fmt          # Format with prettier
just lint         # Run eslint
just clippy       # Run cargo clippy on Rust backend
just rustfmt      # Run cargo fmt on Rust backend
just precommit    # Run all checks in sequence
just winrelease   # Cross-compile kwi-ui.exe for Windows
```

## Files Modified

| File | Change |
|------|--------|
| `src/lib/components/MultiSelectFilter.svelte` | New component |
| `src/lib/components/ProjectDetails.svelte` | New component |
| `src/lib/components/WorkItemList.svelte` | Multi-select filters, refresh button |
| `src/lib/components/WorkItemForm.svelte` | Field order, defaults, top save button |
| `src/lib/components/ProjectSelector.svelte` | Refresh button |
| `src/routes/+page.svelte` | Project details pane |
| `src-tauri/Cargo.toml` | Window state plugin |
| `src-tauri/tauri.conf.json` | Min window size |
| `src-tauri/capabilities/default.json` | Window state permission |
| `src-tauri/src/lib.rs` | Plugin registration |
| `justfile` | Development task runner |
