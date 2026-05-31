# Phase 0 Research: Backlog Cleanup

**Feature**: 005-backlog-cleanup  
**Date**: 2026-05-30

This feature is mostly well-understood (decisions were settled in
`specs/planning/005-backlog-cleanup-preplan.md`). The items below resolve the
remaining technical unknowns and record the patterns to follow.

## R1 — Archived as a boolean separate from status

**Decision**: Add `archived boolean NOT NULL DEFAULT false` to `workitem`,
independent of `wi_status_id`. Archiving sets `archived = true` and preserves the
existing status. Un-archiving sets `archived = false`.

**Rationale**: Today `archive_workitem` sets `wi_status` to the `archived` row,
which is destructive (loses the real status) and conflates lifecycle state with
visibility. A dedicated flag makes archiving non-destructive and lets filters
reason about status and archived independently (required by US4/US5).

**Alternatives considered**:
- *Keep status-based archiving* — rejected: destructive, blocks un-archive to a
  meaningful prior state.
- *Separate `archived_at timestamp`* — rejected as YAGNI (Principle VII); no
  requirement for archive timestamps. A boolean is sufficient; can be revisited.

## R2 — Migration strategy and ordering

**Decision**: Ship `migrations/002_archived_flag.sql`, forward-only and
idempotent, doing in order:
1. `ALTER TABLE workitem ADD COLUMN IF NOT EXISTS archived boolean NOT NULL DEFAULT false;`
2. Repoint rows: set `archived = true, wi_status_id = (closed)` for every row
   whose status is currently `archived`.
3. Delete the `archived` row from `workitem_status` (safe only after step 2
   leaves zero references; FK is `workitem.wi_status_id → workitem_status.id`).
4. Add an index on `archived` (`CREATE INDEX IF NOT EXISTS idx_workitem_archived`).

**Rationale**: The test harness (`tests/conftest.py`) applies `migrations/*.sql`
in sorted order, so `002_…` runs after `001_…` automatically — no migration
runner needed. Idempotency mirrors `001` (`IF NOT EXISTS`, `ON CONFLICT`)
so re-apply is safe. FK ordering (repoint before delete) prevents constraint
violations (SC-001).

**Alternatives considered**:
- *Leave `archived` status row orphaned* — rejected by user decision (Q2): a
  dangling, never-valid status is a footgun in dropdowns and validation.
- *A Python/Rust migration runner* — rejected as over-engineering; the existing
  sorted-glob `.sql` convention is sufficient.

**Idempotency note**: Step 2 selects by joining to the status name, so a second
run finds zero `archived`-status rows (no-op). Step 3 uses
`DELETE … WHERE name = 'archived'` (no-op once gone). Step 1 uses
`ADD COLUMN IF NOT EXISTS`.

## R3 — WI 41 scope: which layers actually drop fields

**Decision**: Fix the **Python** layer only for WI 41:
`queries.update_workitem` adds `wi_tshirt`, `area_id`, `parent_id` to its
`field_map` (with validation), the CLI `work set` exposes `--tshirt/--area/
--parent`, and the MCP `update_work_item` forwards those params into `fields`.

**Rationale**: Inspection shows the **Rust/Tauri** `update_work_item` command and
its `queries.rs` already accept and persist `wi_tshirt`, `area_id`, and
`parent_id`. The silent no-op (WI 41, discovered while sizing WI 21) is confined
to the Python `field_map` omission plus the CLI/MCP surfaces not exposing them.
Scoping the fix to Python avoids touching a working path.

**Alternatives considered**:
- *Re-touch the Rust path* — rejected: already correct; would be churn.

## R4 — Cycle/self-parent protection

**Decision**: When updating `parent_id`, reject (a) self-parenting and (b) any
parent that is a descendant of the item (which would create a cycle), with an
actionable error. Implement a bounded ancestor walk in `queries.update_workitem`.

**Rationale**: `workitem.parent_id` is a self-referential FK with no DB-level
cycle guard. Allowing updates to set parent now makes cycle protection necessary
(FR-018, edge cases). A simple ancestor walk is sufficient at single-user scale.

**Alternatives considered**:
- *Recursive CTE check in SQL* — viable but heavier; the Python walk is simpler
  and adequately fast for this scale (Principle VII).
- *No protection* — rejected: violates FR-018 and risks infinite loops in tree
  rendering.

## R5 — Sticky filters (in-session only)

**Decision**: Hold filter selections (statuses, types, areas, sprints, and the
archived toggle) in the shared Svelte runes store (`stores.svelte.ts`) so they
persist across in-app navigation for the session. **No** `localStorage`
persistence (cross-session is out of scope, FR-010). Default the status filter to
exclude `closed` (FR-008). Show a visual cue when any filter differs from its
default (FR-011).

**Rationale**: `WorkItemList.svelte` currently initializes filter `Set`s in
component-local state, so they reset whenever the list remounts during
navigation. Lifting that state into the module-level `appState` runes store makes
it survive navigation without new dependencies. The existing window-state
`localStorage` path is deliberately *not* reused here, per the deferral decision.

**Alternatives considered**:
- *`localStorage`-backed filters now* — rejected (Q3 deferral); revisit later if
  needed.
- *URL/query-param state* — rejected: heavier and unnecessary for a desktop app.

## R6 — Sprint filter source and "Unassigned" bucket

**Decision**: Build the sprint filter options from the distinct non-null `sprint`
values present in the currently loaded work items, plus a synthetic
"Unassigned" entry that matches items with `sprint IS NULL`. Reuse
`MultiSelectFilter` (all options selected by default), mirroring the existing
status/type/area filters.

**Rationale**: Sprints are free-text labels on `workitem` (no sprint table), so a
dynamic distinct list is the natural source (FR-012). Reusing
`MultiSelectFilter` keeps UX consistent (Principle VI) and avoids new components
(Principle VII).

**Alternatives considered**:
- *A dedicated sprint entity/table* — rejected: out of scope and unnecessary for
  filtering.

## R7 — Application icon generation

**Decision**: Generate the platform icon set from the confirmed square source
`/gratch/kIcons/kwi-kiwi-mascot-cropped.png` (760×760) using the Tauri CLI:
`tauri icon /gratch/kIcons/kwi-kiwi-mascot-cropped.png`, which regenerates the
files already referenced in `tauri.conf.json` (`32x32.png`, `128x128.png`,
`128x128@2x.png`, `icon.icns`, `icon.ico`, plus Windows Store/Android variants).

**Rationale**: The Tauri 2 CLI ships `tauri icon`; the source is square so no
padding is needed (Q4). No new tooling install and no external `ansible-k`
hand-off required.

**Alternatives considered**:
- *Manual per-format export (ImageMagick)* — rejected: `tauri icon` is purpose-
  built and produces the exact set Tauri expects.
- *External hand-off doc* — rejected (Q4): unnecessary.

## R8 — MCP project & area creation

**Decision**: Add `create_project` and `create_area` MCP tools that wrap the
existing `queries.insert_project` / `queries.insert_area`, returning the created
entity serialized like the other MCP tools.

**Rationale**: The query functions already exist and are used by the CLI; the gap
is only MCP exposure (FR-013/FR-014). Thin wrappers keep parity with the CLI and
avoid logic duplication.

**Alternatives considered**:
- *Seed default areas automatically on project creation* — deferred; not required
  by the spec, and would add implicit behavior (Principle VII). `create_area`
  covers the need explicitly.

## Open questions

None — all `[NEEDS CLARIFICATION]` items were resolved in pre-planning.
