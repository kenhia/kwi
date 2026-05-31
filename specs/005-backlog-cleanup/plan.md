# Implementation Plan: Backlog Cleanup (Archived Flag, Filters, MCP & Tooling)

**Branch**: `005-backlog-cleanup` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-backlog-cleanup/spec.md`

## Summary

Clear the kwi backlog in one sprint by (1) making **archived** a first-class
boolean on `workitem`, decoupled from `wi_status`, with a forward migration that
repoints legacy `archived`-status rows to `closed` + `archived=true` and then
retires the `archived` status row; (2) reworking archive/un-archive across the
Python core, CLI, MCP, the Rust/Tauri command layer, and the Svelte GUI
(removing the archive confirmation dialog and adding an un-archive action);
(3) improving GUI filtering — exclude `closed` by default, keep filters sticky
within a session, add a sprint filter via the existing `MultiSelectFilter`, and
show a visual cue when a filter is off its default; (4) adding MCP
`create_project` / `create_area` tools; (5) fixing the Python update path so
`wi_tshirt`, `area_id`, and `parent_id` are settable via the CLI and MCP
(the Rust/Tauri update path already handles them); and (6) replacing the default
app icon with the kiwi mascot via `tauri icon`.

## Technical Context

**Language/Version**: Python 3.12 (uv-managed); Rust (edition 2021, Tauri 2.x); TypeScript / Svelte 5 (runes)  
**Primary Dependencies**: Typer + Rich (CLI), FastMCP (MCP), psycopg 3 (Python DB), sqlx (Rust DB), SvelteKit + Vite + Vitest, Tauri 2 CLI (`tauri icon`)  
**Storage**: PostgreSQL (prod `workitems`, tests `workitems_test`); plain `.sql` files in `migrations/` applied in sorted order  
**Testing**: pytest (Python core/CLI/MCP), cargo test (Rust commands/queries), vitest (Svelte components)  
**Target Platform**: Linux desktop (Tauri); CLI/MCP cross-platform; Windows GUI cross-builds already configured  
**Project Type**: Multi-surface — Python library+CLI+MCP, Rust/Tauri desktop backend, Svelte frontend, shared Postgres  
**Performance Goals**: Interactive desktop responsiveness; no perf-sensitive paths introduced  
**Constraints**: Forward-only `.sql` migration must be idempotent and ordered (repoint rows before retiring the `archived` status); archive semantics must be identical across all surfaces  
**Scale/Scope**: Single-user tool; 7 backlog items (WI 18, 19, 21, 38, 39, 40, 41); ~1 new migration + changes across 5 layers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Spec at `specs/005-backlog-cleanup/spec.md`; combined `docs/specification.md` to be updated in polish. |
| II. Architecture First | PASS | `docs/architecture.md` + `docs/data-model.md` updated in polish to reflect the `archived` column and status-set change. |
| III. Test-Driven Development | PASS | TDD per surface: migration test (repoint + status retired), pytest for queries/CLI/MCP, cargo test for Rust archive/un-archive, vitest for filter/un-archive UI. |
| IV. Code Standards Gate | PASS | Per-ecosystem CI checks: `ruff format --check`/`ruff check`/`ty check`/`pytest -q`; `cargo fmt --check`/`clippy -D warnings`/`cargo test`; `prettier --check`/`eslint`/`svelte-check`/`vitest run`. |
| V. User Documentation | PASS | `docs/setup.md`/`docs/usage.md` updated for new MCP tools, un-archive, filter defaults, and `work set` flags. |
| VI. Quality & Accessibility | PASS | Consistent archive semantics across surfaces; actionable errors for invalid parent (cycle)/area/tshirt; `MultiSelectFilter` reused for sprint filter. |
| VII. Simplicity & Intentional Design | PASS | Reuse existing components/patterns; no new abstractions; in-session stickiness only (cross-session persistence explicitly out of scope). |

**Gate result**: PASS — no violations; Complexity Tracking not required.

**Post-Design re-check (after Phase 1)**: PASS — design adds one column, one
migration, two MCP tools, and additive field handling; no new architectural
patterns or dependencies introduced.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
migrations/
└── 002_archived_flag.sql          # NEW: add archived col, repoint rows, retire 'archived' status

src/kwi/                           # Python core, CLI, MCP
├── models.py                      # WorkItem gains `archived: bool`
├── queries.py                     # archive/unarchive rewrite; update_workitem field_map + cycle check; insert_project/insert_area reused
├── cli/
│   ├── work.py                    # `work set` gains --tshirt/--area/--parent; `work unarchive`; archive sets flag
│   ├── projects.py                # (reference for project/area creation patterns)
│   └── areas.py
└── mcp/
    └── server.py                  # NEW create_project/create_area tools; update_work_item passes tshirt/area/parent; archive/unarchive

kwi-ui/src-tauri/src/              # Rust/Tauri backend
├── models.rs                      # WorkItem gains archived
├── queries.rs                     # archive/unarchive set flag; list filters on archived + status
├── commands.rs                    # unarchive_work_item command; list_work_items status/sprint filtering
└── ...
kwi-ui/src-tauri/
├── tauri.conf.json                # icon list (unchanged paths; regenerated assets)
└── icons/                         # REGENERATED from kiwi mascot via `tauri icon`

kwi-ui/src/                        # Svelte frontend
├── lib/
│   ├── commands.ts                # unarchiveWorkItem; sprint filter args
│   ├── stores.svelte.ts           # session-scoped filter state (sticky within session)
│   └── components/
│       ├── WorkItemList.svelte    # exclude closed default; sprint MultiSelectFilter; off-default visual cue
│       ├── WorkItemDetail.svelte  # un-archive action
│       └── MultiSelectFilter.svelte (reused)
└── routes/+page.svelte            # remove archive confirm() dialog

tests/                             # Python tests
├── test_migration.py              # 002 migration: rows repointed, status retired, idempotent
├── test_work.py                   # archive/unarchive flag; update tshirt/area/parent; cycle rejection
└── test_mcp.py                    # create_project/create_area; update fields

kwi-ui/src/lib/components/*.test.ts  # vitest: default-excludes-closed, sprint filter, un-archive, cue
kwi-ui/src-tauri/src/*               # cargo tests for archive/unarchive + filtering
```

**Structure Decision**: Existing multi-surface layout is retained. Changes are
additive within each established directory. The single schema change ships as a
new forward migration `migrations/002_archived_flag.sql`, automatically applied
by the test harness (which globs `migrations/*.sql` in sorted order) and by the
documented `psql -f` apply step.

## Complexity Tracking

> No constitution violations — section intentionally empty.
