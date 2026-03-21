# Research: kwi MCP Server

**Date**: 2026-03-21
**Feature**: 002-kwi-mcp

## R1: Python MCP SDK (`mcp` package)

**Decision**: Use the official `mcp` Python SDK (v1.x) with the
`FastMCP` high-level API.

**Rationale**: The `mcp` package is the official Model Context Protocol
SDK maintained by Anthropic. The `FastMCP` class provides a
decorator-based pattern for registering tools that is simple and
idiomatic. It handles protocol framing, JSON schema generation from
type hints, and transport (stdio/SSE) automatically.

**Alternatives considered**:
- Raw MCP protocol implementation — too much boilerplate for no benefit
- Third-party MCP libraries — less maintained, no advantage over official SDK

**Key patterns**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kwi")

@mcp.tool()
def list_projects() -> list[dict]:
    """List all projects."""
    ...
```

- Tools are registered via `@mcp.tool()` decorator
- Tool parameters are derived from function signatures with type hints
- Descriptions come from docstrings
- `mcp.run()` starts the stdio transport loop
- Error handling: raise exceptions or return error dicts; the SDK
  handles protocol-level error framing

## R2: Transport Protocol

**Decision**: stdio transport (default).

**Rationale**: stdio is the standard transport for MCP servers invoked
by VS Code, Claude Desktop, and other MCP clients. The server is
started as a subprocess; the client sends JSON-RPC over stdin and
reads responses from stdout. No network ports, no authentication,
no CORS — ideal for a single-user local tool.

**Alternatives considered**:
- SSE (Server-Sent Events) — useful for remote servers, unnecessary
  for local personal use
- WebSocket — not supported by most MCP clients yet

## R3: Database Connection Strategy in MCP Context

**Decision**: Reuse `kwi.db.resolve_db_url()` and
`kwi.db.get_connection()`. Open a connection per tool call.

**Rationale**: The MCP server is long-lived but each tool call is
independent. Opening a connection per call is simple, correct, and
sufficient for single-user workloads. Connection pooling adds
complexity with no measurable benefit at this scale.

The `resolve_db_url()` function already handles the precedence chain
(flag > env > config file). The MCP server passes `None` for the
flag value (no CLI flag) so it falls through to env var or config
file — exactly the right behavior.

**Alternatives considered**:
- Connection pooling (psycopg_pool) — overkill for single-user;
  adds a dependency
- Single persistent connection — risks stale connections after DB
  restarts; per-call is more resilient

## R4: Code Reuse Strategy

**Decision**: Import `kwi.queries`, `kwi.models`, and `kwi.db`
directly. The MCP server lives in the same Python package.

**Rationale**: The MCP server is a new entry point in the existing
`kwi` package, not a separate package. All query functions, models,
and DB connection management are importable directly. This avoids
code duplication and ensures CLI and MCP stay in sync as the
query layer evolves.

**Key reuse points**:
- `kwi.db.resolve_db_url()` — DB connection resolution
- `kwi.db.get_connection()` — connection context manager
- `kwi.queries.list_projects()` — and all other query functions
- `kwi.models.Project`, `WorkItem`, etc. — returned from queries,
  converted to dicts for MCP responses

**Alternatives considered**:
- Separate `kwi-mcp` package importing `kwi` — adds packaging
  complexity for no benefit
- Duplicate queries in MCP server — violates DRY, risks drift

## R5: Search Implementation

**Decision**: SQL `ILIKE` pattern matching for text search.

**Rationale**: Simple, no additional database setup required. The
`search_work_items` query function will use `WHERE title ILIKE
'%term%' OR content ILIKE '%term%'`. Sufficient for a personal
tool with ~500 work items.

**Alternatives considered**:
- PostgreSQL `tsvector` full-text search — more powerful but
  requires index creation and migration; can be added later if
  ILIKE performance becomes insufficient
- Application-side search — unnecessary round-trip overhead

## R6: Entry Point Configuration

**Decision**: Add `kwi-mcp` as a console script entry point in
`pyproject.toml` pointing to a `main()` function in `kwi.mcp`.

**Rationale**: This follows the same pattern as `kwi = "kwi.main:app"`.
MCP clients configure servers by command name (e.g.,
`"command": "kwi-mcp"` in VS Code `settings.json`). A dedicated
entry point makes configuration straightforward.

The MCP SDK's `FastMCP.run()` handles the event loop and stdio
transport. The entry point just needs to create the server, register
tools, and call `run()`.
