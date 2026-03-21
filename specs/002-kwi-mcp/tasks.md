# Tasks: kwi MCP Server

**Input**: Design documents from `/specs/002-kwi-mcp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.md, quickstart.md

**Tests**: Included (constitution Principle III mandates TDD).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Add MCP dependency, create subpackage structure, configure entry point

- [x] T001 Add `mcp` dependency to pyproject.toml and add `kwi-mcp` entry point to `[project.scripts]`
- [x] T002 [P] Create MCP subpackage directory src/kwi/mcp/__init__.py with server factory and main() entry point
- [x] T003 [P] Create src/kwi/mcp/server.py with FastMCP instance and DB helper function
- [x] T004 Verify `uv run kwi-mcp` starts without error (smoke test)
- [x] T005 Run code standards gate: `ruff format --check && ruff check && ty check`

**Checkpoint**: `kwi-mcp` entry point exists, server starts and is ready for tool registration

---

## Phase 2: Foundational

**Purpose**: Test infrastructure for MCP tools — fixtures that all user story phases depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Add MCP test fixtures to tests/conftest.py (mcp_server, call_tool helper using `mcp` SDK test client)
- [x] T007 Write a smoke test in tests/test_mcp.py verifying the server initializes and lists tools

**Checkpoint**: Test harness ready — tool tests can now be written

---

## Phase 3: User Story 1 — Query Work Items (Priority: P1) 🎯 MVP

**Goal**: AI agents can list projects, areas, and work items, and get full work item details

**Independent Test**: Call each read-only tool via MCP test client and verify structured responses match database state

### Tests for User Story 1

- [x] T008 [P] [US1] Write test for `list_projects` tool in tests/test_mcp.py
- [x] T009 [P] [US1] Write test for `list_areas` tool (valid project, invalid project) in tests/test_mcp.py
- [x] T010 [P] [US1] Write test for `list_work_items` tool (basic list, status filter, area filter, archived exclusion) in tests/test_mcp.py
- [x] T011 [P] [US1] Write test for `get_work_item` tool (existing item, non-existent item) in tests/test_mcp.py

### Implementation for User Story 1

- [x] T012 [US1] Implement `list_projects` tool in src/kwi/mcp/server.py
- [x] T013 [US1] Implement `list_areas` tool in src/kwi/mcp/server.py
- [x] T014 [US1] Implement `list_work_items` tool in src/kwi/mcp/server.py
- [x] T015 [US1] Implement `get_work_item` tool in src/kwi/mcp/server.py
- [x] T016 [US1] Run code standards gate and verify all US1 tests pass

**Checkpoint**: An MCP client can discover projects, list/filter work items, and view full details

---

## Phase 4: User Story 2 — Create Work Items (Priority: P1)

**Goal**: AI agents can create new work items with required and optional fields

**Independent Test**: Call `create_work_item` with various field combinations and verify items are persisted correctly

### Tests for User Story 2

- [x] T017 [P] [US2] Write tests for `create_work_item` tool (all fields, defaults only, invalid project, invalid type) in tests/test_mcp.py

### Implementation for User Story 2

- [x] T018 [US2] Implement `create_work_item` tool in src/kwi/mcp/server.py
- [x] T019 [US2] Run code standards gate and verify all US2 tests pass

**Checkpoint**: An MCP client can create work items; combined with US1, agents have full read+create capability

---

## Phase 5: User Story 3 — Update Work Items (Priority: P2)

**Goal**: AI agents can update any mutable field on an existing work item

**Independent Test**: Call `update_work_item` to change fields and verify changes persist

### Tests for User Story 3

- [x] T020 [P] [US3] Write tests for `update_work_item` tool (single field, multiple fields, non-existent ID, invalid status) in tests/test_mcp.py

### Implementation for User Story 3

- [x] T021 [US3] Implement `update_work_item` tool in src/kwi/mcp/server.py
- [x] T022 [US3] Run code standards gate and verify all US3 tests pass

**Checkpoint**: An MCP client can update work items

---

## Phase 6: User Story 4 — Archive Work Items (Priority: P2)

**Goal**: AI agents can archive work items so they are excluded from default listings

**Independent Test**: Archive an item and verify it no longer appears in default `list_work_items`

### Tests for User Story 4

- [x] T023 [P] [US4] Write tests for `archive_work_item` tool (archive succeeds, excluded from default list, included with status filter) in tests/test_mcp.py

### Implementation for User Story 4

- [x] T024 [US4] Implement `archive_work_item` tool in src/kwi/mcp/server.py
- [x] T025 [US4] Run code standards gate and verify all US4 tests pass

**Checkpoint**: Full CRUD + archive for work items via MCP

---

## Phase 7: User Story 5 — Manage Relationships (Priority: P3)

**Goal**: AI agents can create, remove, and list relationships between work items

**Independent Test**: Create a relationship, list it, then remove it

### Tests for User Story 5

- [x] T026 [P] [US5] Write tests for `relate_work_items`, `list_related`, `unrelate_work_items` tools in tests/test_mcp.py

### Implementation for User Story 5

- [x] T027 [US5] Implement `relate_work_items` tool in src/kwi/mcp/server.py
- [x] T028 [US5] Implement `unrelate_work_items` tool in src/kwi/mcp/server.py
- [x] T029 [US5] Implement `list_related` tool in src/kwi/mcp/server.py
- [x] T030 [US5] Run code standards gate and verify all US5 tests pass

**Checkpoint**: Relationship management available via MCP

---

## Phase 8: User Story 6 — Search Work Items (Priority: P3)

**Goal**: AI agents can search work items by keyword across title and content

**Independent Test**: Create items with known text, search for them, verify matches

### Tests for User Story 6

- [x] T031 [P] [US6] Write tests for `search_work_items` tool (title match, content match, no results) in tests/test_mcp.py

### Implementation for User Story 6

- [x] T032 [US6] Add `search_work_items` query function to src/kwi/queries.py (ILIKE on title and content, scoped to project)
- [x] T033 [US6] Implement `search_work_items` MCP tool in src/kwi/mcp/server.py
- [x] T034 [US6] Run code standards gate and verify all US6 tests pass

**Checkpoint**: All 12 MCP tools implemented and tested

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final validation, client verification

- [x] T035 [P] Update docs/setup.md with MCP server installation and configuration instructions
- [x] T036 [P] Update docs/usage.md with MCP tool reference (all 12 tools, parameters, examples)
- [x] T037 [P] Update docs/specification.md with MCP server feature (constitution Principle I)
- [x] T038 [P] Update docs/architecture.md with MCP server architecture (constitution Principle II)
- [x] T039 Add test for DB connection failure error handling in tests/test_mcp.py
- [x] T040 Run full code standards gate: `ruff format --check && ruff check && ty check && pytest -q`
- [x] T041 Configure `kwi-mcp` in .vscode/settings.json and verify tools are discovered by VS Code agent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Phase 2 completion
  - US1 (Phase 3): No dependencies on other stories
  - US2 (Phase 4): No dependencies on other stories (can parallel with US1)
  - US3 (Phase 5): No dependencies on other stories
  - US4 (Phase 6): No dependencies on other stories
  - US5 (Phase 7): No dependencies on other stories
  - US6 (Phase 8): No dependencies on other stories (but adds a new query function)
- **Polish (Phase 9)**: Depends on all user story phases

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Implementation tasks follow test tasks
- Code standards gate at end of each phase

### Parallel Opportunities

- T002, T003 can run in parallel (different files)
- All US test tasks marked [P] within a phase can run in parallel
- Once Phase 2 completes, US1-US6 can theoretically run in parallel (but sequential by priority is recommended for solo developer)

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T007)
3. Complete Phase 3: US1 — Query (T008-T016)
4. Complete Phase 4: US2 — Create (T017-T019)
5. **STOP and VALIDATE**: Agent can read and create work items
6. Configure in VS Code and verify end-to-end

### Incremental Delivery

1. Setup + Foundational → Server skeleton
2. US1 + US2 → Read + Create (MVP — deploy/demo)
3. US3 + US4 → Update + Archive (full CRUD)
4. US5 + US6 → Relationships + Search (complete feature set)
5. Polish → Documentation and client verification

---

## Notes

- All tool implementations reuse `kwi.queries` and `kwi.db` — no new SQL
- Database schema is unchanged from Spec 001
- MCP SDK's `FastMCP` handles JSON schema generation from type hints
- Connection per tool call (no pooling needed for single-user)
- Commit after each completed phase checkpoint
