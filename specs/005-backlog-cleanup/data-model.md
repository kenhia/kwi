# Phase 1 Data Model: Backlog Cleanup

**Feature**: 005-backlog-cleanup  
**Date**: 2026-05-30

## Schema changes

### `workitem` (modified)

Add one column, independent of `wi_status_id`:

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `archived` | `boolean` | `NOT NULL DEFAULT false` | NEW. Decoupled from status. |

New index: `idx_workitem_archived ON workitem(archived)`.

All existing columns unchanged. Relevant existing columns for this feature:

| Column | Type | Notes |
|--------|------|-------|
| `wi_status_id` | int FK → `workitem_status(id)` | Status preserved when archiving. |
| `wi_tshirt` | text | `CHECK IN ('XS','S','M','L','XL','Huge','Unknown')`; now settable via CLI/MCP. |
| `area_id` | int FK → `area(id)` ON DELETE SET NULL | Now settable via CLI/MCP. |
| `parent_id` | int FK → `workitem(id)` ON DELETE SET NULL | Now settable via CLI/MCP; cycle-guarded. |
| `sprint` | text (nullable) | Source for the new sprint filter; NULL ⇒ "Unassigned". |

### `workitem_status` (modified seed data)

The `archived` row is **removed** after migration. Resulting selectable
statuses: `open`, `active`, `resolved`, `closed`, `draft` (5 total, down from 6).

## Migration: `migrations/002_archived_flag.sql`

Forward-only, idempotent, ordered:

1. `ALTER TABLE workitem ADD COLUMN IF NOT EXISTS archived boolean NOT NULL DEFAULT false;`
2. Repoint legacy rows:
   `UPDATE workitem SET archived = true, wi_status_id = (SELECT id FROM workitem_status WHERE name='closed') WHERE wi_status_id = (SELECT id FROM workitem_status WHERE name='archived');`
3. `DELETE FROM workitem_status WHERE name = 'archived';`
4. `CREATE INDEX IF NOT EXISTS idx_workitem_archived ON workitem(archived);`

Invariant after migration: zero rows reference an `archived` status; every
previously-archived item is `closed` + `archived=true`.

## Application model changes

### Python `WorkItem` dataclass (`src/kwi/models.py`)

Add `archived: bool = False`.

### Rust `WorkItem` (`kwi-ui/src-tauri/src/models.rs`)

Add `archived: bool` (serde), populated by the list/get queries.

### TypeScript `WorkItem` (`kwi-ui/src/lib/types.ts`)

Add `archived: boolean`.

## State transitions

```text
            archive (flag=true, status unchanged)
 ┌────────────────────────────────────────────────┐
 │                                                  ▼
 (archived=false) ◄───────────────────────── (archived=true)
            unarchive (flag=false, status unchanged)
```

- Archiving an already-archived item: no-op.
- Un-archiving a non-archived item: no-op.
- Status is never modified by archive/un-archive.

## Validation rules (from requirements)

| Rule | Source | Enforced in |
|------|--------|-------------|
| `archived` defaults false for new items | FR-001 | DB default + models |
| Archive preserves status | FR-002 | `archive_workitem` (Python + Rust) |
| Legacy archived rows → closed+archived | FR-003 | migration 002 |
| `archived` removed from selectable statuses | FR-004 | migration 002 |
| `wi_tshirt` ∈ allowed set | existing CHECK | DB + `update_workitem` validation |
| `area_id` references a real area | FR boundary | `update_workitem` validation |
| `parent_id` not self/cycle | FR-018 | `update_workitem` ancestor walk |
| Unsupplied update fields unchanged | FR-017 | `update_workitem` (skip None) |
| Sprint filter includes "Unassigned" | FR-012 | UI filter builder |

## Entities (unchanged structurally, exposed via MCP)

- **Project** (`insert_project` exists) — now creatable via MCP `create_project`.
- **Area** (`insert_area` exists) — now creatable via MCP `create_area`.
