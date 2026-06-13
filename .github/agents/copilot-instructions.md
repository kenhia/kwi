# kwi Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-30

## Active Technologies
- Python 3.12+ + mcp (Python MCP SDK), psycopg3 (via existing kwi package) (002-kwi-mcp)
- PostgreSQL (existing `workitems` database, no schema changes) (002-kwi-mcp)
- Rust 1.75+ (Tauri backend), TypeScript/Svelte 5 (frontend) + Tauri 2.x, tokio-postgres, deadpool-postgres, serde, marked.js, @tauri-apps/api 2.x (004-kwi-ui-polish)
- PostgreSQL (existing `workitems` database); localStorage or Tauri plugin for window state (004-kwi-ui-polish)
- Python 3.12 (uv-managed); Rust (edition 2021, Tauri 2.x); TypeScript / Svelte 5 (runes) + Typer + Rich (CLI), FastMCP (MCP), psycopg 3 (Python DB), sqlx (Rust DB), SvelteKit + Vite + Vitest, Tauri 2 CLI (`tauri icon`) (005-backlog-cleanup)
- PostgreSQL (prod `workitems`, tests `workitems_test`); plain `.sql` files in `migrations/` applied in sorted order (005-backlog-cleanup)

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
- 005-backlog-cleanup: Added Python 3.12 (uv-managed); Rust (edition 2021, Tauri 2.x); TypeScript / Svelte 5 (runes) + Typer + Rich (CLI), FastMCP (MCP), psycopg 3 (Python DB), sqlx (Rust DB), SvelteKit + Vite + Vitest, Tauri 2 CLI (`tauri icon`)
- 004-kwi-ui-polish: Added Rust 1.75+ (Tauri backend), TypeScript/Svelte 5 (frontend) + Tauri 2.x, tokio-postgres, deadpool-postgres, serde, marked.js, @tauri-apps/api 2.x
- 003-kwi-ui: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
