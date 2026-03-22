# kwi Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-21

## Active Technologies
- Python 3.12+ + mcp (Python MCP SDK), psycopg3 (via existing kwi package) (002-kwi-mcp)
- PostgreSQL (existing `workitems` database, no schema changes) (002-kwi-mcp)

- Python 3.12+ (managed by uv) + typer (CLI framework), psycopg[binary] (PostgreSQL driver), rich (table formatting), tomli (TOML config parsing on <3.11), pyyaml (frontmatter parsing) (001-kwi-db-cli)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12+ (managed by uv): Follow standard conventions

## Recent Changes
- 003-kwi-ui: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 002-kwi-mcp: Added Python 3.12+ + mcp (Python MCP SDK), psycopg3 (via existing kwi package)

- 001-kwi-db-cli: Added Python 3.12+ (managed by uv) + typer (CLI framework), psycopg[binary] (PostgreSQL driver), rich (table formatting), tomli (TOML config parsing on <3.11), pyyaml (frontmatter parsing)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
