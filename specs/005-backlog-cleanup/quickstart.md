# Quickstart: Backlog Cleanup (005)

**Feature**: 005-backlog-cleanup  
**Date**: 2026-05-30

This quickstart validates the feature end-to-end after implementation. It assumes
the test database `workitems_test` and a local dev environment.

## 1. Apply the migration

```bash
# Test DB (or your dev DB)
psql "postgresql://ken@gratch:5432/workitems_test" -f migrations/002_archived_flag.sql
```

**Verify**:

```sql
-- archived column exists, defaults false
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name='workitem' AND column_name='archived';

-- no rows reference a removed status; 'archived' status retired
SELECT name FROM workitem_status ORDER BY id;   -- expect 5 rows, no 'archived'
SELECT COUNT(*) FROM workitem w
  JOIN workitem_status s ON w.wi_status_id=s.id
  WHERE s.name='archived';                        -- expect 0
```

## 2. Python core / CLI

```bash
# Archive preserves status, sets the flag
kwi work archive <ID>
kwi work get <ID>            # status unchanged; archived = true

# Un-archive (new)
kwi work unarchive <ID>     # archived = false; status unchanged

# WI 41 fix: set previously-undroppable fields
kwi work set <ID> --tshirt L --area cli --parent <PARENT_ID>
kwi work get <ID>           # all three reflected

# Cycle protection
kwi work set <ID> --parent <ID>          # error: cannot be its own parent
kwi work set <ANCESTOR> --parent <DESC>  # error: would create a cycle
```

## 3. MCP

```text
create_project(name="demo", cn_path="/tmp/demo")     # returns Project
create_area(project="demo", name="ui")               # returns Area
update_work_item(id=<ID>, tshirt="M", area="ui")     # persists (was silently dropped)
archive_work_item(id=<ID>)                            # archived=true, status kept
unarchive_work_item(id=<ID>)                          # archived=false
```

## 4. GUI (Tauri + Svelte)

```bash
cd kwi-ui
just dev     # or: npm run tauri dev
```

**Verify**:
- Window/taskbar icon is the kiwi mascot (FR-019).
- Default list hides `closed` items (FR-008).
- Archiving an item: no confirmation dialog; item flagged archived, status kept
  (FR-002, FR-006).
- Archived item detail shows an **Un-archive** action that restores it (FR-007).
- Change a filter, navigate to a detail view and back → filter retained (FR-009).
- A filter not at its default shows a visual cue (FR-011).
- Sprint filter lists distinct sprints + "Unassigned"; deselecting hides those
  items (FR-012).

## 5. Run the gates

```bash
# Python
ruff format --check . && ruff check . && ty check && pytest -q

# Rust
cd kwi-ui/src-tauri && cargo fmt --check && cargo clippy --all-targets --all-features -- -D warnings && cargo test

# Svelte
cd kwi-ui && prettier --check . && eslint . && npx svelte-check && vitest run
```

## Acceptance mapping

| Step | Requirements covered |
|------|----------------------|
| 1 | FR-001, FR-003, FR-004, SC-001 |
| 2 | FR-002, FR-005, FR-007, FR-015, FR-017, FR-018, SC-002, SC-007 |
| 3 | FR-013, FR-014, FR-016, SC-006 |
| 4 | FR-006, FR-008, FR-009, FR-010, FR-011, FR-012, FR-019, SC-003, SC-004, SC-005, SC-008 |
