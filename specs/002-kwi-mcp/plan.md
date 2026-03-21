# Implementation Plan: kwi MCP Server

**Branch**: `002-kwi-mcp` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-kwi-mcp/spec.md`

## Summary

Expose the kwi work item database to AI agents via Model Context Protocol (MCP).
The server provides 12 tools (list/get/create/update/archive for work items,
list projects/areas, manage relationships, search) using the official Python MCP
SDK. It reuses all query functions and connection management from the existing
`kwi` package — no new SQL or schema changes.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: mcp (Python MCP SDK), psycopg3 (via existing kwi package)
**Storage**: PostgreSQL (existing `workitems` database, no schema changes)
**Testing**: pytest (unit tests for tool handlers; integration tests against DB)
**Target Platform**: Linux and Windows (cross-platform via uv)
**Project Type**: MCP server (stdio transport, long-running process)
**Performance Goals**: Single-user, no concurrent load targets
**Constraints**: Must reuse existing `kwi.queries` and `kwi.db` modules
**Scale/Scope**: Single user, ~12 MCP tools, ~500 work items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Spec at `specs/002-kwi-mcp/spec.md` |
| II. Architecture First | PASS | Will update `docs/architecture.md` during polish |
| III. Test-Driven Development | PASS | Tests will be written before implementation |
| IV. Code Standards Gate | PASS | ruff format, ruff check, ty check, pytest |
| V. User Documentation | PASS | `docs/setup.md` and `docs/usage.md` will be updated |
| VI. Quality & Accessibility | PASS | Structured error messages; no raw stack traces |
| VII. Simplicity & Intentional Design | PASS | Reuses existing queries; MCP SDK's decorator pattern; no extra abstractions |

No violations. Gate passed.

## Project Structure

### Documentation (this feature)

```text
specs/002-kwi-mcp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (MCP tool schemas)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/kwi/
├── __init__.py          # existing
├── main.py              # existing CLI entry point
├── db.py                # existing — reused by MCP server
├── models.py            # existing — reused by MCP server
├── queries.py           # existing — reused by MCP server
├── output.py            # existing CLI output (not used by MCP)
├── cli/                 # existing CLI subcommands
│   ├── __init__.py
│   ├── projects.py
│   ├── areas.py
│   └── work.py
└── mcp/                 # NEW — MCP server
    ├── __init__.py      # MCP server factory
    └── server.py        # tool definitions

tests/
├── conftest.py          # existing fixtures (reused)
├── test_mcp.py          # NEW — MCP tool handler tests
└── ...                  # existing test files
```

**Structure Decision**: The MCP server lives in `src/kwi/mcp/` as a new
subpackage alongside the existing `src/kwi/cli/`. Both share `db.py`,
`models.py`, and `queries.py`. The server gets its own entry point in
`pyproject.toml` (`kwi-mcp = "kwi.mcp:main"`).

## Implementation Phases

### Phase 1: Project setup & MCP server skeleton

- Add `mcp` dependency to `pyproject.toml`
- Create `src/kwi/mcp/__init__.py` with server factory
- Create `src/kwi/mcp/server.py` with MCP server initialization
- Add `kwi-mcp` entry point to `pyproject.toml`
- Verify `uv run kwi-mcp` starts and accepts stdio connection

### Phase 2: Read-only tools (US1 — P1)

- Implement `list_projects` tool
- Implement `list_areas` tool (accepts project name or ID)
- Implement `list_work_items` tool (with project, status, area, type, tshirt, sprint filters)
- Implement `get_work_item` tool (by ID, full details)
- Write tests for all read-only tools

### Phase 3: Write tools (US2, US3, US4 — P1/P2)

- Implement `create_work_item` tool
- Implement `update_work_item` tool
- Implement `archive_work_item` tool
- Write tests for all write tools

### Phase 4: Relationship tools (US5 — P3)

- Implement `relate_work_items` tool
- Implement `unrelate_work_items` tool
- Implement `list_related` tool
- Write tests for relationship tools

### Phase 5: Search tool (US6 — P3)

- Add `search_work_items` query function to `kwi.queries`
- Implement `search_work_items` MCP tool
- Write tests for search

### Phase 6: Polish & documentation

- Update `docs/setup.md` with MCP server setup instructions
- Update `docs/usage.md` with MCP tool reference
- Run full lint/type/test gate
- Verify with an MCP client (VS Code Copilot agent mode)
