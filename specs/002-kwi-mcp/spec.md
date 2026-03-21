# Feature Specification: kwi MCP Server

**Feature Branch**: `002-kwi-mcp`
**Created**: 2026-03-21
**Status**: Draft
**Input**: MCP server for kwi work item tracking — expose project, area, and work item operations as MCP tools for AI agent integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Query Work Items from an AI Agent (Priority: P1)

An AI coding agent (e.g., GitHub Copilot, Claude) needs to read the user's work items during a coding session. The agent calls MCP tools to list projects, list work items filtered by project/status/area, and retrieve full details of a specific work item — all without the user leaving the editor.

**Why this priority**: Reading data is the foundational capability. Every other story depends on the agent being able to discover and retrieve work items. This alone delivers value by letting agents understand current tasks.

**Independent Test**: Can be fully tested by configuring an MCP client to connect to the server and calling list/get tools; delivers value by giving agents read access to all work item data.

**Acceptance Scenarios**:

1. **Given** the MCP server is running and connected to the database, **When** an agent calls `list_projects`, **Then** it receives a list of all projects with their IDs, short names, and descriptions.
2. **Given** a project "kwi" exists with work items, **When** an agent calls `list_work_items` with `project: "kwi"`, **Then** it receives all non-archived work items for that project with ID, area, type, status, t-shirt size, sprint, and title.
3. **Given** a project "kwi" has items in statuses "open" and "closed", **When** an agent calls `list_work_items` with `project: "kwi"` and `status: "open"`, **Then** only open items are returned.
4. **Given** work item 116 exists, **When** an agent calls `get_work_item` with `id: 116`, **Then** it receives all fields including full markdown content and details.
5. **Given** an agent calls `get_work_item` with a non-existent ID, **Then** the tool returns a clear error message indicating the item was not found.
6. **Given** a project "kwi" exists with areas, **When** an agent calls `list_areas` with `project: "kwi"`, **Then** it receives all areas for that project.

---

### User Story 2 — Create Work Items from an AI Agent (Priority: P1)

While working on code, an AI agent discovers a bug, identifies a needed task, or the user asks the agent to log an idea. The agent calls an MCP tool to create a new work item directly in the database, without the user switching to the terminal or another tool.

**Why this priority**: Creating work items is equally critical to reading them. The primary value of the MCP server is enabling agents to both consume and produce work items during coding sessions.

**Independent Test**: Can be tested by calling `create_work_item` with required fields and verifying the item appears in the database with correct values.

**Acceptance Scenarios**:

1. **Given** project "kwi" and area "cli" exist, **When** an agent calls `create_work_item` with project, title, content, type, and area, **Then** a new work item is created and its ID is returned.
2. **Given** an agent provides only the required fields (project, title, content), **When** it calls `create_work_item`, **Then** the item is created with defaults (type: "task", status: "open", t-shirt: "Unknown").
3. **Given** an agent provides an invalid project name, **When** it calls `create_work_item`, **Then** a clear error message is returned indicating the project was not found.
4. **Given** an agent provides an invalid type or status value, **When** it calls `create_work_item`, **Then** a clear error message is returned listing the valid values.

---

### User Story 3 — Update Work Items from an AI Agent (Priority: P2)

An AI agent needs to update work items as tasks progress — changing status when work is started or completed, updating content with new findings, assigning sprints, or adjusting t-shirt sizes. The agent calls an MCP tool to modify one or more fields on an existing work item.

**Why this priority**: Updating items completes the CRUD lifecycle and allows agents to manage work state transitions, which is essential for tracking progress during sprints.

**Independent Test**: Can be tested by calling `update_work_item` to change a field and verifying the change persists in the database.

**Acceptance Scenarios**:

