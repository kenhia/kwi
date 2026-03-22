# Implementation Plan: kwi Desktop GUI

**Branch**: `003-kwi-ui` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)

## Summary

Build a native desktop GUI for the kwi work-item system using Tauri 2
(Rust backend) and Svelte 5 (frontend). The application connects to the
existing PostgreSQL database via tokio-postgres, exposes Tauri IPC
commands for all work-item operations, and renders a responsive UI for
browsing, creating, editing, searching, and relating work items.

## Technical Context

**Language/Version**: Rust 1.75+ (backend), TypeScript/Svelte 5 (frontend)
**Primary Dependencies**: Tauri 2.x, tokio-postgres, deadpool-postgres, serde, toml, marked.js
**Storage**: PostgreSQL (existing `workitems` database at gratch:5432)
**Testing**: cargo test (Rust), vitest + svelte-check (frontend)
**Target Platform**: Linux (x86_64) and Windows (x86_64); release builds for both, debug builds optional
**Project Type**: desktop-app
**Performance Goals**: <200ms for any list/detail view load; launch to project list within 3 seconds
**Constraints**: Must read `~/.config/kwi/config.toml` for DB config; offline-tolerant (graceful errors)
**Scale/Scope**: Single-user desktop app, ~10 screens/views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| 1 | Spec-Driven Development | PASS | spec.md created and validated first |
| 2 | Architecture First | PASS | Plan defines Tauri/Svelte split, IPC contracts, data model |
| 3 | Test-Driven Development | PASS | cargo test + vitest configured; tests written per phase |
| 4 | Code Standards Gate | PASS | Pre-commit: cargo fmt/clippy, prettier/eslint/svelte-check |
| 5 | User Documentation Day One | PASS | quickstart.md created in Phase 1 |
| 6 | Quality and Accessibility | PASS | Keyboard navigation and semantic HTML planned |
| 7 | Simplicity | PASS | Single Tauri project, no extra abstractions |

## Project Structure

### Documentation (this feature)

```text
specs/003-kwi-ui/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── tauri-commands.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
kwi-ui/
├── package.json
├── vite.config.ts
├── svelte.config.js
├── tsconfig.json
├── src/
│   ├── app.html
│   ├── App.svelte
│   ├── main.ts
│   ├── lib/
│   │   ├── types.ts          # TypeScript interfaces
│   │   ├── commands.ts       # Tauri invoke wrappers
│   │   └── stores.ts         # Svelte 5 state (runes)
│   └── components/
│       ├── WorkItemList.svelte
│       ├── WorkItemDetail.svelte
│       ├── WorkItemForm.svelte
│       ├── ProjectSelector.svelte
│       ├── SearchBar.svelte
│       └── RelationshipPanel.svelte
└── src-tauri/
    ├── Cargo.toml
    ├── tauri.conf.json
    └── src/
        ├── main.rs           # Tauri setup + command registration
        ├── db.rs             # Connection pool + config reading
        ├── models.rs         # Rust structs (serde)
        ├── commands.rs       # #[tauri::command] handlers
        └── queries.rs        # SQL query functions
```

**Structure Decision**: Single Tauri project at `kwi-ui/`. Rust backend in
`src-tauri/`, Svelte frontend in `src/`. No monorepo tooling needed — Tauri's
built-in Vite integration handles both sides.

## Implementation Phases

### Phase 1: Scaffolding and Config

- Initialize Tauri 2 project via `npm create tauri-app@latest`
- Configure `Cargo.toml` with tokio-postgres, deadpool-postgres, serde, toml
- Implement `db.rs`: read `config.toml`, create connection pool
- Write unit test for config parsing
- Verify `npm run tauri dev` launches empty window

### Phase 2: Database Layer and Models

- Define Rust structs in `models.rs`
- Implement `queries.rs` with all SQL functions (mirroring Python `queries.py`)
- Implement `commands.rs` with `#[tauri::command]` wrappers
- Register commands in `main.rs`
- Write Rust tests for query functions (against test database)
- Define TypeScript interfaces in `types.ts`
- Create `commands.ts` invoke wrappers

### Phase 3: Browse and Detail Views

- Build `WorkItemList.svelte` — table view with filtering
- Build `ProjectSelector.svelte` — project/area dropdown
- Build `WorkItemDetail.svelte` — read-only detail with markdown rendering
- Implement `stores.ts` with Svelte 5 runes for app state
- Wire list → detail navigation
- Write component tests with vitest

### Phase 4: Create and Edit

- Build `WorkItemForm.svelte` — create/edit form with validation
- Wire form submission to Tauri commands
- Handle success/error feedback
- Test create and update flows

### Phase 5: Relationships and Search

- Build `RelationshipPanel.svelte` — display and manage related items
- Build `SearchBar.svelte` — full-text search with results
- Wire to relate/unrelate/search commands
- Test relationship and search flows

### Phase 6: Polish and Accessibility

- Keyboard navigation for all interactive elements
- Loading states and error boundaries
- Archive workflow (unarchive is done via the edit form — change status from "archived" to another value)
- Responsive layout adjustments
- Final round of integration testing
