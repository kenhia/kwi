# Tasks: KWI-UI Interface Polish

**Input**: Design documents from `/specs/004-kwi-ui-polish/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution TDD requirement. vitest + @testing-library/svelte for component tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Configure the test infrastructure that doesn't exist yet, and prepare the project for component-level changes.

- [x] T001 Create vitest configuration file at kwi-ui/vitest.config.ts with jsdom environment, Svelte plugin, and component test setup
- [x] T002 Create a vitest setup file at kwi-ui/src/test-setup.ts with @testing-library/jest-dom matchers
- [x] T003 Verify test infrastructure works by running `npx vitest run` from kwi-ui/ (should pass with 0 tests)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared components that multiple user stories depend on.

**⚠️ CRITICAL**: The MultiSelectFilter component must be built before US1 can integrate it into WorkItemList.

- [x] T004 Create MultiSelectFilter component at kwi-ui/src/lib/components/MultiSelectFilter.svelte with props: label (string), options (string[]), selected (Set\<string\>), onchange callback; renders button with selection summary, opens checkbox dropdown on click, includes Select All / Clear All actions, closes on outside click or Escape, uses ARIA role="listbox" with aria-multiselectable="true"
- [x] T005 Write component tests for MultiSelectFilter at kwi-ui/src/lib/components/MultiSelectFilter.test.ts covering: renders button with label, opens dropdown on click, toggles individual checkbox, Select All checks all options, Clear All unchecks all options, closes on outside click, closes on Escape key, calls onchange with updated Set on each toggle

**Checkpoint**: MultiSelectFilter is a tested, reusable component ready for integration.

---

## Phase 3: User Story 1 — Multi-Select Filter Dropdowns (Priority: P1) 🎯 MVP

**Goal**: Replace all single-select filter dropdowns in the work item list with multi-select checkbox dropdowns. Default all filters to all values selected except "archived" status. Remove the "Include archived" checkbox.

**Independent Test**: Select a project with varied work items, toggle checkbox combinations in each filter, verify the list updates with correct intersection filtering.

**FR Coverage**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006

### Implementation for User Story 1

- [x] T006 [US1] Refactor WorkItemList.svelte at kwi-ui/src/lib/components/WorkItemList.svelte: replace the four single-select `<select>` dropdowns (area, type, status, size) with MultiSelectFilter components; initialize selectedTypes and selectedSizes as Set with all values; initialize selectedStatuses as Set with all values except "archived"; initialize selectedAreas reactively via $effect after areas load (Set of area names with all selected by default); remove the `showArchived` checkbox and state variable
- [x] T007 [US1] Update the loadItems function in kwi-ui/src/lib/components/WorkItemList.svelte to call listWorkItems(projectId, undefined, undefined, undefined, true) fetching all items, then apply client-side filtering using $derived: filter by selectedTypes, selectedStatuses, selectedSizes, and selectedAreas using Set.has() intersection
- [x] T008 [US1] Remove the "Clear Filters" button logic in kwi-ui/src/lib/components/WorkItemList.svelte and replace it with a clear that resets all filter Sets to their defaults (all selected, archived unchecked)
- [x] T009 [US1] Write integration tests at kwi-ui/src/lib/components/WorkItemList.test.ts verifying: filters render as MultiSelectFilter components, toggling a type checkbox filters the displayed items, status defaults exclude "archived", clearing filters resets to defaults

**Checkpoint**: Work item list has fully functional multi-select filtering. This is the MVP — independently testable.

---

## Phase 4: User Story 2 — Improved Form Field Ordering (Priority: P1)

**Goal**: Reorder the create/edit work item form so Content and Details appear below the metadata dropdowns.

**Independent Test**: Open create and edit forms, verify field order is Title → Type/Status/Size → Area/Sprint/Parent → Content → Details.

**FR Coverage**: FR-007, FR-008

### Implementation for User Story 2

- [x] T010 [US2] Reorder the template in kwi-ui/src/lib/components/WorkItemForm.svelte: move the Content form-group block (textarea for content) below the Area/Sprint/Parent ID row and immediately before the Details form-group block
- [x] T011 [US2] Write test at kwi-ui/src/lib/components/WorkItemForm.test.ts verifying the DOM order: Title input appears before Type select, Type select appears before Content textarea, Content textarea appears before Details textarea

**Checkpoint**: Form field ordering matches the specified layout for both create and edit modes.

---

## Phase 5: User Story 3 — Sensible Create Form Defaults (Priority: P1)

**Goal**: Set create form defaults to Type="issue", Status="open", Size="S" instead of alphabetically first values.

**Independent Test**: Click "New Work Item", verify the dropdowns show "issue", "open", "S" pre-selected.

**FR Coverage**: FR-009, FR-010, FR-011, FR-012

### Implementation for User Story 3

- [x] T012 [US3] Update default assignment logic in kwi-ui/src/lib/components/WorkItemForm.svelte: replace `types[0]` with `types.find(t => t === "issue") ?? types[0]`, replace `statuses[0]` with `statuses.find(s => s === "open") ?? statuses[0]`, replace `tshirtSizes[0]` with `tshirtSizes.find(s => s === "S") ?? tshirtSizes[0]`; ensure edit mode still uses existing item values
- [x] T013 [US3] Add test cases in kwi-ui/src/lib/components/WorkItemForm.test.ts verifying: create mode defaults Type to "issue", Status to "open", Size to "S"; edit mode shows the item's existing values

**Checkpoint**: Create form shows sensible defaults. Edit form unaffected.

---

## Phase 6: User Story 4 — Save Button at Top of Edit Form (Priority: P2)

**Goal**: Add a "Save Changes" button in the edit form's top action bar so users can save without scrolling.

**Independent Test**: Open edit form, verify "Save Changes" appears at top alongside Cancel; click it and verify it saves.

**FR Coverage**: FR-013, FR-014, FR-015

### Implementation for User Story 4

- [x] T014 [US4] Add a "Save Changes" button in the header section of kwi-ui/src/lib/components/WorkItemForm.svelte next to the existing top Cancel button, visible only when `isEdit` is true; bind it to the same `handleSubmit` function; use the shared `saving` state for disabled and "Saving…" text
- [x] T015 [US4] Add test in kwi-ui/src/lib/components/WorkItemForm.test.ts verifying: top save button appears only in edit mode, top save button does not appear in create mode, both save buttons show "Saving…" state simultaneously during save

**Checkpoint**: Edit form has save buttons at both top and bottom, synchronized.

---

## Phase 7: User Story 5 — Project Details Pane (Priority: P2)

**Goal**: Show project metadata in a collapsible section between the search bar and work item list.

**Independent Test**: Select a project, verify a collapsed "Project Details" section appears; expand it and verify metadata fields display correctly.

**FR Coverage**: FR-016, FR-017, FR-018, FR-019

### Implementation for User Story 5

- [x] T016 [P] [US5] Create ProjectDetails component at kwi-ui/src/lib/components/ProjectDetails.svelte using a native `<details>` element (closed by default); display project short name and CN path always; conditionally display GitHub repo and description only when present (not null/undefined)
- [x] T017 [P] [US5] Write tests at kwi-ui/src/lib/components/ProjectDetails.test.ts verifying: renders collapsed by default, shows short name and CN path, shows GitHub repo when present, omits GitHub repo when null, shows description when present, omits description when null
- [x] T018 [US5] Insert ProjectDetails component in kwi-ui/src/routes/+page.svelte between the SearchBar div and the view content area, passing `appState.selectedProject` as the project prop; only render when a project is selected

**Checkpoint**: Project metadata is accessible without leaving the work item view.

---

## Phase 8: User Story 6 — Refresh Buttons (Priority: P2)

**Goal**: Add manual refresh buttons to the project sidebar and work item list for reloading data from the database.

**Independent Test**: Modify data via CLI, click refresh buttons, verify updated data appears without restarting the app.

**FR Coverage**: FR-020, FR-021, FR-022, FR-023

### Implementation for User Story 6

- [x] T019 [P] [US6] Add a refresh button (↻) to the sidebar header in kwi-ui/src/lib/components/ProjectSelector.svelte next to the "Projects" heading; on click, call the existing loadProjects function; show a loading/spinning state via CSS animation while projects reload; add aria-label="Refresh projects"
- [x] T020 [P] [US6] Add a refresh button (↻) to the work item list header in kwi-ui/src/lib/components/WorkItemList.svelte next to the "New Work Item" button; on click, call the existing loadItems function; show a loading/spinning state while items reload; preserve current filter selections; add aria-label="Refresh work items"
- [x] T021 [US6] Write tests at kwi-ui/src/lib/components/ProjectSelector.test.ts verifying: refresh button is rendered, clicking refresh triggers data reload
- [x] T022 [US6] Write tests at kwi-ui/src/lib/components/WorkItemList.test.ts (append to existing) verifying: refresh button is rendered, clicking refresh triggers data reload with filters preserved

**Checkpoint**: Both lists can be manually refreshed without restarting the application.

---

## Phase 9: User Story 7 — Window Size Persistence (Priority: P3)

**Goal**: Persist window dimensions across application sessions using the tauri-plugin-window-state plugin; enforce minimum window size.

**Independent Test**: Resize window, close app, relaunch — window opens at saved size. Verify minimum size cannot be exceeded.

**FR Coverage**: FR-024, FR-025, FR-026, FR-027

### Implementation for User Story 7

- [x] T023 [US7] Add tauri-plugin-window-state dependency to kwi-ui/src-tauri/Cargo.toml: `tauri-plugin-window-state = "2"`
- [x] T024 [US7] Register the window state plugin in kwi-ui/src-tauri/src/lib.rs: add `.plugin(tauri_plugin_window_state::Builder::new().build())` to the Tauri builder chain after the opener plugin
- [x] T025 [US7] Add window-state permission to kwi-ui/src-tauri/capabilities/default.json: add "window-state:default" to the permissions array
- [x] T026 [US7] Set minimum window size in kwi-ui/src-tauri/tauri.conf.json: add "minWidth": 640 and "minHeight": 480 to the window configuration
- [x] T027 [US7] Build and manually test window state persistence: resize window, close app, relaunch and verify window opens at saved size; verify minimum size is enforced

**Checkpoint**: Window size persists across sessions; minimum size prevents unusable layouts.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final quality checks, documentation, and code standards.

- [x] T028 Run pre-commit checks from kwi-ui/: `npx prettier --write .` then `npx prettier --check .`, `npx eslint .`, `npx svelte-check`
- [x] T029 Run Rust pre-commit checks from kwi-ui/src-tauri/: `cargo fmt`, `cargo clippy --all-targets --all-features`, `cargo test`
- [x] T030 Run full test suite: `cd kwi-ui && npx vitest run`
- [x] T031 [P] Validate quickstart.md at specs/004-kwi-ui-polish/quickstart.md by following the setup steps and verifying all described behaviors work
- [x] T032 [P] Update docs/usage.md with new UI behaviors: multi-select filters, form defaults, project details, refresh buttons, window persistence
- [x] T033 [P] Update docs/specification.md with new functional requirements from this sprint (FR-001 through FR-027)
- [x] T034 [P] Update docs/architecture.md to document the tauri-plugin-window-state dependency and window persistence behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (vitest config must exist for tests)
- **US1 (Phase 3)**: Depends on Phase 2 (needs MultiSelectFilter component)
- **US2 (Phase 4)**: Depends on Phase 1 only — no dependency on other user stories
- **US3 (Phase 5)**: Depends on Phase 1 only — no dependency on other user stories
- **US4 (Phase 6)**: Depends on Phase 1 only — no dependency on other user stories
- **US5 (Phase 7)**: Depends on Phase 1 only — no dependency on other user stories
- **US6 (Phase 8)**: Depends on Phase 1 only — no dependency on other user stories
- **US7 (Phase 9)**: No frontend test dependencies — Rust/Tauri config changes only
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Multi-Select Filters)**: Depends on Foundational (MultiSelectFilter component)
- **US2 (Form Field Order)**: Independent — template-only change
- **US3 (Form Defaults)**: Independent — logic-only change in same file as US2 but different code section
- **US4 (Top Save Button)**: Independent — template addition in same file as US2/US3
- **US5 (Project Details)**: Independent — new component + page integration
- **US6 (Refresh Buttons)**: Independent — small additions to existing components
- **US7 (Window Persistence)**: Independent — Rust/Tauri config only, no frontend component changes

### Within Each User Story

- Implementation before tests (or interleaved per TDD preference)
- Component creation before page integration
- Commit after each completed story

### Parallel Opportunities

- **After Phase 1**: US2, US3, US4, US5, US6, US7 can all start in parallel (different files or different code sections)
- **After Phase 2**: US1 can start (needs MultiSelectFilter)
- **Within Phase 2**: T004 and T005 are sequential (component before tests)
- **Within Phase 7**: T016 and T017 can run in parallel (component and tests are independent files)
- **Within Phase 8**: T019 and T020 can run in parallel (different components)

---

## Parallel Example: After Phase 2

```
# These can all proceed simultaneously after Foundational is complete:

