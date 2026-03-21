# kwi Architecture

## System Components

```
┌─────────┐     ┌───────────┐     ┌────────────┐
│  CLI    │────▶│  queries  │────▶│ PostgreSQL │
│  (kwi)  │     │           │     │            │
└─────────┘     │  models   │     └────────────┘
                │  db       │
┌─────────┐     │           │
│  MCP    │────▶│           │
│(kwi-mcp)│     └───────────┘
└─────────┘
```

## Package Structure

```
src/kwi/
├── __init__.py          # Package init
├── main.py              # Typer CLI app with global options
├── output.py            # Table/JSON output formatting
├── db.py                # DB URL resolution and connection management
├── models.py            # Dataclasses: Project, Area, WorkItem, Related
├── queries.py           # SQL query functions (all DB operations)
├── cli/
│   ├── projects.py      # Projects subcommands
│   ├── areas.py         # Areas subcommands
│   └── work.py          # Work items subcommands
└── mcp/
    ├── __init__.py      # MCP entry point (main → mcp.run())
    └── server.py        # FastMCP instance + 12 tool definitions
```

## Key Design Decisions

### Shared Query Layer

Both CLI and MCP server use the same `queries.py` functions.
This ensures consistent behavior and a single source of truth
for all database operations.

### MCP Transport

stdio transport only. The MCP server is designed to be launched
by an MCP client as a subprocess. No HTTP/SSE transport.

### Database Connection

- CLI: Connection managed via Typer callback, passed through
  context state
- MCP: Each tool call creates its own connection via
  `get_connection(_db_url())`

### Error Handling

- CLI: Typer-friendly error messages with `rich` formatting
- MCP: JSON error responses `{"error": "message"}` — never
  raises exceptions to the MCP client

### Configuration Precedence

1. CLI flag (`--db-url`)
2. Environment variable (`KWI_DATABASE_URL`)
3. Config file (`~/.config/kwi/config.toml`)
