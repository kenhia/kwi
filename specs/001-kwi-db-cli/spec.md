# Feature Specification: kwi Database Schema & CLI

**Feature Branch**: `001-kwi-db-cli`
**Created**: 2026-03-21
**Status**: Draft
**Input**: Database schema and kwi CLI tool for work item tracking

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Provision the Database (Priority: P1)

As a user setting up kwi for the first time, I need to create the
database schema so that all other commands have a working data store.
I apply a SQL migration file against my PostgreSQL instance and the
schema is ready.

**Why this priority**: Nothing else works without the schema. This is
the foundation for every other story.

**Independent Test**: Run the initial migration against an empty
database, then verify all tables and seed data exist by querying
the information schema.

**Acceptance Scenarios**:

1. **Given** an empty PostgreSQL database, **When** I apply the
   initial migration script, **Then** all tables (`project`, `area`,
   `workitem`, `workitem_type`, `workitem_status`, `related`) are
   created with correct columns and constraints.
2. **Given** the migration has been applied, **When** I query
   `workitem_type` and `workitem_status`, **Then** the seed values
   (bug, task, idea, research, tweak, issue, feature, epic, story;
   open, active, resolved, closed, draft, archived) are present.
3. **Given** the migration has already been applied, **When** I
   attempt to apply it again, **Then** it fails gracefully (or is
   idempotent) without corrupting existing data.

---

### User Story 2 — Manage Projects and Areas (Priority: P1)

As a user, I need to create and view projects and their areas so
that work items can be organized by project and functional area.

**Why this priority**: Work items require a project. Without project
management, no work items can be created.

**Independent Test**: Create a project, list projects, show project
details, add an area to the project, list areas.

**Acceptance Scenarios**:

1. **Given** an initialized database, **When** I run
   `kwi projects add` with a short name, canonical path, and
   description, **Then** a new project is created and its ID is
   displayed.
2. **Given** one or more projects exist, **When** I run
   `kwi projects list`, **Then** I see a table of project IDs and
   short names.
3. **Given** a project exists, **When** I run `kwi projects show`
   with its short name or ID, **Then** I see all fields of that
   project.
4. **Given** a project exists, **When** I run `kwi areas add` with
   a project and area name, **Then** a new area is created under
   that project.
5. **Given** a project with areas, **When** I run
   `kwi projects areas --project <name>`, **Then** I see the areas
   for that project.
6. **Given** a project exists, **When** I attempt to create another
   project with the same short name, **Then** I receive a clear
   error message.

---

### User Story 3 — Create Work Items (Priority: P1)

As a user, I need to add new work items to a project so that I can
track bugs, tasks, ideas, and other work.

**Why this priority**: Creating work items is the core purpose of
the tool. Without this, there is nothing to list, update, or manage.

**Independent Test**: Generate a template, fill it in, add the work
item, verify it appears in the database.

**Acceptance Scenarios**:

1. **Given** a project exists, **When** I run `kwi work template`
   with a file path, **Then** a markdown template file is created
   with frontmatter fields (project, title, area, type, t-shirt,
   status, sprint, parent) and a content section.
2. **Given** I have a completed template file, **When** I run
   `kwi work add <path>`, **Then** the work item is created and
   its ID is displayed.
3. **Given** a template references a project that does not exist,
   **When** I run `kwi work add`, **Then** I receive a clear error
   identifying the invalid project.
4. **Given** a template with an invalid type or status value,
   **When** I run `kwi work add`, **Then** I receive a clear error
   listing the valid values.
5. **Given** a template specifying a parent ID, **When** I run
   `kwi work add`, **Then** the work item is created with the
   parent relationship set.

---

### User Story 4 — List and View Work Items (Priority: P2)

As a user, I need to list and filter work items for a project and
view the full details of any individual item.

**Why this priority**: Once items exist, the user needs to find and
read them. This is the primary read path.

**Independent Test**: Create several work items with different
types, statuses, and areas; verify list output and filters;
verify show output includes all fields.

**Acceptance Scenarios**:

1. **Given** work items exist for a project, **When** I run
   `kwi work list --project <name>`, **Then** I see a table with
   ID, area, type, status, and title for each item, sorted by ID.
2. **Given** work items exist, **When** I run `kwi work list` with
   `--area`, `--status`, or `--tshirt` filters, **Then** only
   matching items are shown.
3. **Given** a work item exists, **When** I run
   `kwi work show <id>`, **Then** I see all fields including
   content and details rendered as text.
4. **Given** archived work items exist, **When** I run
   `kwi work list` without a status filter, **Then** archived
   items are excluded.
