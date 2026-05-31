# Contracts: Tauri Commands & GUI (005-backlog-cleanup)

Surface: `kwi-ui/src-tauri/src/commands.rs` (Rust) and the Svelte frontend
(`kwi-ui/src/lib/commands.ts`, components). Only additions/changes are listed.

## CHANGED: `archive_work_item`

```rust
#[tauri::command]
pub async fn archive_work_item(state, id: i32) -> Result<(), String>
```

- **Behavior**: Sets `archived = true`, preserves status (previously status →
  `archived`). Idempotent.
- **Maps to**: FR-002, FR-005.

## NEW: `unarchive_work_item`

```rust
#[tauri::command]
pub async fn unarchive_work_item(state, id: i32) -> Result<(), String>
```

- **Behavior**: Sets `archived = false`, status unchanged. Idempotent.
- **Frontend**: `unarchiveWorkItem(id)` in `commands.ts` → `invoke("unarchive_work_item", { id })`.
- **Maps to**: FR-007.

## CHANGED: `list_work_items`

```rust
#[tauri::command]
pub async fn list_work_items(
    state, project_id, area_id: Option<i32>,
    status_filter, show_archived: Option<bool>, /* existing */
) -> Result<Vec<WorkItem>, String>
```

- **Behavior**: Returned `WorkItem`s MUST include the `archived` boolean. Status
  filtering operates on real statuses (the `archived` pseudo-status no longer
  exists). Visibility of archived items is controlled by `show_archived`,
  independent of status. Sprint filtering is applied client-side from the
  returned set (dynamic distinct list + "Unassigned").
- **Maps to**: FR-008, FR-012.

## GUI behavior contracts (Svelte)

| Behavior | Component | Requirement |
|----------|-----------|-------------|
| Remove archive confirmation dialog | `routes/+page.svelte` (delete `confirm(...)`) | FR-006 |
| Un-archive action on archived item | `components/WorkItemDetail.svelte` | FR-007 |
| Default status filter excludes `closed` | `components/WorkItemList.svelte` | FR-008 |
| Filters sticky within session | `lib/stores.svelte.ts` (lift filter state into runes store) | FR-009 |
| No cross-session persistence | (explicitly NOT using `localStorage`) | FR-010 |
| Visual cue when a filter is off-default | `components/WorkItemList.svelte` | FR-011 |
| Sprint filter (distinct + "Unassigned") | `components/WorkItemList.svelte` via reused `MultiSelectFilter` | FR-012 |

## Model contract

`WorkItem` in `kwi-ui/src-tauri/src/models.rs` and
`kwi-ui/src/lib/types.ts` MUST gain an `archived: bool` / `archived: boolean`
field. The `class:archived` styling MUST key off this flag (not
`wi_status === "archived"`).

## Application icon

- **Action**: Run `tauri icon /gratch/kIcons/kwi-kiwi-mascot-cropped.png` to
  regenerate `kwi-ui/src-tauri/icons/*` (the set referenced by
  `tauri.conf.json`: `32x32.png`, `128x128.png`, `128x128@2x.png`, `icon.icns`,
  `icon.ico`, plus Windows/Android variants).
- **Result**: Built app shows the kiwi mascot icon.
- **Maps to**: FR-019.
