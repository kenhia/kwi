# Quickstart: kwi MCP Server

## Prerequisites

- Python 3.12+
- `uv` package manager
- PostgreSQL database with kwi schema applied (see Spec 001)
- Database connection configured via one of:
  - `KWI_DATABASE_URL` environment variable
  - `~/.config/kwi/config.toml` with `database_url = "postgresql://..."`

## Install

```bash
cd /path/to/kwi
uv sync
```

## Run the MCP server

```bash
uv run kwi-mcp
```

The server communicates over stdio (JSON-RPC). It is started as a
subprocess by MCP clients, not run interactively.

## Configure in VS Code

Add to `.vscode/settings.json` (or user settings):

```json
{
  "mcp": {
    "servers": {
      "kwi": {
        "command": "uv",
        "args": ["run", "--directory", "/path/to/kwi", "kwi-mcp"]
      }
    }
  }
}
```

## Configure in Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kwi": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/kwi", "kwi-mcp"]
    }
  }
}
```

## Verify

Once configured, the MCP client should discover 12 tools:

- `list_projects`, `list_areas`
- `list_work_items`, `get_work_item`, `search_work_items`
- `create_work_item`, `update_work_item`, `archive_work_item`
- `relate_work_items`, `unrelate_work_items`, `list_related`

Test by asking your AI agent: "List all projects in kwi"
