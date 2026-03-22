---
name: kwi-workitems
description: Manage work items using kwi MCP tools. Use when creating, reading, updating,
  or tracking bugs, issues, and tasks. Handles bidirectional linking between workitems
  and repo spec/task files.
compatibility: Requires kwi MCP server configured in .vscode/mcp.json
metadata:
  author: kwi
  source: manual
---

# kwi Work Item Management Skill

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Available MCP Tools

All workitem operations use the `mcp_kwi_*` tools:

| Tool | Purpose | Required Params |
|------|---------|-----------------|
| `mcp_kwi_list_projects` | List all projects | (none) |
| `mcp_kwi_list_areas` | List areas in a project | `project` |
| `mcp_kwi_list_work_items` | List workitems with filters | `project` (+ optional: `area`, `status`, `type`, `sprint`) |
| `mcp_kwi_get_work_item` | Get full workitem detail | `id` |
| `mcp_kwi_create_work_item` | Create a new workitem | `project`, `area`, `title`, `type`, `status` (+ optional: `content`, `details`, `tshirt`, `sprint`) |
| `mcp_kwi_update_work_item` | Update workitem fields | `id` (+ optional: `title`, `content`, `details`, `status`, `type`, `tshirt`, `sprint`, `area`) |
| `mcp_kwi_archive_work_item` | Archive (soft-delete) a workitem | `id` |
| `mcp_kwi_search_work_items` | Full-text search | `project`, `query` |
| `mcp_kwi_list_related` | List related workitems | `id` |
| `mcp_kwi_relate_work_items` | Create a relationship | `left_id`, `right_id`, `relationship` |
| `mcp_kwi_unrelate_work_items` | Remove a relationship | `left_id`, `right_id` |

## Conventions

### Project

Use the repository folder name as the project name (e.g., `kwi` for
`/home/ken/src/kwi`). If the project doesn't exist yet, create it
first using the CLI: `uv run kwi project add <name> --path <path>`.

### Areas

Areas group workitems by component. For kwi:
- `cli` — Command Line Interface
- `mcp` — kwi-mcp agent interface
- `gui` — kwi-ui desktop GUI

### Work Item Types

- `bug` — Something is broken
- `issue` — Enhancement, question, or general issue

### Status Lifecycle

```
draft → open → active → resolved → closed
```

- **draft**: Incomplete idea or needs research before actionable
- **open**: Ready for work (default for new items)
- **active**: Currently being worked on
- **resolved**: Fix implemented, awaiting verification
- **closed**: Done

### Sprint

Set `sprint` to the current branch name if the item will likely be
completed in the current iteration (e.g., `003-kwi-ui`). Leave blank
if the timeline is uncertain.

### T-Shirt Sizing

- `XS`, `S`, `M`, `L`, `XL`, `Huge`, `Unknown`

## Workflow: Creating a Work Item

1. **Determine project and area** from the workspace context:
   - Project = repo folder name
   - Area = component being affected

2. **Create the workitem** via MCP:
   ```
   mcp_kwi_create_work_item(
     project=<project>,
     area=<area>,
     title=<concise title>,
     type=<bug|issue>,
     status=<open|draft>,
     content=<detailed description>,
     tshirt=<size>,
     sprint=<branch or blank>
   )
   ```

3. **Add tasks to the supplemental spec** at `specs/supplemental-spec.md`:
   - Create a section with format: `## S###: <title> (WI #<id>)`
   - Include type, status, size, sprint
   - Define acceptance criteria
   - List tasks as `ST###` items with `(WI #<id>)` suffix

4. **Update the workitem details** with tracking info:
   ```
   mcp_kwi_update_work_item(
     id=<id>,
     details="Tracking: specs/supplemental-spec.md § S###, Tasks: ST###-ST###"
   )
   ```

5. **Relate** overlapping workitems:
   ```
   mcp_kwi_relate_work_items(left_id=<id1>, right_id=<id2>, relationship="related")
   ```

## Workflow: Updating Work Item Status

When starting work:
```
mcp_kwi_update_work_item(id=<id>, status="active")
```

When implementation is done:
```
mcp_kwi_update_work_item(id=<id>, status="resolved")
```

After verification:
```
mcp_kwi_update_work_item(id=<id>, status="closed")
```

## Workflow: Checking Current Work

1. List active items: `mcp_kwi_list_work_items(project=<p>, status="active")`
2. For each, read `details` field for tracking info (spec section + task IDs)
3. Check task completion in `specs/supplemental-spec.md`

## Known Issues

(none currently)
