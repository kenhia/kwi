# Data Model: KWI-UI Interface Polish

**Date**: 2026-03-22
**Feature**: 004-kwi-ui-polish

## Overview

This sprint introduces no database schema changes. All improvements
operate on existing entities and frontend-only state. This document
describes the new frontend data structures and state changes.

## Existing Entities (Unchanged)

### Project

| Field       | Type     | Notes              |
|-------------|----------|--------------------|
| id          | number   | Primary key        |
| project     | string   | Short name         |
| cn_path     | string   | CN path            |
| gh_repo     | string?  | GitHub repo (opt)  |
| description | string?  | Description (opt)  |
| created     | string   | ISO timestamp      |
| updated     | string   | ISO timestamp      |

### WorkItem

| Field        | Type     | Notes              |
|--------------|----------|--------------------|
| id           | number   | Primary key        |
| project_id   | number   | FK → Project       |
| project_name | string?  | Denormalized       |
| area_id      | number?  | FK → Area          |
| area_name    | string?  | Denormalized       |
| wi_type      | string   | Type reference     |
| wi_status    | string   | Status reference   |
| wi_tshirt    | string   | T-shirt size       |
| sprint       | string?  | Sprint label       |
| title        | string   | Title              |
| content      | string   | Markdown body      |
| details      | string?  | Markdown details   |
| parent_id    | number?  | FK → WorkItem      |
| created      | string   | ISO timestamp      |
| updated      | string   | ISO timestamp      |

### Area

| Field       | Type     | Notes              |
|-------------|----------|--------------------|
| id          | number   | Primary key        |
| project_id  | number   | FK → Project       |
| name        | string   | Area name          |
| description | string?  | Description (opt)  |

## New Frontend State

### MultiSelectFilter Component State

Each `MultiSelectFilter` instance manages:

| Field    | Type          | Description                                      |
|----------|---------------|--------------------------------------------------|
| options  | string[]      | All available values (from ref data or areas)     |
| selected | Set\<string\> | Currently selected values                        |
| open     | boolean       | Whether the dropdown panel is visible             |
| label    | string        | Display label (e.g., "Type", "Status", "Size")   |

### Filter State in WorkItemList

Current state (single-select):
- `filterArea: number | undefined`
- `filterType: string | undefined`
- `filterStatus: string | undefined`
- `filterTshirt: string | undefined`
- `showArchived: boolean`

New state (multi-select):
- `selectedAreas: Set<string>` — all area names selected by default (initialized reactively after areas load)
- `selectedTypes: Set<string>` — all types selected by default
- `selectedStatuses: Set<string>` — all statuses except "archived" selected by default
- `selectedSizes: Set<string>` — all sizes selected by default
- `showArchived` removed — handled through `selectedStatuses`

### Derived Filtered Items

```
allItems = await listWorkItems(projectId)  // no filters, fetch all
filteredItems = allItems
  .filter(item => selectedTypes.has(item.wi_type))
  .filter(item => selectedStatuses.has(item.wi_status))
  .filter(item => selectedSizes.has(item.wi_tshirt))
  .filter(item => selectedAreas.size === 0 || selectedAreas.has(item.area_name))
```

### Window State (Managed by Plugin)

Persisted by `tauri-plugin-window-state` — no custom data model needed.
The plugin stores window position, size, and maximized state in its own
storage (typically `~/.local/share/com.ken.kwi-ui/`).

## Reference Data

### Work Item Types (alphabetical from database)

bug, epic, feature, idea, issue, research, story, task, tweak

### Work Item Statuses (alphabetical from database)

active, archived, closed, draft, open, resolved

### T-Shirt Sizes (hardcoded order)

XS, S, M, L, XL, Huge, Unknown
