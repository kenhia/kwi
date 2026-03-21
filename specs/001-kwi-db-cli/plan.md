# Implementation Plan: kwi Database Schema & CLI

**Branch**: `001-kwi-db-cli` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-kwi-db-cli/spec.md`

## Summary

Create the PostgreSQL database schema for kwi (Ken's Work Items)
and a Python CLI tool (`kwi`) for managing projects, areas, work
items, and relationships. The schema uses raw SQL migrations applied
manually. The CLI is built with Typer, uses psycopg3 for direct SQL
access, and supports both table and JSON output. Connection
configuration follows a flag > env > config file precedence chain.

## Technical Context

**Language/Version**: Python 3.12+ (managed by uv)
**Primary Dependencies**: typer (CLI framework), psycopg[binary] (PostgreSQL driver), rich (table formatting), python-frontmatter (YAML frontmatter parsing)
**Storage**: PostgreSQL (gratch:5432:workitems)
**Testing**: pytest, pytest-postgresql (integration tests against real/temp PG)
**Target Platform**: Linux and Windows
**Project Type**: CLI tool + database migrations
**Performance Goals**: All commands complete within 2 seconds for up to 1,000 work items
**Constraints**: Single-user personal tool; no auth required
**Scale/Scope**: One user, one database, ~1,000 work items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ Pass | Spec at `specs/001-kwi-db-cli/spec.md` |
| II. Architecture First | ✅ Pass | `docs/architecture.md` will be created during polish |
| III. Test-Driven Development | ✅ Pass | pytest + TDD workflow planned |
| IV. Code Standards Gate | ✅ Pass | ruff format, ruff check, ty check, pytest |
| V. User Documentation | ✅ Pass | `docs/setup.md` and `docs/usage.md` in scope |
| VI. Quality & Accessibility | ✅ Pass | Rich tables, JSON output, stderr errors, NO_COLOR support |
| VII. Simplicity | ✅ Pass | Direct SQL, no ORM, no unnecessary abstractions |

## Project Structure

### Documentation (this feature)

```text
specs/001-kwi-db-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI command reference)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
migrations/
└── 001_initial_schema.sql

src/
└── kwi/
    ├── __init__.py
    ├── main.py            # Typer app, global options (--json, --db-url)
    ├── cli/
    │   ├── __init__.py
    │   ├── projects.py    # projects list/show/add subcommands
    │   ├── areas.py       # areas add subcommand
    │   └── work.py        # work list/show/add/set/archive/template/relate/unrelate/related
    ├── db.py              # Connection management, config resolution
    ├── models.py          # Dataclasses for Project, Area, WorkItem, Related
    ├── queries.py         # SQL query functions (parameterized)
    └── output.py          # Table/JSON rendering, error formatting

tests/
├── conftest.py            # Shared fixtures (db connection, test project)
├── test_db.py             # Connection config resolution tests
├── test_projects.py       # Project CRUD tests
├── test_areas.py          # Area CRUD tests
├── test_work.py           # Work item CRUD, filtering, archive tests
├── test_related.py        # Relationship management tests
├── test_output.py         # Table/JSON rendering tests
└── test_cli.py            # CLI integration tests (typer.testing.CliRunner)

pyproject.toml             # Project metadata, dependencies, tool config
```

**Structure Decision**: Single project layout. The CLI is one Python
package (`kwi`) with submodules for CLI commands, database access,
and output formatting. `migrations/` sits at repo root since it is
not Python code. Tests mirror the source structure.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
