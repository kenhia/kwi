# Research: kwi Desktop GUI

**Date**: 2026-03-21
**Feature**: 003-kwi-ui

## Decision 1: Rust PostgreSQL Driver

**Decision**: `tokio-postgres` (via `deadpool-postgres` for pooling)

**Rationale**: Tauri 2 uses `tokio` as its async runtime. `tokio-postgres`
is the native async PostgreSQL driver for tokio. It provides direct SQL
execution (no ORM), which matches the project's philosophy of raw SQL
(Principle VII). `deadpool-postgres` adds lightweight connection pooling
suitable for a desktop app.

**Alternatives considered**:
- `sqlx`: Compile-time SQL checking is nice but adds build complexity
  (requires a live DB or `sqlx-data.json` offline). Overkill for a
  personal desktop app.
- `diesel`: Full ORM, heavy macro usage, sync-only. Doesn't align with
  Tauri's async model or the project's raw-SQL approach.

## Decision 2: Config File Parsing (Rust)

**Decision**: `toml` crate for parsing `~/.config/kwi/config.toml`

**Rationale**: The config file is TOML format. The `toml` crate is the
standard Rust TOML parser, well-maintained, and derives directly into
Rust structs via serde. Minimal code to read `database_url` from the
config file.

**Alternatives considered**:
- Custom parser: Unnecessary complexity for a simple key-value file.
- `config` crate: Feature-rich configuration library. Overkill — we
  only need to read one field from one file with env var fallback.

## Decision 3: Markdown Rendering

**Decision**: `marked` (JavaScript library) in the Svelte frontend

**Rationale**: Markdown content and details fields need to be rendered
as HTML in the detail view. `marked` is a fast, widely-used JavaScript
markdown parser that runs in the browser. Since rendering happens in
the frontend webview, a JavaScript library is the natural choice.
No need for a Rust-side markdown parser.

**Alternatives considered**:
- `markdown-it`: Slightly heavier, more extensible. Not needed for
  basic markdown rendering.
- Rust-side rendering (`pulldown-cmark`): Would require passing HTML
  strings over IPC instead of markdown. Adds complexity without benefit.

## Decision 4: Frontend State Management

**Decision**: Svelte 5 runes (`$state`, `$derived`) with simple stores

**Rationale**: Svelte 5's built-in reactivity system (runes) handles
component-level state elegantly. For cross-component state (selected
project, work item list), simple writable stores in `stores.ts` suffice.
No external state management library needed for a single-user desktop app.

**Alternatives considered**:
- Svelte stores (Svelte 4 style): Still work in Svelte 5 but runes are
  the recommended approach.
- Redux/Zustand patterns: Massive overkill for a personal app with <10
  views and no concurrent users.

## Decision 5: CSS Approach

**Decision**: Plain CSS with Svelte scoped styles

**Rationale**: Svelte's built-in `<style>` blocks provide automatic
scoping. For a personal desktop app with a small number of components,
no CSS framework is needed. Plain CSS keeps the build simple and avoids
adding dependencies (Principle VII).

**Alternatives considered**:
- Tailwind CSS: Adds build complexity and a learning curve for class-based
  styling. Not worth it for ~10 components.
- Component library (e.g., Skeleton UI): Pre-built components would speed
  up development but add a large dependency and reduce control.

## Decision 6: Tauri IPC Pattern

**Decision**: One Tauri command per database operation, returning
JSON-serializable Rust structs

**Rationale**: Each command maps 1:1 to a query function (e.g.,
`list_projects`, `get_work_item`). Commands return `Result<T, String>`
where `T` is a serde-serializable struct. Errors are returned as
descriptive strings. This keeps the interface thin and predictable.

**Alternatives considered**:
- Single "query" command with a discriminator: More flexible but
  loses type safety and makes the API harder to understand.
- GraphQL-like batching: Completely unnecessary for a local desktop app
  with no network latency.
