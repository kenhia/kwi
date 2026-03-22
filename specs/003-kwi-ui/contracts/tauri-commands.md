# Tauri IPC Command Contracts

**Date**: 2026-03-21
**Feature**: 003-kwi-ui

All commands are invoked from the Svelte frontend via `invoke()`.
Every command returns `Result<T, String>` where the error string
contains a user-readable message.

---

## Projects

### `list_projects`

- **Parameters**: none
- **Returns**: `Vec<Project>`
- **Errors**: Database connection failure

### `create_project`

- **Parameters**:
  - `project: String` — short name (required)
  - `cn_path: String` — canonical path (required)
  - `gh_repo: Option<String>` — GitHub repo URL
  - `description: Option<String>`
- **Returns**: `Project`
- **Errors**: Duplicate project name; database failure

---

## Areas

### `list_areas`

- **Parameters**:
  - `project_id: i32` (required)
- **Returns**: `Vec<Area>`
- **Errors**: Database failure; project not found

### `create_area`

- **Parameters**:
  - `project_id: i32` (required)
  - `name: String` (required)
  - `description: Option<String>`
- **Returns**: `Area`
- **Errors**: Duplicate area name within project; database failure

---

## Work Items

### `list_work_items`

- **Parameters**:
  - `project_id: Option<i32>` — filter by project
  - `area_id: Option<i32>` — filter by area
  - `wi_type: Option<String>` — filter by type
  - `wi_status: Option<String>` — filter by status
  - `show_archived: Option<bool>` — include archived items (default: false)
- **Returns**: `Vec<WorkItem>`
- **Errors**: Database failure

### `get_work_item`

- **Parameters**:
  - `id: i32` (required)
- **Returns**: `WorkItem`
- **Errors**: Not found; database failure

### `create_work_item`

- **Parameters**:
  - `project_id: i32` (required)
  - `title: String` (required)
  - `content: String` (required)
  - `wi_type: String` (required)
  - `wi_status: Option<String>` — defaults to `"open"`
  - `wi_tshirt: Option<String>` — defaults to `"M"`
  - `area_id: Option<i32>`
  - `sprint: Option<String>`
  - `details: Option<String>`
  - `parent_id: Option<i32>`
- **Returns**: `WorkItem`
- **Errors**: Invalid type/status; project not found; database failure

### `update_work_item`

- **Parameters**:
  - `id: i32` (required)
  - `title: Option<String>`
  - `content: Option<String>`
  - `wi_type: Option<String>`
  - `wi_status: Option<String>`
  - `wi_tshirt: Option<String>`
  - `area_id: Option<i32>`
  - `sprint: Option<String>`
  - `details: Option<String>`
  - `parent_id: Option<i32>`
- **Returns**: `WorkItem`
- **Errors**: Not found; invalid type/status; database failure

### `archive_work_item`

- **Parameters**:
  - `id: i32` (required)
- **Returns**: `WorkItem` (with status set to `"archived"`)
- **Errors**: Not found; database failure

### `search_work_items`

- **Parameters**:
  - `query: String` (required) — full-text search term
  - `project_id: Option<i32>` — narrow to project
- **Returns**: `Vec<WorkItem>`
- **Errors**: Database failure

---

## Relationships

### `list_related`

- **Parameters**:
  - `work_item_id: i32` (required)
- **Returns**: `Vec<RelatedItem>`
- **Errors**: Not found; database failure

### `relate_work_items`

- **Parameters**:
  - `left_id: i32` (required)
  - `right_id: i32` (required)
  - `relationship: String` (required)
- **Returns**: `()` (success confirmation)
- **Errors**: Self-relation; item not found; duplicate relation; database failure

### `unrelate_work_items`

- **Parameters**:
  - `left_id: i32` (required)
  - `right_id: i32` (required)
- **Returns**: `()` (success confirmation)
- **Errors**: Relation not found; database failure

---

## Reference Data

### `get_valid_types`

- **Parameters**: none
- **Returns**: `Vec<String>`
- **Errors**: Database failure

### `get_valid_statuses`

- **Parameters**: none
- **Returns**: `Vec<String>`
- **Errors**: Database failure

### `get_valid_tshirt_sizes`

- **Parameters**: none
- **Returns**: `Vec<String>` — hardcoded: `["XS", "S", "M", "L", "XL", "Huge", "Unknown"]`
- **Errors**: none (no database call)
- **Note**: No `workitem_tshirt_size` reference table exists; values are a fixed enum
