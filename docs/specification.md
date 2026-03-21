# kwi Specification

## Overview

kwi is a work item management system with a PostgreSQL backend,
a CLI interface, and an MCP server for AI agent integration.

## Features

### CLI (`kwi`)

Full CRUD for projects, areas, and work items via command-line.
Supports JSON output, markdown templates, and relationship
management.

### MCP Server (`kwi-mcp`)

Model Context Protocol server exposing 12 tools over stdio
transport. Enables AI agents to query, create, update, archive,
and search work items programmatically.

**Tools**: `list_projects`, `list_areas`, `list_work_items`,
`get_work_item`, `create_work_item`, `update_work_item`,
`archive_work_item`, `relate_work_items`, `unrelate_work_items`,
`list_related`, `search_work_items`.

## Data Model

- **Project**: Top-level container with short name and path
- **Area**: Subdivision within a project
- **WorkItem**: Core entity with type, status, t-shirt size,
  sprint, content, and details
- **Related**: Labeled bidirectional relationships between work items

## Reference Data

- **Types**: bug, epic, feature, idea, issue, research, story, task, tweak
- **Statuses**: active, archived, closed, draft, open, resolved
- **T-shirt sizes**: XS, S, M, L, XL, Huge, Unknown
