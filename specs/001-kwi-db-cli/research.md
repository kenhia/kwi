# Research: kwi Database Schema & CLI

**Date**: 2026-03-21
**Feature**: 001-kwi-db-cli

## R1: Python CLI Framework — Typer

**Decision**: Use Typer for CLI command structure.

**Rationale**: Typer provides declarative command/subcommand
definition via type annotations, auto-generated help, and built-in
support for nested command groups (`projects`, `work`, `areas`).
It wraps Click under the hood but offers a cleaner API. Pairs
naturally with Rich for table output.

**Alternatives considered**:
- **Click**: More verbose; Typer is built on Click and adds
  type-hint-driven convenience.
- **argparse**: Standard library but requires more boilerplate for
  nested subcommands and lacks Rich integration.
- **Fire**: Auto-generates CLI from functions/classes but offers
  less control over help text and validation.

## R2: PostgreSQL Driver — psycopg 3

**Decision**: Use psycopg (v3) with binary extras.

**Rationale**: Direct SQL access matches the raw-SQL migration
strategy (no ORM model layer to keep in sync). psycopg3 supports
both sync and async modes from the same package, which allows the
shared DB layer to be reused by `kwi-mcp` (Spec 002) without
switching libraries. Connection pooling is built in. Parameterized
queries protect against SQL injection.

**Alternatives considered**:
- **SQLAlchemy Core**: Adds a query-builder layer on top of SQL;
  unnecessary when queries are straightforward and hand-written.
- **SQLAlchemy ORM**: Full object mapping adds significant
  complexity for a simple schema with known queries.
- **asyncpg**: Async-only; the CLI is synchronous, so this would
  require running an event loop for every command.

## R3: Frontmatter Parsing for `work add`

**Decision**: Use `python-frontmatter` library for parsing YAML
frontmatter in markdown files.

**Rationale**: The `kwi work add` command reads a markdown file
with YAML frontmatter (delimited by `---`). `python-frontmatter`
handles this pattern exactly — it parses the YAML metadata and
separates the body content. This is more reliable than hand-rolling
a parser.

**Alternatives considered**:
- **PyYAML + manual split**: Would work but requires reimplementing
  the frontmatter delimiter detection that `python-frontmatter`
  already handles correctly.
- **ruyaml**: YAML parser only; doesn't handle the frontmatter
  pattern (metadata + body separation).

**Note**: `python-frontmatter` depends on PyYAML internally, so
PyYAML is an indirect dependency either way.

## R4: Configuration File Format — TOML

**Decision**: Use TOML for `~/.config/kwi/config.toml`.

**Rationale**: TOML is the standard config format in the Python
ecosystem (pyproject.toml). Python 3.11+ includes `tomllib` in the
standard library. For 3.10 compatibility, `tomli` is a zero-dep
fallback. The config is minimal (just `database_url`), so TOML's
simplicity is a good fit.

**Config file structure**:
```toml
database_url = "postgresql://user:pass@gratch:5432/workitems"
```

**Alternatives considered**:
- **JSON**: No comments support; awkward for config files.
- **YAML**: Heavier dependency, more complex than needed for a flat
  config.
- **INI**: Less standardized in the Python ecosystem than TOML.

## R5: Output Rendering — Rich

**Decision**: Use Rich for table output, with a JSON serializer for
`--json` mode.

**Rationale**: The constitution (Principle VI) requires consistent
CLI formatting via Rich, errors to stderr, and JSON output for
programmatic use. Rich provides `Table` and `Console` classes that
handle terminal width, color, and `NO_COLOR` environment variable
support out of the box.

**JSON output**: Use Python's built-in `json` module. Each command's
output function checks the global `--json` flag and either renders
a Rich table or prints JSON to stdout.

**Error output**: Errors go to stderr via `Console(stderr=True)`.
In JSON mode, errors are formatted as
`{"error": "message", "code": "ERROR_CODE"}`.

## R6: Database Migration Strategy

**Decision**: Raw SQL scripts in `migrations/` directory, applied
manually via `psql`.

**Rationale**: Single-user personal project with a well-defined
up-front schema. No need for migration tooling overhead. Files are
numbered sequentially (`001_initial_schema.sql`, etc.) and can be
applied with `psql -f migrations/001_initial_schema.sql`.

**Idempotency**: The initial migration uses `CREATE TABLE IF NOT
EXISTS` and `INSERT ... ON CONFLICT DO NOTHING` to allow safe
re-application.

**Future**: If migration complexity grows, a `kwi db migrate`
wrapper can be added later.

## R7: Project Layout and Packaging

**Decision**: Single `src/kwi/` package managed by `uv` with
`pyproject.toml`.

**Rationale**: `uv` manages the virtual environment and
dependencies. The package is installable via `uv pip install -e .`
(or `uv sync` with a workspace) which makes the `kwi` entry point
available. Typer's CLI entry point is defined in `pyproject.toml`
under `[project.scripts]`.

**Entry point**:
```toml
[project.scripts]
kwi = "kwi.main:app"
```

**Shared code for Spec 002**: The `kwi.db`, `kwi.models`, and
`kwi.queries` modules contain no CLI-specific logic and can be
imported by `kwi-mcp` directly. Whether to extract a separate
`kwi-core` package will be decided during Spec 002 planning.

## R8: Testing Strategy

**Decision**: pytest with `typer.testing.CliRunner` for CLI tests,
real PostgreSQL for integration tests.

**Rationale**: CliRunner captures stdout/stderr and exit codes,
enabling end-to-end CLI testing without subprocesses. Database
tests use a test database (either a dedicated test DB or
`pytest-postgresql` for ephemeral instances).

**Test categories**:
- **Unit tests**: Models, output formatting, config resolution,
  frontmatter parsing — no DB required.
- **Integration tests**: Query functions against a real PostgreSQL
  instance with test data.
- **CLI tests**: Full command invocations via CliRunner, verifying
  output format and exit codes.

## R9: Connection Config Precedence

**Decision**: Flag > environment variable > config file.

**Implementation approach**:
1. Typer callback checks `--db-url` flag.
2. If not set, check `KWI_DATABASE_URL` environment variable.
3. If not set, read `~/.config/kwi/config.toml` for `database_url`.
4. If none found, print error to stderr listing all three options.

The resolved URL is stored in a Typer context object and passed to
the `db.get_connection()` function.