5. **Given** archived work items exist, **When** I run
   `kwi work list --status archived`, **Then** only archived items
   are shown.
6. **Given** the `--status` filter accepts multiple values
   (comma-separated), **When** I run
   `kwi work list --status open,active`, **Then** items matching
   either status are shown.

---

### User Story 5 — Update and Archive Work Items (Priority: P2)

As a user, I need to update fields on existing work items and
archive items that are no longer active.

**Why this priority**: Work items change over time — status
transitions, sprint assignments, content edits. This is the
primary write path after creation.

**Independent Test**: Create a work item, update individual fields
via `kwi work set`, verify changes; archive an item and verify it
is excluded from default list.

**Acceptance Scenarios**:

1. **Given** a work item exists, **When** I run
   `kwi work set <id> --status active`, **Then** the item's status
   is updated and the updated timestamp changes.
2. **Given** a work item exists, **When** I run
   `kwi work set <id> --content <path>`, **Then** the item's
   content is replaced with the contents of the file.
3. **Given** a work item exists, **When** I run
   `kwi work set <id>` with multiple flags (e.g., `--status`,
   `--sprint`, `--title`), **Then** all specified fields are
   updated in a single operation.
4. **Given** a work item exists, **When** I run
   `kwi work archive <id>`, **Then** the item's status is set to
   "archived."
5. **Given** an invalid field value (e.g., a nonexistent status),
   **When** I run `kwi work set`, **Then** I receive a clear error
   and no changes are applied.

---

### User Story 6 — Manage Related Items (Priority: P3)

As a user, I need to link work items together with a named
relationship so I can track dependencies and connections.

**Why this priority**: Relationships are useful but not required
for basic tracking. They add value once the core workflow is
established.

**Independent Test**: Create two work items, relate them, list
related items for each, unrelate them.

**Acceptance Scenarios**:

1. **Given** two work items exist, **When** I run
   `kwi work relate <id1> <id2> --relationship "blocks"`,
   **Then** a relationship is created between them.
2. **Given** a work item has related items, **When** I run
   `kwi work related <id>`, **Then** I see all items related to
   it with their relationship labels (in both directions).
3. **Given** two related items, **When** I run
   `kwi work unrelate <id1> <id2>`, **Then** the relationship
   is removed.
4. **Given** I attempt to relate a work item to itself, **When** I
   run `kwi work relate <id> <id>`, **Then** I receive an error.

---

### User Story 7 — JSON Output (Priority: P3)

As a user integrating kwi with scripts or other tools, I need
machine-readable output from any command.

**Why this priority**: Enables automation and scripting but is not
needed for manual daily use.

**Independent Test**: Run any list/show command with the `--json`
global flag and verify the output is valid JSON containing the
same data as the table output.

**Acceptance Scenarios**:

1. **Given** any command that produces output, **When** I pass the
   `--json` global flag, **Then** the output is valid JSON.
2. **Given** the `--json` flag is used, **When** the command
   produces an error, **Then** the error is also formatted as JSON
   on stderr.

---

### User Story 8 — Connection Configuration (Priority: P3)

As a user, I need flexible database connection configuration so
kwi works across my machines without hardcoded values.

**Why this priority**: The tool must connect to the database, but a
sensible default or environment variable covers most use during
development. Full config flexibility is a polish concern.

**Independent Test**: Verify connection is established using each
configuration method and that precedence is respected.

**Acceptance Scenarios**:

1. **Given** a `--db-url` flag is passed, **When** kwi runs,
   **Then** it connects using that URL regardless of env or config.
2. **Given** no flag is passed but `KWI_DATABASE_URL` is set,
   **When** kwi runs, **Then** it connects using the env variable.
3. **Given** no flag or env variable, but
   `~/.config/kwi/config.toml` exists with a `database_url` key,
   **When** kwi runs, **Then** it connects using the config file.
4. **Given** none of the above are set, **When** kwi runs,
   **Then** it displays a clear error explaining how to configure
   the connection.

---

### Edge Cases

- Empty project (no work items) — list returns an empty table with
  headers, not an error.
- Very long markdown content — content and details fields accept
  markdown of any practical length.
- Non-existent IDs — all commands referencing an ID that does not
  exist return a clear "not found" error.
- Template file path without `.md` extension — the tool appends it
  automatically.
- Unicode in titles and content — fully supported.
- Concurrent access — the database handles concurrent reads and
  writes; the CLI does not need special locking.

## Requirements *(mandatory)*

### Functional Requirements

**Database Schema**

