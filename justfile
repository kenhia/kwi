# kwi — top-level development commands
#
# Python (kwi library / CLI / MCP) recipes run from the repo root.
# UI recipes delegate into kwi-ui/ (its own justfile drives Tauri + Svelte).
# Run `just` with no arguments to list available recipes.

# Show available recipes
default:
    @just --list

# --- Python: kwi library, CLI, and MCP server ---

# Format Python sources with ruff
fmt:
    uv run ruff format

# Check Python formatting without writing
fmt-check:
    uv run ruff format --check

# Lint with ruff
lint:
    uv run ruff check

# Auto-fix lint issues where possible
lint-fix:
    uv run ruff check --fix

# Type-check with ty
typecheck:
    uv run ty check

# Run the Python test suite
test:
    uv run --with pytest python -m pytest

# Run the Python tests quietly
test-quiet:
    uv run --with pytest python -m pytest -q

# Run all Python CI gates in sequence (format, lint, types, tests)
check: fmt-check lint typecheck test

# Run the CLI (pass args after --, e.g. `just cli -- work list --project kwi`)
cli *ARGS:
    uv run kwi {{ARGS}}

# Run the MCP server over stdio
mcp:
    uv run kwi-mcp

# --- Database migrations ---

# Apply all migrations to a database (default: local workitems)
# Usage: just migrate            (uses DB below)
#        just migrate DB=workitems_test
migrate DB="workitems" HOST="gratch" USER="ken":
    #!/usr/bin/env bash
    set -euo pipefail
    for f in migrations/*.sql; do
        echo "Applying $f ..."
        psql -h {{HOST}} -U {{USER}} -d {{DB}} -f "$f"
    done

# --- UI: kwi-ui (Tauri + Svelte) ---

# Start the Tauri dev server
ui-dev:
    cd kwi-ui && just dev

# Run the Svelte/Vitest UI tests
ui-test:
    cd kwi-ui && just test

# Run all UI pre-commit checks (prettier, eslint, svelte-check, vitest, rust fmt/clippy)
ui-check:
    cd kwi-ui && just precommit

# Build the Linux desktop app frontend bundle
ui-build:
    cd kwi-ui && just build

# Cross-compile the Windows UI executable (.exe) via x86_64-pc-windows-gnu
build-win-ui:
    cd kwi-ui && just winrelease

# --- Aggregate ---

# Run every CI gate across Python and the UI
check-all: check ui-check
