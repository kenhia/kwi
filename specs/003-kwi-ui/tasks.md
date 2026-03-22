# Tasks: kwi Desktop GUI

**Input**: Design documents from `/specs/003-kwi-ui/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/tauri-commands.md, quickstart.md

**Tests**: TDD is mandatory per constitution (Principle III). Test tasks are included for each phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Rust backend**: `kwi-ui/src-tauri/src/`
- **Svelte frontend**: `kwi-ui/src/`
- **Frontend components**: `kwi-ui/src/components/`
- **Frontend lib**: `kwi-ui/src/lib/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Tauri 2 / Svelte 5 project with all dependencies

- [x] T001 Initialize Tauri 2 project with Svelte 5 template in `kwi-ui/` via `npm create tauri-app@latest`
- [x] T002 Add Rust dependencies (tokio-postgres, deadpool-postgres, serde, toml, serde_json) to `kwi-ui/src-tauri/Cargo.toml`
- [x] T003 [P] Add frontend dependencies (marked, @types/marked) to `kwi-ui/package.json`
- [x] T004 [P] Configure pre-commit checks: cargo fmt/clippy in `kwi-ui/src-tauri/`, prettier/eslint/svelte-check in `kwi-ui/`
- [x] T005 [P] Create TypeScript interfaces for all entities (Project, Area, WorkItem, RelatedItem, RefData) in `kwi-ui/src/lib/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database connection layer and Rust models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [x] T006 [P] Write Rust unit test for config file parsing (reads `database_url` from TOML, env var fallback) in `kwi-ui/src-tauri/src/db.rs` (test module)
- [x] T007 [P] Write Rust unit test for `models.rs` struct serialization/deserialization in `kwi-ui/src-tauri/src/models.rs` (test module)

### Implementation for Foundation

- [x] T008 Implement config reading and connection pool setup in `kwi-ui/src-tauri/src/db.rs` — read `~/.config/kwi/config.toml`, fall back to `KWI_DATABASE_URL` env var, create `deadpool_postgres::Pool`
- [x] T009 Define all Rust model structs (Project, Area, WorkItem, RelatedItem, RefData) with Serialize/Deserialize in `kwi-ui/src-tauri/src/models.rs`
- [x] T010 [P] Create Tauri invoke wrapper functions for all commands in `kwi-ui/src/lib/commands.ts`
- [x] T011 Implement app state management scaffolding with Svelte 5 runes in `kwi-ui/src/lib/stores.ts` — selected project, work item list, current view
- [x] T012 Wire `db::Pool` into Tauri app state and register empty command stubs in `kwi-ui/src-tauri/src/main.rs`

**Checkpoint**: `npm run tauri dev` launches, connects to database, all Tauri command stubs registered

---

## Phase 3: User Story 1 — Browse Projects and Work Items (Priority: P1) 🎯 MVP

**Goal**: Launch the app, see projects in sidebar, browse work items in a table, view details with rendered markdown

**Independent Test**: Launch the app, select a project from the sidebar, see a filtered list of work items, click one to view its full details

### Tests for User Story 1

- [x] T013 [P] [US1] Write Rust tests for `list_projects` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T014 [P] [US1] Write Rust tests for `list_work_items` query function with filters (project, area, type, status, show_archived) in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T015 [P] [US1] Write Rust tests for `get_work_item` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T016 [P] [US1] Write Rust tests for `list_areas` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T017 [P] [US1] Write Rust tests for `get_valid_types`, `get_valid_statuses`, and `get_valid_tshirt_sizes` query functions in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T018 [P] [US1] Write Svelte component test for ProjectSelector (renders project list, emits selection) in `kwi-ui/src/components/ProjectSelector.test.ts`

### Implementation for User Story 1

- [x] T019 [P] [US1] Implement `list_projects`, `list_areas`, `get_valid_types`, `get_valid_statuses`, `get_valid_tshirt_sizes` (hardcoded XS/S/M/L/XL) query functions in `kwi-ui/src-tauri/src/queries.rs`
- [x] T020 [P] [US1] Implement `list_work_items` query function with optional filters (project_id, area_id, wi_type, wi_status, show_archived) in `kwi-ui/src-tauri/src/queries.rs`
- [x] T021 [US1] Implement `get_work_item` query function in `kwi-ui/src-tauri/src/queries.rs`
- [x] T022 [US1] Implement `#[tauri::command]` handlers for `list_projects`, `list_areas`, `list_work_items`, `get_work_item`, `get_valid_types`, `get_valid_statuses`, `get_valid_tshirt_sizes` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T023 [US1] Register US1 commands in `kwi-ui/src-tauri/src/main.rs`
- [x] T024 [US1] Build `ProjectSelector.svelte` — sidebar component listing projects alphabetically, emitting selected project in `kwi-ui/src/components/ProjectSelector.svelte`
- [x] T025 [US1] Build `WorkItemList.svelte` — table with columns (ID, area, type, status, t-shirt, sprint, title), filter controls for area/status/type/t-shirt/sprint, "include archived" toggle in `kwi-ui/src/components/WorkItemList.svelte`
- [x] T026 [US1] Build `WorkItemDetail.svelte` — read-only detail view with markdown rendering via `marked` for content and details fields in `kwi-ui/src/components/WorkItemDetail.svelte`
- [x] T027 [US1] Wire `App.svelte` layout: sidebar (ProjectSelector) + main panel (WorkItemList or WorkItemDetail) with navigation; re-fetch data on navigation to ensure freshness in `kwi-ui/src/App.svelte`
- [x] T028 [US1] Implement connection error screen — display clear message with config instructions when database is unreachable in `kwi-ui/src/App.svelte`

