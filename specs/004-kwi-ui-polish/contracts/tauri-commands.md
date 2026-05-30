# Tauri Commands Contract: KWI-UI Interface Polish

**Date**: 2026-03-22
**Feature**: 004-kwi-ui-polish

## Overview

This sprint requires **no new Tauri commands**. All existing IPC
commands remain unchanged. The UI improvements are implemented entirely
in frontend Svelte components and Tauri configuration.

## Existing Commands Used (No Changes)

| Command             | Signature                                                           | Used By               |
|---------------------|---------------------------------------------------------------------|-----------------------|
| `list_projects`     | `() → Project[]`                                                    | ProjectSelector       |
| `list_areas`        | `(projectId: number) → Area[]`                                      | WorkItemList          |
| `list_work_items`   | `(projectId?, areaId?, wiType?, wiStatus?, showArchived?) → WorkItem[]` | WorkItemList     |
| `get_valid_types`   | `() → string[]`                                                    | WorkItemList, Form    |
| `get_valid_statuses`| `() → string[]`                                                    | WorkItemList, Form    |
| `get_valid_tshirt_sizes` | `() → string[]`                                               | WorkItemList, Form    |
| `create_work_item`  | `(params) → WorkItem`                                              | WorkItemForm          |
| `update_work_item`  | `(params) → WorkItem`                                              | WorkItemForm          |

## Changes to Command Usage

### `list_work_items` — Changed Call Pattern

**Before**: Called with individual filter parameters matching the
selected dropdown values.
```typescript
listWorkItems(projectId, filterArea, filterType, filterStatus, showArchived)
```

**After**: Called with no filter parameters to fetch all items; filtering
done client-side via `Set` intersections.
```typescript
listWorkItems(projectId, undefined, undefined, undefined, true)
```

This change is in the frontend call site only — the backend command
signature is unchanged.

## Tauri Configuration Changes

### `tauri.conf.json` — Window Settings

Add minimum window dimensions:
```json
"windows": [
  {
    "title": "kwi-ui",
    "width": 800,
    "height": 600,
    "minWidth": 640,
    "minHeight": 480
  }
]
```

### `Cargo.toml` — New Plugin Dependency

```toml
tauri-plugin-window-state = "2"
```

### `capabilities/default.json` — New Permission

```json
"permissions": [
  "core:default",
  "opener:default",
  "window-state:default"
]
```

### `lib.rs` — Plugin Registration

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_opener::init())
    .plugin(tauri_plugin_window_state::Builder::new().build())
    // ... rest unchanged
```

## New Svelte Component Contracts

### `MultiSelectFilter.svelte`

**Props**:
| Prop       | Type                              | Required | Description                    |
|------------|-----------------------------------|----------|--------------------------------|
| label      | string                            | Yes      | Display label (e.g., "Type")   |
| options    | string[]                          | Yes      | Available values               |
| selected   | Set\<string\>                     | Yes      | Currently selected values      |
| onchange   | (selected: Set\<string\>) => void | Yes      | Callback when selection changes|

**Behavior**:
- Renders a button showing selection summary
- Opens checkbox dropdown on click
- "Select All" / "Clear All" text actions at top
- Closes on outside click or Escape
- ARIA: `role="listbox"`, `aria-multiselectable="true"`

### `ProjectDetails.svelte`

**Props**:
| Prop    | Type    | Required | Description        |
|---------|---------|----------|--------------------|
| project | Project | Yes      | Project to display |

**Behavior**:
- Renders `<details>` element, closed by default
- Shows: short name, CN path
- Conditionally shows: GitHub repo, description
- Omits fields that are null/undefined
