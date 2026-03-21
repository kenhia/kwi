# Data Model: kwi MCP Server

**Date**: 2026-03-21
**Feature**: 002-kwi-mcp

## Overview

The MCP server operates on the same database schema as the CLI
(Spec 001). No new tables, columns, or migrations are required.

This document describes the entities as seen by MCP tool consumers
(AI agents) — the "view model" exposed through tool responses.

## Entities

### Project

Returned by `list_projects` and referenced by other tools.

| Field       | Type    | Notes                          |
|-------------|---------|--------------------------------|
| id          | integer | Primary key                    |
| project     | string  | Short name (unique)            |
| cn_path     | string  | Canonical filesystem path      |
| gh_repo     | string? | GitHub repo (nullable)         |
| description | string? | Markdown description           |
| created     | string  | ISO 8601 timestamp             |
| updated     | string  | ISO 8601 timestamp             |

### Area

Returned by `list_areas`, scoped to a project.

| Field       | Type    | Notes                          |
|-------------|---------|--------------------------------|
| id          | integer | Primary key                    |
| project_id  | integer | Parent project                 |
| name        | string  | Area name (unique per project) |
| description | string? | Optional description           |

### Work Item

Returned by `list_work_items`, `get_work_item`, `create_work_item`,
and `update_work_item`.

| Field        | Type    | Notes                                |
|--------------|---------|--------------------------------------|
| id           | integer | Primary key                          |
| project_id   | integer | Parent project                       |
| project_name | string? | Resolved project short name          |
| area_id      | integer?| Optional area                        |
| area_name    | string? | Resolved area name                   |
| title        | string  | Work item title                      |
| content      | string  | Markdown body                        |
| details      | string? | Additional markdown details          |
| wi_type      | string  | One of: bug, task, idea, research, tweak, issue, feature, epic, story |
| wi_status    | string  | One of: open, active, resolved, closed, draft, archived |
| wi_tshirt    | string  | One of: XS, S, M, L, XL, Huge, Unknown |
| sprint       | string? | Free-form sprint label               |
| parent_id    | integer?| Parent work item (for hierarchy)     |
| created      | string  | ISO 8601 timestamp                   |
| updated      | string  | ISO 8601 timestamp                   |

**list_work_items** returns a summary subset: id, area_name,
wi_type, wi_status, wi_tshirt, sprint, title.

**get_work_item** returns all fields.

### Related

Returned by `list_related`.

| Field        | Type    | Notes                          |
|--------------|---------|--------------------------------|
| id           | integer | Relationship ID                |
| left_id      | integer | Source work item                |
| right_id     | integer | Target work item               |
| relationship | string  | Relationship label (e.g., "blocks") |
| other_id     | integer | The related item's ID          |
| other_title  | string  | The related item's title       |

## State Transitions

Work item statuses follow the existing semantics:

```
draft → open → active → resolved → closed → archived
```

Any status can be set directly via `update_work_item`. The
`archive_work_item` tool is a shortcut that sets status to
"archived".

## No Schema Changes

The MCP server uses the existing schema from `migrations/001_initial_schema.sql`
without modification. All data access goes through `kwi.queries`.