**Checkpoint**: User can launch app, see projects, browse work items with filtering, view details with rendered markdown. US1 is independently functional.

---

## Phase 4: User Story 2 — Create Work Items (Priority: P1)

**Goal**: Create new work items through a form with dropdown menus and validation

**Independent Test**: Open create form, fill in required and optional fields, submit, verify new item appears in list

### Tests for User Story 2

- [x] T029 [P] [US2] Write Rust tests for `create_work_item` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T030 [P] [US2] Write Svelte component test for WorkItemForm in create mode (renders fields, validates required, submits) in `kwi-ui/src/components/WorkItemForm.test.ts`

### Implementation for User Story 2

- [x] T031 [US2] Implement `create_work_item` query function in `kwi-ui/src-tauri/src/queries.rs`
- [x] T032 [US2] Implement `#[tauri::command]` handler for `create_work_item` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T033 [US2] Register `create_work_item` command in `kwi-ui/src-tauri/src/main.rs`
- [x] T034 [US2] Build `WorkItemForm.svelte` — form with project (pre-filled), title, content (textarea), type/status dropdowns (populated via `get_valid_types`/`get_valid_statuses`), t-shirt size dropdown (hardcoded XS/S/M/L/XL), area dropdown, sprint text input, details textarea, parent ID input; inline required field validation in `kwi-ui/src/components/WorkItemForm.svelte`
- [x] T035 [US2] Wire "New Work Item" button in WorkItemList to open WorkItemForm in create mode, refresh list on success in `kwi-ui/src/components/WorkItemList.svelte`

**Checkpoint**: User can create work items via form and see them in the list. US1 + US2 are both functional. MVP complete.

---

## Phase 5: User Story 3 — Edit Work Items (Priority: P1)

**Goal**: Edit existing work items with pre-populated form, save changes

**Independent Test**: Open a work item, click Edit, modify fields, save, verify changes persist

### Tests for User Story 3

- [x] T036 [P] [US3] Write Rust tests for `update_work_item` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T037 [P] [US3] Write Svelte component test for WorkItemForm in edit mode (pre-populates fields, submits updates) in `kwi-ui/src/components/WorkItemForm.test.ts`

### Implementation for User Story 3

- [x] T038 [US3] Implement `update_work_item` query function in `kwi-ui/src-tauri/src/queries.rs`
- [x] T039 [US3] Implement `#[tauri::command]` handler for `update_work_item` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T040 [US3] Register `update_work_item` command in `kwi-ui/src-tauri/src/main.rs`
- [x] T041 [US3] Add edit mode to `WorkItemForm.svelte` — pre-populate with current values, submit as update in `kwi-ui/src/components/WorkItemForm.svelte`
- [x] T042 [US3] Wire "Edit" button in WorkItemDetail to open WorkItemForm in edit mode, refresh detail on save, handle Cancel in `kwi-ui/src/components/WorkItemDetail.svelte`

**Checkpoint**: User can edit any work item field and see changes immediately. US1-US3 functional.

---

## Phase 6: User Story 4 — Archive Work Items (Priority: P2)

**Goal**: Archive work items with confirmation, hide from default list, show with toggle

**Independent Test**: Select a work item, archive it, verify it disappears from list, toggle "include archived" to see it

### Tests for User Story 4