Stream A (US1 — depends on MultiSelectFilter):
  T006 → T007 → T008 → T009

Stream B (US2 + US3 + US4 — all in WorkItemForm.svelte, apply sequentially):
  T010 → T011 → T012 → T013 → T014 → T015

Stream C (US5 — new component):
  T016 + T017 (parallel) → T018

Stream D (US6 — refresh buttons):
  T019 + T020 (parallel) → T021 + T022

Stream E (US7 — Rust/Tauri config):
  T023 → T024 → T025 → T026 → T027
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (vitest config)
2. Complete Phase 2: Foundational (MultiSelectFilter component)
3. Complete Phase 3: User Story 1 (integrate filters into WorkItemList)
4. **STOP and VALIDATE**: Test multi-select filtering independently
5. Demo if ready — this alone delivers the highest-value improvement

### Incremental Delivery

1. Setup + Foundational → Test infrastructure + MultiSelectFilter ready
2. US1 (Multi-Select Filters) → Test independently → **MVP!**
3. US2 + US3 (Form order + defaults) → Test independently → Quick wins
4. US4 (Top save button) → Test independently → Edit workflow improved
5. US5 (Project details) → Test independently → Context accessible
6. US6 (Refresh buttons) → Test independently → Multi-tool workflow
7. US7 (Window persistence) → Test manually → Desktop polish
8. Polish → Full validation → Sprint complete

---

## Phase 11: Developer Tooling

**Purpose**: Add a justfile for streamlined development commands including Windows cross-compilation.

- [x] T035 Create kwi-ui/justfile with recipes: dev, build, test, check, fmt, lint, clippy, rustfmt, winrelease, precommit
- [x] T036 Verify `just test` and `just check` run successfully from kwi-ui/
- [x] T037 Verify `just winrelease` cross-compiles for x86_64-pc-windows-gnu

---

## Notes

- All frontend changes are in kwi-ui/src/ — no Python CLI or MCP changes
- US2, US3, US4 all modify WorkItemForm.svelte — apply sequentially to avoid merge conflicts
- US7 is the only story requiring Rust changes (Cargo.toml, lib.rs)
- The "Include archived" checkbox removal (FR-006) is part of US1 (T006)
- Area filter also converted to multi-select for consistency (per Assumptions in spec.md)