1. **Given** work item 116 exists with status "open", **When** an agent calls `update_work_item` with `id: 116` and `status: "active"`, **Then** the item's status is updated and the `updated` timestamp changes.
2. **Given** work item 116 exists, **When** an agent calls `update_work_item` with `id: 116`, `sprint: "002-kwi-mcp"`, and `tshirt: "M"`, **Then** both fields are updated in a single call.
3. **Given** an agent calls `update_work_item` with a non-existent ID, **Then** a clear error is returned.
4. **Given** an agent tries to set an invalid status, **Then** a clear error is returned listing valid statuses.

---

### User Story 4 — Archive Work Items from an AI Agent (Priority: P2)

An AI agent needs to archive completed or obsolete work items so they no longer appear in default listings. This is a soft delete — the item remains in the database but is excluded from normal queries.

**Why this priority**: Archiving keeps work item lists clean and is a common action when closing out sprints or completing features.

**Independent Test**: Can be tested by calling `archive_work_item` and verifying the item's status changes to "archived" and it no longer appears in default `list_work_items` results.

**Acceptance Scenarios**:

1. **Given** work item 42 exists with status "closed", **When** an agent calls `archive_work_item` with `id: 42`, **Then** the item's status is set to "archived".
2. **Given** work item 42 is archived, **When** an agent calls `list_work_items` for its project without a status filter, **Then** item 42 is not included in results.
3. **Given** work item 42 is archived, **When** an agent calls `list_work_items` with `status: "archived"`, **Then** item 42 is included.

---

### User Story 5 — Manage Work Item Relationships from an AI Agent (Priority: P3)

An AI agent needs to link related work items — for example, linking a bug to the feature it affects, or linking duplicate issues. The agent can create, remove, and list relationships between work items.

**Why this priority**: Relationships add context but aren't required for core tracking. Agents can function effectively without them.

**Independent Test**: Can be tested by calling `relate_work_items`, then `list_related` to verify the link, then `unrelate_work_items` to remove it.

**Acceptance Scenarios**:

1. **Given** work items 10 and 20 exist, **When** an agent calls `relate_work_items` with `left_id: 10`, `right_id: 20`, `relationship: "blocks"`, **Then** the relationship is created.
2. **Given** items 10 and 20 are related, **When** an agent calls `list_related` with `id: 10`, **Then** item 20 appears in the results with the relationship label.
3. **Given** items 10 and 20 are related, **When** an agent calls `unrelate_work_items` with `left_id: 10`, `right_id: 20`, **Then** the relationship is removed.

---

### User Story 6 — Search Work Items (Priority: P3)

An AI agent needs to find work items by searching across titles and content. This lets agents discover relevant items without knowing exact IDs — for example, finding all items mentioning "authentication" or "login bug".

**Why this priority**: Search enhances discoverability but agents can use filtered listing as a fallback. Valuable but not essential for MVP.

**Independent Test**: Can be tested by calling `search_work_items` with a term that matches known items and verifying results include those items.

**Acceptance Scenarios**:

1. **Given** work items exist with "template" in their title, **When** an agent calls `search_work_items` with `query: "template"` and `project: "kwi"`, **Then** matching items are returned.
2. **Given** a search query matches content but not title, **When** an agent calls `search_work_items`, **Then** the item is still found (search covers both title and content fields).
3. **Given** a search query has no matches, **When** an agent calls `search_work_items`, **Then** an empty list is returned (not an error).

---

### Edge Cases