- [x] T043 [P] [US4] Write Rust tests for `archive_work_item` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)

### Implementation for User Story 4

- [x] T044 [US4] Implement `archive_work_item` query function in `kwi-ui/src-tauri/src/queries.rs`
- [x] T045 [US4] Implement `#[tauri::command]` handler for `archive_work_item` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T046 [US4] Register `archive_work_item` command in `kwi-ui/src-tauri/src/main.rs`
- [x] T047 [US4] Add "Archive" button with confirmation prompt to WorkItemDetail and WorkItemList row actions in `kwi-ui/src/components/WorkItemDetail.svelte` and `kwi-ui/src/components/WorkItemList.svelte`
- [x] T048 [US4] Add visual indicator for archived items when "include archived" is enabled in `kwi-ui/src/components/WorkItemList.svelte`

**Checkpoint**: Archive workflow complete. Archived items hidden by default, viewable with toggle. US1-US4 functional.

---

## Phase 7: User Story 5 — Manage Relationships (Priority: P2)

**Goal**: View, add, and remove relationships between work items

**Independent Test**: Navigate to a work item, add a relationship to another item, see it listed, remove it

### Tests for User Story 5

- [x] T049 [P] [US5] Write Rust tests for `list_related`, `relate_work_items`, `unrelate_work_items` query functions in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T050 [P] [US5] Write Svelte component test for RelationshipPanel (renders list, add/remove actions) in `kwi-ui/src/components/RelationshipPanel.test.ts`

### Implementation for User Story 5

- [x] T051 [US5] Implement `list_related`, `relate_work_items`, `unrelate_work_items` query functions in `kwi-ui/src-tauri/src/queries.rs`
- [x] T052 [US5] Implement `#[tauri::command]` handlers for `list_related`, `relate_work_items`, `unrelate_work_items` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T053 [US5] Register relationship commands in `kwi-ui/src-tauri/src/main.rs`
- [x] T054 [US5] Build `RelationshipPanel.svelte` — list related items with labels, "Add Relationship" form (search/select work item + label), "Remove" with confirmation in `kwi-ui/src/components/RelationshipPanel.svelte`
- [x] T055 [US5] Embed RelationshipPanel in WorkItemDetail view, wire click-through navigation to related items in `kwi-ui/src/components/WorkItemDetail.svelte`

**Checkpoint**: Relationships viewable, addable, removable. Click-through navigation works. US1-US5 functional.

---

## Phase 8: User Story 6 — Search Work Items (Priority: P2)

**Goal**: Full-text search across work item titles and content within selected project

**Independent Test**: Enter a search term, see matching work items, click one to view details

### Tests for User Story 6

- [x] T056 [P] [US6] Write Rust tests for `search_work_items` query function in `kwi-ui/src-tauri/src/queries.rs` (test module)
- [x] T057 [P] [US6] Write Svelte component test for SearchBar (emits query, displays results) in `kwi-ui/src/components/SearchBar.test.ts`

### Implementation for User Story 6

- [x] T058 [US6] Implement `search_work_items` query function in `kwi-ui/src-tauri/src/queries.rs`
- [x] T059 [US6] Implement `#[tauri::command]` handler for `search_work_items` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T060 [US6] Register `search_work_items` command in `kwi-ui/src-tauri/src/main.rs`
- [x] T061 [US6] Build `SearchBar.svelte` — text input with search results list, "no results" message in `kwi-ui/src/components/SearchBar.svelte`
- [x] T062 [US6] Integrate SearchBar into App.svelte layout, wire result clicks to WorkItemDetail navigation in `kwi-ui/src/App.svelte`

**Checkpoint**: Search works within project scope. US1-US6 functional.

---

## Phase 9: User Story 7 — Manage Projects and Areas (Priority: P3)

**Goal**: Create projects and areas through the GUI

**Independent Test**: Create a new project via form, create an area under it, verify both appear in sidebar

### Tests for User Story 7

- [x] T063 [P] [US7] Write Rust tests for `create_project` and `create_area` query functions in `kwi-ui/src-tauri/src/queries.rs` (test module)

### Implementation for User Story 7

