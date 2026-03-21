# kwi — Project Overview

**Created**: 2026-03-21

## Purpose

kwi (Ken's Work Items) is a personal work item tracking system
backed by a PostgreSQL database. It provides three interfaces to
the same data: a CLI, an MCP server for AI agent integration, and
a desktop GUI.

## Iteration Plan

| Spec | Scope | Tools | Tech Stack |
|------|-------|-------|------------|
| 001  | Database schema + CLI | `kwi` | Python (uv, typer, psycopg3) |
| 002  | MCP server | `kwi-mcp` | Python (uv, psycopg3) |
| 003  | Desktop GUI | `kwi-ui` | Rust / Tauri / Svelte |

## Shared Infrastructure

### Database

- **Host**: `gratch:5432`
- **Database**: `workitems`
- **Schema**: Defined in `migrations/` as raw SQL scripts,
  applied manually via `psql`
- **Migrations**: Sequential numbered files
  (`001_initial_schema.sql`, `002_...`, etc.)

### Connection Configuration

All three tools discover the database connection using the same
precedence:

1. CLI flag / tool-specific argument (`--db-url`)
2. Environment variable (`KWI_DATABASE_URL`)
3. Config file (`~/.config/kwi/config.toml`)

### Data Model (shared across all tools)

| Entity | Key Fields |
|--------|------------|
| Project | short name, GitHub repo (optional), canonical path, description |
| Area | name, description; scoped to a project |
| Work Item | project, area, type, status, t-shirt size, sprint, title, content (markdown), details (markdown), parent |
| Related | left item, right item, relationship label |

**Work Item Types**: bug, task, idea, research, tweak, issue,
feature, epic, story

**Work Item Statuses**: open, active, resolved, closed, draft,
archived

**T-Shirt Sizes**: XS, S, M, L, XL, Huge, Unknown

### Output Formatting

All tools that produce user-visible output MUST support at least:
- **Table** format (human-readable, default)
- **JSON** format (programmatic use, enabled via global `--json`
  flag for CLI)

### Sprint Semantics

Sprints are free-form text labels (not managed entities). Typical
values are feature branch names (e.g., `001-kwi-db-cli`) matching
Spec Kit iteration branches.

## Cross-Cutting Concerns

### Platform Support

- Linux and Windows clients for all tools
- CLI and MCP: Python — cross-platform via `uv`
- GUI: Tauri — cross-platform native desktop

### Shared DB Access (Python tools)

`kwi` and `kwi-mcp` both use Python with psycopg3. A shared
database access layer (package or module) SHOULD be used to avoid
duplicating connection management and query logic across the two
tools. The shape of this shared layer will be defined during
planning for Spec 001 and refined during Spec 002.

## References

- [Design Notes](../.scratch/kwi-thoughts.md)
- [M365 Discussion](../.scratch/m365-discussion.md)
- [Clarifications](../docs/clarifications-needed.md)
