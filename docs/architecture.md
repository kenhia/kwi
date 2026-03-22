# kwi Architecture

## System Components

```
┌─────────┐     ┌───────────┐     ┌────────────┐
│  CLI    │────▶│  queries  │────▶│ PostgreSQL │
│  (kwi)  │     │  (Python) │     │            │
└─────────┘     │  models   │     └────────────┘
                │  db       │
┌─────────┐     │           │
│  MCP    │────▶│           │
│(kwi-mcp)│     └───────────┘
└─────────┘

┌─────────┐     ┌───────────┐     ┌────────────┐
│  GUI    │────▶│  queries  │────▶│ PostgreSQL │
│(kwi-ui) │     │  (Rust)   │     │            │
└─────────┘     │  models   │     └────────────┘
  Tauri 2       │  db       │
  Svelte 5      └───────────┘
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

### Desktop GUI (kwi-ui)

```
kwi-ui/
├── src/                         # Svelte 5 frontend
│   ├── routes/+page.svelte      # Main page layout
│   └── lib/
│       ├── types.ts             # TypeScript interfaces
│       ├── commands.ts          # Tauri invoke wrappers
│       ├── stores.svelte.ts     # Reactive state ($state runes)
│       └── components/
│           ├── ProjectSelector.svelte
│           ├── WorkItemList.svelte
│           ├── WorkItemDetail.svelte
│           ├── WorkItemForm.svelte
│           ├── SearchBar.svelte
│           └── RelationshipPanel.svelte
└── src-tauri/                   # Rust backend
    └── src/
        ├── lib.rs               # Tauri app setup + command registration
        ├── main.rs              # Entry point
        ├── db.rs                # Connection pool + config reading
        ├── models.rs            # Rust structs (serde)
        ├── queries.rs           # SQL query functions
        └── commands.rs          # #[tauri::command] IPC handlers
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
- GUI: deadpool-postgres connection pool created at startup,
  shared via Tauri `State<AppState>`

### Error Handling

- CLI: Typer-friendly error messages with `rich` formatting
- MCP: JSON error responses `{"error": "message"}` — never
  raises exceptions to the MCP client
- GUI: Connection errors show config instructions screen;
  query errors displayed inline in components

### Configuration Precedence

1. CLI flag (`--db-url`) — CLI only
2. Environment variable (`KWI_DATABASE_URL`)
3. Config file (`~/.config/kwi/config.toml`)

### GUI IPC Architecture

The desktop GUI uses Tauri 2's command system for frontend-backend
communication. Each Svelte component calls typed wrapper functions
in `commands.ts`, which invoke Rust `#[tauri::command]` handlers
via JSON-serialized IPC. The Rust handlers call query functions
that mirror the Python `queries.py` patterns (same SQL, same
column order) against the same PostgreSQL database.
