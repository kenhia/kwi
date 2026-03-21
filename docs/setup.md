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

## Verify Installation

```bash
kwi --version
kwi --help
kwi projects list
```

## Development

```bash
# Run tests
uv run pytest -v

# Lint and format
uv run ruff format .
uv run ruff check .

# Type check
ty check
```