- [x] T064 [US7] Implement `create_project` and `create_area` query functions in `kwi-ui/src-tauri/src/queries.rs`
- [x] T065 [US7] Implement `#[tauri::command]` handlers for `create_project` and `create_area` in `kwi-ui/src-tauri/src/commands.rs`
- [x] T066 [US7] Register `create_project` and `create_area` commands in `kwi-ui/src-tauri/src/main.rs`
- [x] T067 [US7] Add "Add Project" button and form to ProjectSelector sidebar (short name, cn_path, optional gh_repo, optional description), inline validation for required fields and duplicate name errors in `kwi-ui/src/components/ProjectSelector.svelte`
- [x] T068 [US7] Add area management UI — "Add Area" form accessible from project context (name, optional description), inline validation for required fields and duplicate name error handling in `kwi-ui/src/components/ProjectSelector.svelte`

**Checkpoint**: Projects and areas creatable from GUI. All 7 user stories functional.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, error handling, and final quality pass

- [x] T069 [P] Add keyboard navigation for all interactive elements (tab order, Enter to select, Escape to close) across all components in `kwi-ui/src/components/`
- [x] T070 [P] Add loading states (spinners/skeletons) for async operations in `kwi-ui/src/components/WorkItemList.svelte`, `WorkItemDetail.svelte`
- [x] T071 [P] Add semantic HTML (proper headings, landmarks, aria-labels) across all components in `kwi-ui/src/components/`
- [x] T072 Responsive layout — sidebar collapse/scroll on narrow windows in `kwi-ui/src/App.svelte`
- [x] T073 Run `quickstart.md` validation — verify all setup, dev, build, and test commands work end-to-end
- [x] T074 Run full pre-commit gate: `cargo fmt --check && cargo clippy -- -D warnings && cargo test` and `npm run format -- --check && npm run lint && npm run check && npm run test`
- [x] T075 [P] Update `docs/architecture.md` with Tauri 2 / Svelte 5 architecture, IPC command pattern, and project structure
- [x] T076 [P] Update `docs/specification.md` with GUI feature specification content from `specs/003-kwi-ui/spec.md`
- [x] T077 [P] Update `docs/setup.md` with Tauri prerequisites (Rust, Node, system libs) and GUI build instructions for Linux and Windows
- [x] T078 [P] Update `docs/usage.md` with GUI workflows (browse, create, edit, archive, search, relationships)
- [x] T079 Verify SC-005: application launches and displays project list within 3 seconds on standard desktop
- [x] T080 Verify SC-006: application handles 1,000+ work items per project without noticeable lag in list rendering or filtering

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - US1 (P1): No dependencies on other stories
  - US2 (P1): No dependencies on other stories (WorkItemForm is new)
  - US3 (P1): Depends on US2 (reuses WorkItemForm in edit mode)
  - US4 (P2): No dependencies on other stories
  - US5 (P2): No dependencies on other stories (RelationshipPanel is new)
  - US6 (P2): No dependencies on other stories (SearchBar is new)
  - US7 (P3): No dependencies on other stories
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per constitution)
- Query functions before command handlers
- Command handlers before frontend components
- Register commands before frontend can invoke them

### Parallel Opportunities

- T003, T004, T005 can run in parallel (different files)
- T006, T007 can run in parallel (different test modules)
- T010 can run in parallel with Rust implementation
- All test tasks within a story marked [P] can run in parallel
- US1 and US2 can proceed in parallel after Phase 2
- US4, US5, US6, US7 can all proceed in parallel after Phase 2
- T069, T070, T071 can run in parallel (different components)
- T075, T076, T077, T078 can run in parallel (different doc files)

---

## Parallel Example: User Story 1

```text
# Write all US1 tests in parallel:
T013: Rust test for list_projects
T014: Rust test for list_work_items with filters
T015: Rust test for get_work_item
T016: Rust test for list_areas
T017: Rust test for get_valid_types/get_valid_statuses/get_valid_tshirt_sizes
T018: Svelte test for ProjectSelector

# Then implement query functions in parallel:
T019: list_projects, list_areas, get_valid_types, get_valid_statuses, get_valid_tshirt_sizes
T020: list_work_items with filters

# Then sequentially:
T021 → T022 → T023 → T024 → T025 → T026 → T027 → T028
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 — Browse
4. Complete Phase 4: User Story 2 — Create
5. **STOP and VALIDATE**: User can browse and create work items — MVP complete
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Browse) → Test independently → MVP read-only
3. US2 (Create) → Test independently → MVP complete
4. US3 (Edit) → Test independently → Core CRUD complete
5. US4 (Archive) → Test independently → Housekeeping
6. US5 (Relationships) → Test independently → Work item graph
7. US6 (Search) → Test independently → Discovery
8. US7 (Projects/Areas) → Test independently → Full self-service
9. Polish → Final quality pass
