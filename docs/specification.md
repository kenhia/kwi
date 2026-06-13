# kwi Specification

## Overview

kwi is a work item management system with a PostgreSQL backend,
a CLI interface, an MCP server for AI agent integration, and a
desktop GUI for visual work item management.

## Features

### CLI (`kwi`)

Full CRUD for projects, areas, and work items via command-line.
Supports JSON output, markdown templates, and relationship
management.

### MCP Server (`kwi-mcp`)

Model Context Protocol server exposing 15 tools over stdio
transport. Enables AI agents to query, create, update, archive,
un-archive, and search work items programmatically, and to create
projects and areas.

**Tools**: `list_projects`, `list_areas`, `list_work_items`,
`get_work_item`, `create_work_item`, `update_work_item`,
`archive_work_item`, `unarchive_work_item`, `relate_work_items`,
`unrelate_work_items`, `list_related`, `search_work_items`,
`create_project`, `create_area`.

### Desktop GUI (`kwi-ui`)

Tauri 2 / Svelte 5 desktop application for visual work item
management. Provides a two-panel layout with project sidebar
and main content area.

**Capabilities**: Browse projects and work items, create and
edit work items with form validation, archive and un-archive
work items, manage relationships between items, full-text search,
create projects and areas. Renders markdown content and details.
Multi-select checkbox filter dropdowns for type, status, size,
area, and sprint (with an "Unassigned" bucket). Filters are
session-sticky and show a cue when off-default; `closed` items
and archived items are hidden by default. Archiving is immediate
(no confirmation prompt). Collapsible project details pane.
Refresh buttons for projects and work items. Sensible form
defaults (issue/open/S). Save button at top and bottom of edit
form. Window size and position persistence across sessions.

**Platforms**: Linux (x86_64) and Windows (x86_64).

## Data Model

- **Project**: Top-level container with short name and path
- **Area**: Subdivision within a project
- **WorkItem**: Core entity with type, status, t-shirt size,
  sprint, content, details, and an `archived` boolean flag
  (independent of status)
- **Related**: Labeled bidirectional relationships between work items

## Reference Data

- **Types**: bug, epic, feature, idea, issue, research, story, task, tweak
- **Statuses**: active, closed, draft, open, resolved
- **T-shirt sizes**: XS, S, M, L, XL, Huge, Unknown
