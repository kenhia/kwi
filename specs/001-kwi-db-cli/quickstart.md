# Quickstart: kwi CLI

Get from zero to tracking work items in 5 minutes.

## Prerequisites

- Python 3.12+
- `uv` (Python package manager)
- PostgreSQL server accessible (e.g., `gratch:5432`)
- `psql` (PostgreSQL client) for applying migrations

## 1. Clone and Install

```bash
git clone https://github.com/you/kwi.git
cd kwi
uv sync
```

## 2. Configure Database Connection

Set your database URL using one of these methods (in priority
order):

**Option A — Environment variable** (recommended for getting
started):
```bash
export KWI_DATABASE_URL="postgresql://user:pass@gratch:5432/workitems"
```

**Option B — Config file**:
```bash
mkdir -p ~/.config/kwi
cat > ~/.config/kwi/config.toml << 'EOF'
database_url = "postgresql://user:pass@gratch:5432/workitems"
EOF
```

**Option C — Per-command flag**:
```bash
kwi --db-url "postgresql://user:pass@gratch:5432/workitems" projects list
```

## 3. Apply the Database Migration

```bash
psql "$KWI_DATABASE_URL" -f migrations/001_initial_schema.sql
```

This creates all tables and seeds the type/status reference data.

## 4. Create a Project

```bash
kwi projects add --name kwi --path "~/src/kwi" --description "Ken's Work Items"
```

## 5. Create a Work Item

Generate a template:
```bash
kwi work template my-first-item.md
```

Edit the file, then add it:
```bash
kwi work add my-first-item.md
```

## 6. List Work Items

```bash
kwi work list --project kwi
```

Filter by status:
```bash
kwi work list --project kwi --status open,active
```

## 7. Update and Archive

```bash
kwi work set 1 --status active --sprint "001-kwi-db-cli"
kwi work archive 1
```

## JSON Output

Add `--json` before any subcommand for machine-readable output:
```bash
kwi --json work list --project kwi
```

## Next Steps

- Create areas: `kwi areas add --project kwi --name backend`
- Link items: `kwi work relate 1 2 --relationship "blocks"`
- See all commands: `kwi --help`
