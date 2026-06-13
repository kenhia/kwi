# kwi Usage Reference

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--json` | Output results as JSON |
| `--db-url TEXT` | PostgreSQL connection URL (env: `KWI_DATABASE_URL`) |
| `--help` | Show help and exit |

## Projects

### `kwi projects list`

List all projects.

```bash
kwi projects list
kwi --json projects list
```

### `kwi projects show <project>`

Show all fields of a project (by name or ID).

```bash
kwi projects show kwi
kwi projects show 1
```

### `kwi projects add`

Create a new project.

```bash
kwi projects add --name kwi --path ~/src/kwi --description "Work items"
kwi projects add --name kwi --path ~/src/kwi --repo https://github.com/user/kwi
```

### `kwi projects areas --project <project>`

List areas for a project.

```bash
kwi projects areas --project kwi
```

## Areas

### `kwi areas add`

Create a new area under a project.

```bash
kwi areas add --project kwi --name backend --description "Server code"
```

## Work Items

### `kwi work template <path>`

Generate a blank work item template file. Appends `.md` if no extension.

```bash
kwi work template my-bug
# Creates my-bug.md with frontmatter template
```

### `kwi work add <path>`

Create a work item from a markdown file with YAML frontmatter.

```bash
kwi work add my-bug.md
```

**Frontmatter fields:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| project | yes | — | Project short name |
| title | yes | — | Work item title |
| type | no | idea | bug, task, idea, research, tweak, issue, feature, epic, story |
| status | no | open | open, active, resolved, closed, draft |
| t-shirt | no | Unknown | XS, S, M, L, XL, Huge, Unknown |
| area | no | — | Area name |
| sprint | no | — | Sprint label |
| parent | no | — | Parent work item ID |

### `kwi work list --project <project>`

List work items for a project. Archived items are excluded by default. Use
`--archived` to list **only** archived items (useful for finding an item's ID
to un-archive).

```bash
kwi work list --project kwi
kwi work list --project kwi --area backend
kwi work list --project kwi --status active
kwi work list --project kwi --status "open,active"
kwi work list --project kwi --tshirt M
kwi work list --project kwi --archived
```

### `kwi work show <id>`

Show all fields of a work item.

```bash
kwi work show 42
kwi --json work show 42
```

### `kwi work set <id>`

Update fields on a work item. At least one option required.

```bash
kwi work set 42 --status active
kwi work set 42 --type bug --sprint "001-kwi-db-cli"
kwi work set 42 --content path/to/new-content.md
kwi work set 42 --tshirt L
kwi work set 42 --area backend
kwi work set 42 --parent 7
```

The `--tshirt` value must be one of `XS, S, M, L, XL, Huge, Unknown`.
The `--area` value must be an existing area in the item's project.
The `--parent` value must reference an existing item and may not create a
parent cycle (an item cannot be its own ancestor). Omitted fields are left
unchanged.

### `kwi work archive <id>`

Archive a work item. This sets the `archived` flag to `true` and leaves the
item's status unchanged.

```bash
kwi work archive 42
```

### `kwi work unarchive <id>`

Restore an archived work item. Clears the `archived` flag; the status is
left unchanged.

```bash
kwi work unarchive 42
```

### `kwi work relate <id1> <id2> --relationship <text>`

Create a relationship between two work items.

```bash
kwi work relate 1 2 --relationship "blocks"
```

### `kwi work unrelate <id1> <id2>`

Remove a relationship between two work items.

```bash
kwi work unrelate 1 2
```

### `kwi work related <id>`

List all items related to a work item.

```bash
kwi work related 1
```

## MCP Server Tools

The `kwi-mcp` server exposes 15 tools via the Model Context Protocol.
All tools return JSON. Errors are returned as `{"error": "message"}`.

### `create_project`

Create a new project.

| Parameter   | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| name        | string | yes      | Project short name             |
| cn_path     | string | yes      | Canonical filesystem path      |
| gh_repo     | string | no       | GitHub repo (owner/name)       |
| description | string | no       | Project description            |

### `create_area`

Create a new area within a project.

| Parameter   | Type   | Required | Description                      |
|-------------|--------|----------|----------------------------------|
| project     | string | yes      | Project short name or numeric ID |
| name        | string | yes      | Area name                        |
| description | string | no       | Area description                 |

### `list_projects`

List all projects. No parameters.

### `list_areas`

List areas for a project.

| Parameter | Type   | Required | Description                      |
|-----------|--------|----------|----------------------------------|
| project   | string | yes      | Project short name or numeric ID |

### `list_work_items`

List work items with optional filters. Archived excluded by default.

| Parameter | Type   | Required | Description                       |
|-----------|--------|----------|-----------------------------------|
| project   | string | yes      | Project short name or numeric ID  |
| area      | string | no       | Filter by area name               |
| status    | string | no       | Filter by status (comma-separated)|
| tshirt    | string | no       | Filter by t-shirt size            |

### `get_work_item`

Get full details of a single work item.

| Parameter | Type    | Required | Description  |
|-----------|---------|----------|--------------|
| id        | integer | yes      | Work item ID |

### `create_work_item`

Create a new work item.

| Parameter | Type    | Required | Default   | Description              |
|-----------|---------|----------|-----------|--------------------------|
| project   | string  | yes      |           | Project short name or ID |
| title     | string  | yes      |           | Work item title          |
| content   | string  | yes      |           | Markdown body            |
| area      | string  | no       | null      | Area name                |
| type      | string  | no       | task      | Work item type           |
| status    | string  | no       | open      | Status                   |
| tshirt    | string  | no       | Unknown   | T-shirt size             |
| sprint    | string  | no       | null      | Sprint label             |
| details   | string  | no       | null      | Additional markdown      |
| parent    | integer | no       | null      | Parent work item ID      |

### `update_work_item`

Update one or more fields on an existing work item.

| Parameter | Type    | Required | Description              |
|-----------|---------|----------|--------------------------|
| id        | integer | yes      | Work item ID             |
| title     | string  | no       | New title                |
| content   | string  | no       | New markdown body        |
| details   | string  | no       | New additional markdown  |
| type      | string  | no       | New work item type       |
| status    | string  | no       | New status               |
| tshirt    | string  | no       | New t-shirt size         |
| sprint    | string  | no       | New sprint label         |
| area      | string  | no       | New area name            |
| parent    | integer | no       | New parent work item ID  |

### `archive_work_item`

Archive a work item. Sets the `archived` flag to `true` and preserves the
item's status. The serialized result includes `archived`.

| Parameter | Type    | Required | Description  |
|-----------|---------|----------|--------------|
| id        | integer | yes      | Work item ID |

### `unarchive_work_item`

Restore an archived work item. Clears the `archived` flag and preserves the
item's status.

| Parameter | Type    | Required | Description  |
|-----------|---------|----------|--------------|
| id        | integer | yes      | Work item ID |

### `relate_work_items`

Create a relationship between two work items.

| Parameter    | Type    | Required | Description                  |
|--------------|---------|----------|------------------------------|
| left_id      | integer | yes      | First work item ID           |
| right_id     | integer | yes      | Second work item ID          |
| relationship | string  | yes      | Relationship label           |

### `unrelate_work_items`

Remove a relationship between two work items.

| Parameter | Type    | Required | Description        |
|-----------|---------|----------|--------------------|
| left_id   | integer | yes      | First work item ID |
| right_id  | integer | yes      | Second work item ID|

### `list_related`

List all work items related to a given item.

| Parameter | Type    | Required | Description  |
|-----------|---------|----------|--------------|
| id        | integer | yes      | Work item ID |

### `search_work_items`

Search work items by keyword across title and content.

| Parameter | Type   | Required | Description                      |
|-----------|--------|----------|----------------------------------|
| project   | string | yes      | Project short name or numeric ID |
| query     | string | yes      | Search term                      |

## Desktop GUI (kwi-ui)

Launch the GUI with `npm run tauri dev` (development) or run
the built binary directly.

### Browse

1. Projects appear in the left sidebar, sorted alphabetically
2. Click a project to see its work items in a table
3. A collapsible "Project Details" section shows the project's short name,
   CN path, GitHub repo (if set), and description (if set)
4. Use the multi-select filter dropdowns (area, type, status, size, sprint)
   above the table to narrow results — each filter opens a checkbox list
   supporting multiple selections, with "Select All" and "Clear All" actions.
   The sprint filter lists each distinct sprint plus an "Unassigned" bucket
   for items with no sprint.
5. By default, every filter value is selected except the `closed` status,
   which is hidden on first load. Archived items are hidden regardless of
   status. A filter whose selection differs from its default shows a small
   dot cue on its dropdown button.
6. Filter selections are sticky for the session — navigating to a detail
   view and back preserves them (they are not persisted to disk).
7. Click any row to open the detail view
8. Click the ↻ button next to "Projects" to refresh the project list
9. Click the ↻ button next to "+ New Work Item" to refresh the work item list

### Create Work Items

1. With a project selected, click "+ New Work Item"
2. Fill in title (required) and type (required, defaults to "issue")
3. Status defaults to "open", size defaults to "S"
4. Optionally set area, sprint, parent, then fill in content (required) and details
5. Click "Create" — the new item appears in the list

### Edit Work Items

1. Open a work item's detail view
2. Click "Edit" to switch to form mode with pre-filled values
3. Modify fields and click "Save Changes" (available at both top and bottom of the form)
4. Click "Cancel" to return to the detail view without saving

### Archive

1. Open a work item's detail view
2. Click "Archive" — the item is archived immediately (no confirmation prompt)
3. The item is hidden from the list because archived items are excluded by
   default
4. To restore it, open the archived item's detail view and click
   "Un-archive"; its status is preserved throughout

### Search

1. Use the search bar at the top of the main panel
2. Type at least 2 characters to trigger search
3. Results appear in a dropdown — click one to view its details
4. Search is scoped to the currently selected project

### Relationships

1. Open a work item's detail view
2. The "Relationships" section shows related items
3. Click "+ Add" to relate another item by ID and label
4. Click "×" to remove a relationship
5. Click a related item to navigate to it

### Manage Projects and Areas

1. Click "+" in the sidebar header to add a new project
2. Click the "◆" icon next to a project to add an area

### Window Management

The window size and position are persisted automatically across sessions.
A minimum window size of 640×480 is enforced to prevent unusable layouts.
