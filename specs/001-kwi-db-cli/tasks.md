# Tasks: kwi Database Schema & CLI

**Input**: Design documents from `/specs/001-kwi-db-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-commands.md

**Tests**: Included per constitution Principle III (TDD mandatory).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/kwi/`, `tests/` at repository root
- **Migrations**: `migrations/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, package structure, and tooling configuration

- [X] T001 Initialize Python project with `uv init` and configure pyproject.toml with dependencies (typer, psycopg[binary], rich, python-frontmatter) and `[project.scripts]` entry point `kwi = "kwi.main:app"` in pyproject.toml. Note: TOML config parsing uses stdlib `tomllib` (Python 3.12+), no extra dependency needed.
- [X] T002 Create package structure: src/kwi/__init__.py, src/kwi/main.py (Typer app skeleton with `--json` and `--db-url` global options, `--version` flag), src/kwi/cli/__init__.py
- [X] T003 [P] Configure ruff (format + lint), ty (type checking), and pytest in pyproject.toml
- [X] T004 [P] Create tests/conftest.py with shared pytest fixtures (db connection, cleanup)

**Checkpoint**: `uv sync` succeeds, `kwi --help` prints help text, `ruff check` and `ty check` pass clean

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database connection layer and output formatting — required by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Write test for config resolution (flag > env > config file > error) in tests/test_db.py
- [X] T006 Implement connection config resolution in src/kwi/db.py: read `--db-url` flag, `KWI_DATABASE_URL` env var, `~/.config/kwi/config.toml` (using tomllib), return connection URL or raise error with actionable message
- [X] T007 Implement `get_connection()` in src/kwi/db.py: create psycopg connection from resolved URL, expose as context manager
- [X] T008 [P] Write test for table and JSON output rendering in tests/test_output.py
- [X] T009 [P] Implement output helpers in src/kwi/output.py: `render_table()` (Rich Table to stdout), `render_json()` (json.dumps to stdout), `render_error()` (stderr, JSON-aware), `render_detail()` (key-value pairs for show commands)
- [X] T010 [P] Create dataclasses in src/kwi/models.py: Project, Area, WorkItem, Related (matching data-model.md entities)

**Checkpoint**: Connection resolves correctly from all three sources, table and JSON output helpers work, `ruff format --check && ruff check && ty check && pytest -q` passes

---

## Phase 3: User Story 1 — Provision the Database (Priority: P1) 🎯 MVP

**Goal**: Create the SQL migration that builds the full schema and seeds reference data

**Independent Test**: Apply migration to empty DB, verify all tables and seed data exist

- [X] T011 [US1] Write test that applies migration and verifies all 6 tables exist with correct columns in tests/test_migration.py
- [X] T012 [US1] Write test that verifies seed data (9 types, 6 statuses) in tests/test_migration.py
- [X] T013 [US1] Write test that migration is idempotent (re-apply succeeds without error) in tests/test_migration.py
- [X] T014 [US1] Create migrations/001_initial_schema.sql with CREATE TABLE IF NOT EXISTS for workitem_type, workitem_status, project, area, workitem, related; INSERT ... ON CONFLICT DO NOTHING for seed data; all constraints and indexes per data-model.md

**Checkpoint**: `psql -f migrations/001_initial_schema.sql` creates schema; re-run succeeds; all migration tests pass

---

## Phase 4: User Story 2 — Manage Projects and Areas (Priority: P1)

**Goal**: CRUD commands for projects and areas via CLI

**Independent Test**: `kwi projects add`, `kwi projects list`, `kwi projects show`, `kwi areas add`, `kwi projects areas` all work end-to-end

### Tests for User Story 2

- [X] T015 [P] [US2] Write tests for project queries (create, list, show, duplicate error) in tests/test_projects.py
- [X] T016 [P] [US2] Write tests for area queries (create, list, duplicate error) in tests/test_areas.py

### Implementation for User Story 2

- [X] T017 [US2] Implement project query functions in src/kwi/queries.py: insert_project, list_projects, get_project (by name or ID)
- [X] T018 [US2] Implement area query functions in src/kwi/queries.py: insert_area, list_areas (by project)
- [X] T019 [US2] Implement `projects` CLI subcommands in src/kwi/cli/projects.py: `list`, `show`, `add`, `areas` — register as Typer sub-app in src/kwi/main.py
- [X] T020 [US2] Implement `areas` CLI subcommand in src/kwi/cli/areas.py: `add` — register as Typer sub-app in src/kwi/main.py
- [X] T021 [US2] Write CLI integration tests for projects and areas commands using CliRunner in tests/test_cli.py

**Checkpoint**: All project and area commands work in table and JSON mode; duplicate names produce clear errors; all tests pass

---

## Phase 5: User Story 3 — Create Work Items (Priority: P1)

**Goal**: Template generation and work item creation via markdown frontmatter files

**Independent Test**: `kwi work template` creates valid file; `kwi work add` parses it and inserts a work item

### Tests for User Story 3

- [X] T022 [P] [US3] Write tests for work item creation queries (insert, validation of type/status/project) in tests/test_work.py
- [X] T023 [P] [US3] Write tests for frontmatter parsing (valid file, missing fields, invalid values) in tests/test_work.py

### Implementation for User Story 3

- [X] T024 [US3] Implement work item insert query in src/kwi/queries.py: insert_workitem (resolve type/status names to IDs, validate project, area, parent)
- [X] T025 [US3] Implement `work template` command in src/kwi/cli/work.py: generate markdown file with YAML frontmatter defaults, append `.md` if missing, refuse to overwrite existing files
- [X] T026 [US3] Implement `work add` command in src/kwi/cli/work.py: parse frontmatter with python-frontmatter, validate fields, call insert_workitem, display created ID
- [X] T027 [US3] Write CLI integration tests for `work template` (including path without `.md` extension) and `work add` using CliRunner in tests/test_cli.py

**Checkpoint**: Full create flow works: template → edit → add → item in DB; invalid frontmatter produces clear errors; all tests pass

---

## Phase 6: User Story 4 — List and View Work Items (Priority: P2)

**Goal**: List work items with filters and view full details of a single item

**Independent Test**: Create items with varying types/statuses/areas, verify list output and filters, verify show output includes all fields

### Tests for User Story 4

- [X] T028 [P] [US4] Write tests for list query with filters (area, status, tshirt, archived exclusion, multi-status) in tests/test_work.py
- [X] T029 [P] [US4] Write tests for show query (all fields returned, not-found error) in tests/test_work.py

### Implementation for User Story 4

- [X] T030 [US4] Implement list_workitems query in src/kwi/queries.py: JOIN type/status/area names, filter by area, status (multi-value), tshirt, exclude archived by default, sort by ID asc
- [X] T031 [US4] Implement get_workitem query in src/kwi/queries.py: fetch all fields by ID with resolved type/status/area/project names
- [X] T032 [US4] Implement `work list` command in src/kwi/cli/work.py: `--project`, `--area`, `--status`, `--tshirt` options; render table or JSON
- [X] T033 [US4] Implement `work show` command in src/kwi/cli/work.py: display all fields as key-value pairs or JSON
- [X] T034 [US4] Write CLI integration tests for `work list` (filters, archived exclusion, empty project returns headers) and `work show` in tests/test_cli.py

**Checkpoint**: List shows correct columns, filters work, archived items excluded by default, show displays all fields; all tests pass

---

## Phase 7: User Story 5 — Update and Archive Work Items (Priority: P2)

**Goal**: Update individual fields on work items and archive items

**Independent Test**: Create an item, update fields via `work set`, verify changes; archive an item and verify it's excluded from list

### Tests for User Story 5

- [X] T035 [P] [US5] Write tests for update query (single field, multiple fields, timestamp update, validation) in tests/test_work.py
- [X] T036 [P] [US5] Write tests for archive query (status set to archived) in tests/test_work.py

### Implementation for User Story 5

- [X] T037 [US5] Implement update_workitem query in src/kwi/queries.py: dynamic SET clause for provided fields, resolve type/status names to IDs, update timestamp, validate field values
- [X] T038 [US5] Implement `work set` command in src/kwi/cli/work.py: `--type`, `--status`, `--sprint`, `--title`, `--content`, `--details` options; read file contents for content/details; require at least one option
- [X] T039 [US5] Implement `work archive` command in src/kwi/cli/work.py: set status to "archived"
- [X] T040 [US5] Write CLI integration tests for `work set` (single/multiple fields, validation errors) and `work archive` in tests/test_cli.py

**Checkpoint**: Fields update correctly, timestamps change, content/details accept file paths, archive excludes from list; all tests pass

---

## Phase 8: User Story 6 — Manage Related Items (Priority: P3)

**Goal**: Create, list, and remove relationships between work items

**Independent Test**: Create two items, relate them, list related items for each, unrelate them

### Tests for User Story 6

- [X] T041 [P] [US6] Write tests for relate/unrelate/list-related queries (bidirectional, self-reference error) in tests/test_related.py

### Implementation for User Story 6

- [X] T042 [US6] Implement relationship query functions in src/kwi/queries.py: insert_related (with self-reference check), list_related (bidirectional query), delete_related
- [X] T043 [US6] Implement `work relate`, `work unrelate`, `work related` commands in src/kwi/cli/work.py per contracts/cli-commands.md
- [X] T044 [US6] Write CLI integration tests for relate/unrelate/related commands in tests/test_cli.py

**Checkpoint**: Relationships create/list/delete correctly, self-reference blocked, bidirectional listing works; all tests pass

---

## Phase 9: User Story 7 — JSON Output (Priority: P3)

**Goal**: Global `--json` flag produces valid JSON for all commands

**Independent Test**: Run every list/show/add/set command with `--json` and verify valid JSON output

- [X] T045 [US7] Write tests that every command produces valid JSON when `--json` is passed in tests/test_output.py
- [X] T046 [US7] Write test that errors are JSON-formatted on stderr when `--json` is active in tests/test_output.py
- [X] T047 [US7] Audit all CLI commands in src/kwi/cli/ to ensure they use output.py helpers consistently and pass the json flag through; fix any gaps

**Checkpoint**: Every command's output is valid, parseable JSON with `--json`; errors also JSON on stderr; all tests pass

---

## Phase 10: User Story 8 — Connection Configuration (Priority: P3)

**Goal**: Full config precedence chain (flag > env > config file > error)

**Independent Test**: Verify connection using each method and precedence

- [X] T048 [US8] Write tests for full precedence chain (flag overrides env overrides config file) in tests/test_db.py
- [X] T049 [US8] Write test for missing config error message (all three options explained) in tests/test_db.py
- [X] T050 [US8] Verify and refine config resolution implementation in src/kwi/db.py, ensure TOML parsing, env reading, and error message match spec

**Checkpoint**: Config resolves correctly at every level; missing config produces actionable error; all tests pass

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, code quality, and final validation

- [X] T051 [P] Create docs/setup.md with installation and database setup instructions
- [X] T052 [P] Create docs/usage.md with CLI command reference and examples
- [X] T053 Run full pre-commit check suite: `ruff format --check && ruff check && ty check && pytest -q`
- [X] T054 Run quickstart.md end-to-end validation (follow steps against a clean database)
- [X] T055 Code review for NO_COLOR support in output.py (Rich handles this, verify)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — creates the database schema all other stories need
- **US2 (Phase 4)**: Depends on US1 (schema must exist) — creates projects that US3+ needs
- **US3 (Phase 5)**: Depends on US2 (projects must be creatable)
- **US4 (Phase 6)**: Depends on US3 (work items must exist to list/view)
- **US5 (Phase 7)**: Depends on US3 (work items must exist to update)
- **US6 (Phase 8)**: Depends on US3 (work items must exist to relate)
- **US7 (Phase 9)**: Depends on US2-US6 (all commands must exist to verify JSON)
- **US8 (Phase 10)**: Can run after Foundational (T005-T007 are the base; T048-T050 refine)
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: No story dependencies — foundational schema
- **US2 (P1)**: Depends on US1 — needs schema
- **US3 (P1)**: Depends on US2 — needs projects to create items
- **US4 (P2)**: Depends on US3 — needs items to list/view; can run in parallel with US5
- **US5 (P2)**: Depends on US3 — needs items to update; can run in parallel with US4
- **US6 (P3)**: Depends on US3 — needs items to relate; can run in parallel with US4/US5
- **US7 (P3)**: Depends on US2-US6 — needs all commands for JSON audit
- **US8 (P3)**: Independent of user stories — refines foundational config

### Parallel Opportunities

- T003 and T004 can run in parallel (tooling config vs test fixtures)
- T008/T009 and T010 can run in parallel (output helpers vs models)
- Within US2: T015 and T016 in parallel (project tests vs area tests)
- Within US3: T022 and T023 in parallel (query tests vs frontmatter tests)
- US4 and US5 can run in parallel after US3 completes
- US6 can run in parallel with US4/US5 after US3 completes
- US8 can start as soon as Foundational is complete
- T051 and T052 in parallel (setup docs vs usage docs)

---

## Implementation Strategy

**MVP (minimum demoable)**: Phases 1–5 (Setup → Foundational → Schema → Projects → Create Work Items). After Phase 5, a user can create projects, areas, and work items — the core loop is functional.

**Incremental delivery**:
1. Phases 1–5: Core create path (MVP)
2. Phase 6: Read path (list + show)
3. Phase 7: Update path (set + archive)
4. Phase 8: Relationships (relate/unrelate/related)
5. Phases 9–10: Polish (JSON output audit, config refinement)
6. Phase 11: Documentation and final validation