- **FR-001**: The system MUST provide a SQL migration file that
  creates all required tables and seed data.
- **FR-002**: The schema MUST enforce referential integrity via
  foreign keys for all entity relationships.
- **FR-003**: Work item types and statuses MUST be stored as
  reference tables with seed data, not as unconstrained text.
- **FR-004**: T-shirt sizes MUST be constrained to the defined set
  (XS, S, M, L, XL, Huge, Unknown) with a default of Unknown.
- **FR-005**: Timestamps (created, updated) MUST be set
  automatically and updated on modification.

**Project Management**

- **FR-006**: The user MUST be able to create a project with a
  short name (unique), canonical path (filesystem path), and
  optional GitHub repo URL and description.
- **FR-007**: The user MUST be able to list all projects (ID and
  short name).
- **FR-008**: The user MUST be able to view all fields of a
  specific project by short name or ID.
- **FR-009**: The user MUST be able to create areas scoped to a
  project (with unique name per project).
- **FR-010**: The user MUST be able to list areas for a project.

**Work Item Management**

- **FR-011**: The user MUST be able to generate a markdown template
  file with frontmatter for creating work items.
- **FR-012**: The user MUST be able to create a work item by
  providing a markdown file with frontmatter (project, title, type,
  status, and content are required; area, t-shirt, sprint, parent
  are optional).
- **FR-013**: The user MUST be able to list work items for a
  project, showing ID, area, type, status, and title.
- **FR-014**: Work item lists MUST be filterable by area, status
  (comma-separated for multiple), and t-shirt size.
- **FR-015**: The user MUST be able to view all fields of a
  specific work item by ID.
- **FR-016**: The user MUST be able to update one or more fields
  of an existing work item (type, status, sprint, title, content,
  details).
- **FR-017**: Content and details updates MUST accept a file path
  to a markdown file.
- **FR-018**: The user MUST be able to archive a work item (sets
  status to "archived").
- **FR-019**: Archived items MUST be excluded from list output by
  default, but included when explicitly filtered.
- **FR-020**: Work items MUST be listed in order of ID (ascending)
  by default.

**Relationships**

- **FR-021**: The user MUST be able to create a named relationship
  between two work items.
- **FR-022**: The user MUST be able to list all items related to a
  given work item (in both directions).
- **FR-023**: The user MUST be able to remove a relationship
  between two items.
- **FR-024**: The system MUST prevent a work item from being
  related to itself.

**Output & Configuration**

- **FR-025**: All commands producing output MUST default to
  human-readable table format.
- **FR-026**: A global `--json` flag MUST switch all output to JSON.
- **FR-027**: Errors MUST be written to stderr with actionable
  messages; in JSON mode, errors MUST also be JSON-formatted.
- **FR-028**: Database connection MUST be configurable via CLI flag
  (`--db-url`), environment variable (`KWI_DATABASE_URL`), or
  config file (`~/.config/kwi/config.toml`), with precedence:
  flag > env > config file.
- **FR-029**: If no connection configuration is found, the tool
  MUST display a clear error explaining the configuration options.

### Key Entities

- **Project**: A named container for work items. Has a unique short
  name, canonical filesystem path, optional GitHub repo URL, and
  optional markdown description.
- **Area**: A sub-grouping within a project. Has a name (unique
  per project) and optional description.
- **Work Item**: The core trackable unit. Belongs to a project,
  optionally to an area. Has a type, status, t-shirt size, optional
  sprint label, title, markdown content, optional markdown details,
  and optional parent work item.
- **Related**: A named link between two work items (e.g., "blocks",
  "duplicates", "related to").

## Assumptions

- The PostgreSQL database already exists and is accessible; this
  spec covers schema creation, not database server provisioning.
- The user has `psql` available for applying migrations.
- This is a single-user personal tool; authentication and
  authorization are not required.
- The config file format is TOML with a `database_url` key.
- Project deletion and area deletion are not in scope for this
  iteration (can be done via SQL if needed).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from an empty database to creating and
  listing work items in under 5 minutes.
- **SC-002**: Every CLI command completes within 2 seconds for a
  database containing up to 1,000 work items.
- **SC-003**: All valid work item types and statuses are accepted;
  all invalid values produce clear error messages listing the
  valid options.
- **SC-004**: The `--json` flag produces valid, parseable JSON for
  every command that produces output.
- **SC-005**: The tool works on both Linux and Windows without
  platform-specific setup beyond Python and database access.
- **SC-006**: A user unfamiliar with the tool can understand every
  error message and take corrective action without consulting
  documentation.
