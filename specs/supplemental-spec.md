# Supplemental Specification

Ad-hoc changes that fall outside an active iteration spec.

---

## S001: Config file for kwi-ui not being used (WI #356)

**Type**: Bug | **Status**: Active | **Size**: S | **Sprint**: 003-kwi-ui

**Problem**: `kwi-ui` does not read `~/.config/kwi/config.toml` on Windows.
The config file exists at `C:\Users\kenhi\.config\kwi\config.toml` with a
valid `database_url`, but kwi-ui reports "No database URL configured."

**Root Cause**: `dirs::config_dir()` returns `AppData\Roaming` on Windows,
but the Python CLI uses `Path.home() / ".config"`. User placed config at
`~/.config/kwi/config.toml` which kwi-ui wasn't finding.

**Fix**: Changed `config_file_path()` to use `dirs::home_dir().join(".config")`
instead of `dirs::config_dir()`, matching Python CLI behavior. Error messages
now include the actual file path searched. Parser errors show the file path.

**Acceptance Criteria**:
- [x] `kwi-ui` reads `config.toml` from the platform-appropriate config directory on Windows
- [x] If config file exists but cannot be parsed, show a descriptive error (not "No database URL configured")
- [x] Existing Linux config resolution continues to work

**Tasks**:
- [x] ST001 Changed `config_file_path()` to use `home_dir()/.config/` matching Python CLI (`WI #356`)
- [x] ST002 Error messages now include the actual config path searched (`WI #356`)
- [x] ST003 Added `test_config_file_path_uses_home_dir` test verifying no AppData path (`WI #356`)

---

## S002: Config format mismatch between kwi-ui and kwi CLI (WI #357)

**Type**: Issue | **Status**: Active | **Size**: S | **Sprint**: 003-kwi-ui

**Problem**: `kwi-ui` (Rust/tokio-postgres) expects libpq key=value format:
`database_url = "host=gratch port=5432 dbname=workitems user=ken"`
while `kwi` CLI (Python/psycopg3) expects URI format:
`database_url = "postgresql://ken@gratch:5432/workitems"`

Both read from `~/.config/kwi/config.toml`, making the config
incompatible between the two tools.

**Fix**: Replaced `deadpool_postgres::Config::url` with `tokio_postgres::Config::from_str()`
which natively accepts both URI and key=value formats. Both `kwi` and `kwi-ui`
now accept either format. URI is documented as the recommended format.

**Acceptance Criteria**:
- [x] Both `kwi` and `kwi-ui` accept the same `database_url` format in `config.toml`
- [x] Either: both accept both formats (auto-detect), or one is migrated to match the other
- [x] Document the canonical format in `docs/setup.md`

**Tasks**:
- [x] ST004 Both formats accepted — URI recommended in docs (`WI #357`)
- [x] ST005 `create_pool()` now uses `tokio_postgres::Config::from_str()` for dual-format support (`WI #357`)
- [x] ST006 Added `test_create_pool_uri_format` and `test_create_pool_keyvalue_format` tests (`WI #357`)
- [x] ST007 Updated `docs/setup.md` with both formats and recommendation (`WI #357`)

---

## S003: Secure password handling for kwi-ui (WI #358)

**Type**: Issue | **Status**: Active | **Size**: S | **Sprint**: 003-kwi-ui

**Problem**: Adding `password=...` to `KWI_DATABASE_URL` env var exposes the
password in process listings and shell history. User wants a `db_password`
key in `config.toml` to keep the password in a file (with file permissions)
rather than environment variables.

**Fix**: Added `db_password: Option<String>` to `KwiConfig`. `resolve_db_url()`
now returns a `ResolvedDb` struct with the URL and optional password.
`create_pool()` applies the password via `tokio_postgres::Config::password()`.
The password is never included in error messages.

**Acceptance Criteria**:
- [x] `config.toml` supports an optional `db_password` key
- [x] If `db_password` is set, it is appended to the connection string automatically
- [x] Password in `database_url` still works (not breaking)
- [x] `db_password` is NOT logged or included in error messages

**Tasks**:
- [x] ST008 Added `db_password: Option<String>` to `KwiConfig` in `models.rs` (`WI #358`)
- [x] ST009 `resolve_db_url()` returns `ResolvedDb` with password; `create_pool()` applies it (`WI #358`)
- [x] ST010 Added `test_create_pool_with_separate_password` and `test_toml_with_db_password` tests (`WI #358`)
- [x] ST011 Updated `docs/setup.md` with `db_password` config option (`WI #358`)

---

## S004: list/search queries missing project_name (WI #359)

**Type**: Bug | **Status**: Active | **Size**: S | **Sprint**: 003-kwi-ui | **Area**: mcp

**Problem**: `list_work_items` and `search_work_items` return `project_name: null`
while `get_work_item` returns it correctly. The list/search SQL queries in
`queries.py` did not JOIN the `project` table.

**Root Cause**: `list_workitems()` and `search_work_items()` in `queries.py`
selected from `workitem w` with JOINs on `workitem_type`, `workitem_status`,
and `area`, but omitted `JOIN project p ON w.project_id = p.id`. The
`WorkItem` constructor was called without `project_name=`, leaving it at
the dataclass default of `None`.

**Fix**: Added `JOIN project p ON w.project_id = p.id` and `p.project` to
the SELECT list in both `list_workitems()` and `search_work_items()`.
Updated column index mapping in `WorkItem()` construction.

**Acceptance Criteria**:
- [x] `list_workitems()` returns `project_name` populated
- [x] `search_work_items()` returns `project_name` populated
- [x] All 109 Python tests pass
- [x] Lint clean

**Tasks**:
- [x] ST012 Added `JOIN project` and `p.project` to `list_workitems()` SELECT (`WI #359`)
- [x] ST013 Added `JOIN project` and `p.project` to `search_work_items()` SELECT (`WI #359`)
- [x] ST014 Updated column index mapping in both WorkItem constructors (`WI #359`)

---

## MCP Issues Found During Testing

| # | WI | Issue | Status |
|---|-----|-------|--------|
| ~~M001~~ | ~~#359~~ | ~~`list_work_items` and `search_work_items` return `project_name: null`~~ | Fixed |
