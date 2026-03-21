# MCP Tool Contracts: kwi MCP Server

**Date**: 2026-03-21
**Feature**: 002-kwi-mcp

All tools use the MCP protocol. Parameters are derived from Python
function signatures. Responses are JSON objects returned as MCP tool
results.

---

## list_projects

List all projects in the database.

**Parameters**: None

**Returns**: List of project objects with fields: id, project,
cn_path, gh_repo, description, created, updated.

**Errors**: Database connection failure.

---

## list_areas

List areas for a given project.

**Parameters**:

| Name    | Type   | Required | Description                      |
|---------|--------|----------|----------------------------------|
| project | string | yes      | Project short name or numeric ID |

**Returns**: List of area objects with fields: id, project_id,
name, description.

**Errors**: Project not found.

---

## list_work_items

List work items with optional filters. Archived items are excluded
by default.

**Parameters**:

| Name    | Type   | Required | Description                       |
|---------|--------|----------|-----------------------------------|
| project | string | yes      | Project short name or numeric ID  |
| area    | string | no       | Filter by area name               |
| status  | string | no       | Filter by status (comma-separated for multiple) |
| type    | string | no       | Filter by work item type          |
| tshirt  | string | no       | Filter by t-shirt size            |
| sprint  | string | no       | Filter by sprint label            |

**Returns**: List of work item summaries with fields: id,
area_name, wi_type, wi_status, wi_tshirt, sprint, title.

**Errors**: Project not found.

---

## get_work_item

Get full details of a single work item.

**Parameters**:

| Name | Type    | Required | Description    |
|------|---------|----------|----------------|
| id   | integer | yes      | Work item ID   |

**Returns**: Full work item object with all fields.

**Errors**: Work item not found.

---

## create_work_item

Create a new work item.

**Parameters**:

| Name    | Type    | Required | Default   | Description              |
|---------|---------|----------|-----------|--------------------------|
| project | string  | yes      |           | Project short name or ID |
| title   | string  | yes      |           | Work item title          |
| content | string  | yes      |           | Markdown body            |
| area    | string  | no       | null      | Area name                |
| type    | string  | no       | "task"    | Work item type           |
| status  | string  | no       | "open"    | Work item status         |
| tshirt  | string  | no       | "Unknown" | T-shirt size             |
| sprint  | string  | no       | null      | Sprint label             |
| details | string  | no       | null      | Additional markdown      |
| parent  | integer | no       | null      | Parent work item ID      |

**Returns**: Created work item object with generated ID.

**Errors**: Project not found; invalid type/status/tshirt value;
area not found.

---

## update_work_item

Update one or more fields on an existing work item.

**Parameters**:

| Name    | Type    | Required | Description              |
|---------|---------|----------|--------------------------|
| id      | integer | yes      | Work item ID             |
| title   | string  | no       | New title                |
| content | string  | no       | New markdown body        |
| details | string  | no       | New additional markdown  |
| type    | string  | no       | New work item type       |
| status  | string  | no       | New status               |
| tshirt  | string  | no       | New t-shirt size         |
| sprint  | string  | no       | New sprint label         |
| area    | string  | no       | New area name            |
| parent  | integer | no       | New parent work item ID  |

**Returns**: Confirmation message with work item ID.

**Errors**: Work item not found; invalid type/status/tshirt value;
area not found.

---

## archive_work_item

Archive a work item (sets status to "archived").

**Parameters**:

| Name | Type    | Required | Description    |
|------|---------|----------|----------------|
| id   | integer | yes      | Work item ID   |

**Returns**: Confirmation message.

**Errors**: Work item not found.

---

## relate_work_items

Create a labeled relationship between two work items.

**Parameters**:

| Name         | Type    | Required | Description                  |
|--------------|---------|----------|------------------------------|
| left_id      | integer | yes      | First work item ID           |
| right_id     | integer | yes      | Second work item ID          |
| relationship | string  | yes      | Relationship label (e.g., "blocks") |

**Returns**: Confirmation message.

**Errors**: Work item(s) not found; duplicate relationship.

---

## unrelate_work_items

Remove a relationship between two work items.

**Parameters**:

| Name     | Type    | Required | Description          |
|----------|---------|----------|----------------------|
| left_id  | integer | yes      | First work item ID   |
| right_id | integer | yes      | Second work item ID  |

**Returns**: Confirmation message.

**Errors**: Relationship not found.

---

## list_related

List all work items related to a given item.

**Parameters**:

| Name | Type    | Required | Description    |
|------|---------|----------|----------------|
| id   | integer | yes      | Work item ID   |

**Returns**: List of related item objects with fields: id, left_id,
right_id, relationship, other_id, other_title.

**Errors**: None (returns empty list if no relationships).

---

## search_work_items

Search work items by keyword across title and content.

**Parameters**:

| Name    | Type   | Required | Description                      |
|---------|--------|----------|----------------------------------|
| project | string | yes      | Project short name or numeric ID |
| query   | string | yes      | Search term                      |

**Returns**: List of matching work item summaries (same shape as
list_work_items).

**Errors**: Project not found.
