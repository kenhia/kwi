# kwi Setup Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL server (tested on gratch:5432)

## Installation

```bash
# Clone and install
git clone <repo-url> && cd kwi
uv sync
```

## Database Setup

1. Create the database (if needed):

```sql
CREATE DATABASE workitems;
```

2. Apply the initial migration:

```bash
psql -h gratch -U ken -d workitems -f migrations/001_initial_schema.sql
```

This creates all tables and seeds the reference data (9 work item
types, 6 statuses). The migration is idempotent — safe to re-run.

## Configuration

Configure the database connection using one of (in precedence order):

1. **CLI flag**: `kwi --db-url postgresql://user:pass@host/db <command>`
2. **Environment variable**: `export KWI_DATABASE_URL=postgresql://user:pass@host/db`
3. **Config file**: `~/.config/kwi/config.toml`

```toml
database_url = "postgresql://user:pass@host:5432/workitems"
```

### Connection String Formats

Both `kwi` (CLI) and `kwi-ui` (GUI) accept either format:

- **URI**: `postgresql://user:pass@host:5432/workitems`
- **Key=value**: `host=gratch port=5432 dbname=workitems user=ken`

URI format is recommended for portability.

### Separate Password (kwi-ui)

To keep the password out of the connection string and environment
variables, add `db_password` to `config.toml`:

```toml
database_url = "postgresql://ken@gratch:5432/workitems"
db_password = "my_secret_password"
```

The password is appended to the connection automatically. If the
connection string already contains a password, the `db_password`
value takes precedence.

### Config File Location

All tools use `~/.config/kwi/config.toml`:

- **Linux/macOS**: `$HOME/.config/kwi/config.toml`
- **Windows**: `C:\Users\<username>\.config\kwi\config.toml`

## Verify Installation

```bash
kwi --version
kwi --help
kwi projects list
```

## MCP Server

kwi includes an MCP (Model Context Protocol) server that exposes
work item management to AI agents.

### Starting the MCP Server

```bash
kwi-mcp
```

The server runs over stdio transport. It is designed to be launched
by an MCP client (such as VS Code, Claude Desktop, or similar).

### VS Code Configuration

Add to `.vscode/settings.json`:

```json
{
  "mcp": {
    "servers": {
      "kwi": {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "/path/to/kwi", "kwi-mcp"]
      }
    }
  }
}
```

The MCP server uses the same database configuration as the CLI
(env var, config file, or default).

## Desktop GUI (kwi-ui)

### Prerequisites

- Rust 1.75+
- Node.js 18+
- System libraries (Linux): `libwebkit2gtk-4.1-dev`, `libgtk-3-dev`,
  `libayatana-appindicator3-dev`, `librsvg2-dev`

### Setup

```bash
cd kwi-ui
npm install
```

### Development

```bash
npm run tauri dev
```

### Build

```bash
# Linux
npm run tauri build

# Cross-compile for Windows (requires cross-compilation toolchain)
npm run tauri build -- --target x86_64-pc-windows-gnu
```

### Configuration

The GUI uses the same config file as the CLI:

1. **Environment variable**: `KWI_DATABASE_URL`
2. **Config file**: `~/.config/kwi/config.toml`

The GUI does not support a `--db-url` CLI flag.

## Development

```bash
# Python tests
uv run pytest -v

# Python lint and format
uv run ruff format .
uv run ruff check .

# Python type check
ty check

# Rust (kwi-ui backend)
cd kwi-ui/src-tauri
cargo fmt --check
cargo clippy -- -D warnings
cargo test

# Svelte (kwi-ui frontend)
cd kwi-ui
npx svelte-check --threshold error
```
