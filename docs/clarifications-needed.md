# kwi — Clarifications Needed

Decisions to resolve before writing the first spec.

## 1. Iteration Scope

The project has three deliverables: `kwi` (CLI), `kwi-ui` (GUI),
and `kwi-mcp` (MCP server). The constitution requires iteration-scoped
specs.

**Question**: What should the first spec cover?

Suggested breakdown:
- **Spec 001**: Database schema (migrations) + `kwi` CLI
- **Spec 002**: `kwi-mcp` server
- **Spec 003**: `kwi-ui` (Tauri/Svelte)

This lets the CLI validate the schema before building the GUI on top.
Alternatively, schema + CLI + MCP could be one spec since they share
the Python codebase and DB layer.

**Decision**: use suggested breakdown, three specs with GUI being last.

## 2. Project & Area Management Commands

The CLI defines `projects list`, `projects show`, and
`projects areas`, but there are no commands to **create, update, or
delete** projects or areas.

**Question**: How are projects and areas managed?
- (a) CLI commands (`kwi projects add`, `kwi areas add`, etc.)
- (b) GUI only
- (c) Direct SQL / migration scripts
- (d) All of the above — CLI + GUI, with SQL for initial seeding

**Decision**: a

## 3. Related Items Management

The schema has a `related` table but no CLI commands reference it.

**Question**: Should the CLI support managing relationships?
```
kwi work relate <id1> <id2> --relationship <text>
kwi work unrelate <id1> <id2>
kwi work related <id>   # list related items
```

Or is this GUI/MCP-only? Or deferred to a later spec?

**Decision**: your example is perfect for `related`

## 4. `cn_path` Field on Project

The `project` table has a `cn_path TEXT NOT NULL` column described as
"canonical path."

**Question**: What does this represent?
- (a) Filesystem path to the project's source code
- (b) A URL or URI (e.g., to a repo or docs site)
- (c) A hierarchical namespace (e.g., `org/team/project`)
- (d) Something else

**Decision**: a, example using this project "~/src/kwi"

## 5. Database Connection Configuration

The database is at `gratch:5432:workitems`.

**Question**: How should tools discover the connection?
- (a) Environment variable (e.g., `KWI_DATABASE_URL`)
- (b) Config file (e.g., `~/.config/kwi/config.toml`)
- (c) CLI flag (`--db-url`) with env var fallback
- (d) All three with precedence: flag > env > config file

**Decision**: d

## 6. Database Migration Strategy

**Question**: How should the schema be provisioned and evolved?
- (a) Raw SQL scripts in a `migrations/` directory, applied manually
- (b) Alembic (Python migration tool, pairs with SQLAlchemy)
- (c) A `kwi db migrate` CLI subcommand wrapping one of the above
- (d) Other

**Decision**: a — raw SQL scripts in `migrations/`, applied manually. Simple, no extra dependencies, matches a personal project. Can wrap in a CLI subcommand later if needed.

## 7. Output Formatting

The constitution (Principle VI) requires JSON output for programmatic
use.

**Question**: Should the CLI support output format flags?
```
kwi work list --project foo --format json
kwi work list --project foo --format table   # default
```

Or a global flag like `kwi --json work list ...`?

**Decision**: global flag

## 8. `kwi-mcp` Capabilities

The thoughts doc says "fully open to suggestions." Here's a proposed
tool set for the MCP server:

| MCP Tool | Description |
|----------|-------------|
| `list_projects` | List all projects |
| `list_work_items` | List/filter work items (project, status, area, type) |
| `get_work_item` | Get full details of a work item by ID |
| `create_work_item` | Create a new work item |
| `update_work_item` | Update fields on an existing work item |
| `archive_work_item` | Archive a work item |
| `list_areas` | List areas for a project |
| `search_work_items` | Full-text search across titles and content |

This mirrors the CLI surface. The agent can then read/create/update
work items during coding sessions.

**Question**: Does this cover the intended use? Any tools to add or
remove?

**Decision**: Looks good.

## 9. Sprint Semantics

Sprints are stored as a nullable `TEXT` field — just a label.

**Question**: Is this intentional (free-form text like "2026-Q1" or
"March Week 3"), or should sprints be a managed entity with start/end
dates?

**Decision**: intentional; I use "sprint" as that's a mindset I have at work and how I think of as a "demoable set of work". As I use Spec Kit, each iteration of work has a branch the work is done in like "001-kwi-db-cli"; generally this branch name is what I'll put in for "sprint"

## 10. Work Item Ordering & Pagination

`kwi work list` doesn't mention sort order or pagination.

**Question**:
- Default sort: by ID (creation order)? By updated date? By status?
- Should there be `--sort` and `--limit`/`--offset` flags?
- Or is the list always "all items" (filtered by status, area, etc.)?

**Decision**: default sort should be by id, no pagination. I like the idea of the additional flags, but we can defer those to later (post MVP across all three tools)

## 11. Python DB Layer

**Question**: What library for PostgreSQL access?
- (a) `psycopg` (psycopg3) — direct SQL, minimal abstraction
- (b) SQLAlchemy Core — query builder, no ORM overhead
- (c) SQLAlchemy ORM — full object mapping
- (d) `asyncpg` — async-first (relevant if MCP server is async)

Since both `kwi` and `kwi-mcp` are Python, they should share a
common DB access library (e.g., a `kwi-core` package or shared
module).

**Decision**: a — psycopg (psycopg3). Direct SQL matches the raw-SQL migration strategy, supports both sync and async (covers CLI and MCP), minimal dependencies.

---

## Summary

All decisions resolved. Ready to proceed with `/speckit.spec` for
Spec 001 (database schema + `kwi` CLI).

**Suggested defaults** if you want to move fast:
- **7**: `--format json|table` flag, table default
- **8**: Accept proposed MCP tools as-is
- **9**: Free-form text, no managed sprint entity
- **10**: Default sort by ID desc, add `--sort` later if needed