- What happens when the database is unreachable? The server should return clear error messages rather than crashing.
- What happens when an agent provides extra/unknown parameters? The server should ignore unknown parameters gracefully.
- What happens when two agents modify the same work item simultaneously? PostgreSQL transaction isolation handles this; last write wins.
- What happens when content contains very large markdown (100KB+)? The system should handle it without truncation since PostgreSQL `text` columns have no practical limit.
- What happens when an agent calls `list_work_items` with no filters? It should return all non-archived items across all projects (may be a large result set).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST implement the Model Context Protocol (MCP) and be usable from any MCP-compatible client.
- **FR-002**: The server MUST expose a `list_projects` tool that returns all projects with ID, short name, canonical path, GitHub repo, and description.
- **FR-003**: The server MUST expose a `list_areas` tool that accepts a project identifier (name or ID) and returns all areas for that project.
- **FR-004**: The server MUST expose a `list_work_items` tool that accepts optional filters: project (required), area, status (one or more), type, t-shirt size, and sprint. Archived items are excluded by default unless status "archived" is explicitly requested.
- **FR-005**: The server MUST expose a `get_work_item` tool that accepts a work item ID and returns all fields including full markdown content and details.
- **FR-006**: The server MUST expose a `create_work_item` tool that accepts project (required), title (required), content (required), and optional fields: area, type (default: "task"), status (default: "open"), t-shirt size (default: "Unknown"), sprint, details, and parent ID.
- **FR-007**: The server MUST expose an `update_work_item` tool that accepts a work item ID (required) and one or more optional fields to change: title, content, details, type, status, t-shirt size, sprint, area, and parent ID.
- **FR-008**: The server MUST expose an `archive_work_item` tool that sets a work item's status to "archived".
- **FR-009**: The server MUST expose a `relate_work_items` tool that creates a labeled relationship between two work items.
- **FR-010**: The server MUST expose an `unrelate_work_items` tool that removes a relationship between two work items.
- **FR-011**: The server MUST expose a `list_related` tool that returns all items related to a given work item, with relationship labels.
- **FR-012**: The server MUST expose a `search_work_items` tool that performs text search across work item titles and content, scoped to a project.
- **FR-013**: All tools MUST return structured data (not pre-formatted tables) so that agents can process results programmatically.
- **FR-014**: All tools MUST return clear, descriptive error messages when operations fail (invalid IDs, missing required fields, invalid enum values).
- **FR-015**: The server MUST discover the database connection using the same precedence as the CLI: tool-specific argument > `KWI_DATABASE_URL` environment variable > `~/.config/kwi/config.toml`.
- **FR-016**: The server MUST reuse the existing database access layer from `kwi` (query functions and connection management) to avoid duplicating logic.
- **FR-017**: The server MUST be installable and runnable via `uv` as a standalone entry point (`kwi-mcp`).

### Key Entities

All entities are shared with the existing `kwi` database and CLI — no new tables or schema changes are required for this spec.

- **Project**: Container for work items; identified by short name or numeric ID.
- **Area**: Sub-category within a project (e.g., "cli", "mcp", "api").
- **Work Item**: The central tracked entity with type, status, t-shirt size, sprint, title, markdown content, optional details, and optional parent.
- **Related**: A labeled directional link between two work items.

## Assumptions

- The existing PostgreSQL schema from Spec 001 is already deployed and unchanged. No new migrations are needed for this spec.
- The existing `kwi` query functions (`src/kwi/queries.py`) and connection management (`src/kwi/db.py`) can be imported and reused directly by the MCP server.
- The MCP server runs as a long-lived process (stdio or SSE transport) rather than a one-shot CLI invocation.
- The server is single-user (personal tool) — no authentication or authorization is required.
- Text search (FR-012) uses SQL `ILIKE` pattern matching rather than PostgreSQL full-text search (`tsvector`). Full-text search can be added in a future iteration if needed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An AI agent can list all projects and their areas within a single MCP tool call.
- **SC-002**: An AI agent can retrieve a filtered list of work items (by project, status, area, type) in a single tool call.
- **SC-003**: An AI agent can create a new work item and receive its ID in a single tool call, without needing to use the terminal or CLI.
- **SC-004**: An AI agent can update any mutable field on a work item in a single tool call.
- **SC-005**: An AI agent can search for work items by keyword and find relevant results across title and content.
- **SC-006**: All MCP tool errors return structured messages that agents can interpret without parsing stack traces.
- **SC-007**: The server passes validation with at least one MCP-compatible client (e.g., VS Code Copilot agent mode, Claude Desktop).
