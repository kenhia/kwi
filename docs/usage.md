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
| status | no | open | open, active, resolved, closed, draft, archived |
| t-shirt | no | Unknown | XS, S, M, L, XL, Huge, Unknown |
| area | no | — | Area name |
| sprint | no | — | Sprint label |
| parent | no | — | Parent work item ID |

### `kwi work list --project <project>`

List work items for a project. Archived items excluded by default.

```bash
kwi work list --project kwi
kwi work list --project kwi --area backend
kwi work list --project kwi --status active
kwi work list --project kwi --status "open,active"
kwi work list --project kwi --tshirt M
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
```

### `kwi work archive <id>`

Archive a work item (sets status to "archived").

```bash
kwi work archive 42
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

The `kwi-mcp` server exposes 12 tools via the Model Context Protocol.
All tools return JSON. Errors are returned as `{"error": "message"}`.

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

Archive a work item (sets status to "archived").

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
3. Use the filter dropdowns (area, type, status, size) above
   the table to narrow results
4. Toggle "Include archived" to show/hide archived items
5. Click any row to open the detail view

### Create Work Items

1. With a project selected, click "+ New Work Item"
2. Fill in title (required), content (required), and type (required)
3. Optionally set status, t-shirt size, area, sprint, details, parent
4. Click "Create" — the new item appears in the list

### Edit Work Items

1. Open a work item's detail view
2. Click "Edit" to switch to form mode with pre-filled values
3. Modify fields and click "Save Changes"
4. Click "Cancel" to return to the detail view without saving

### Archive

1. Open a work item's detail view
2. Click "Archive" and confirm the prompt
3. The item is removed from the default list view
4. Toggle "Include archived" in the list filters to see it

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
