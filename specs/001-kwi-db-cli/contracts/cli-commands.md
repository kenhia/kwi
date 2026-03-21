# CLI Command Contract: kwi

**Date**: 2026-03-21
**Feature**: 001-kwi-db-cli

## Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | Output all results as JSON |
| `--db-url` | string | none | PostgreSQL connection URL |
| `--help` | flag | — | Show help and exit |
| `--version` | flag | — | Show version and exit |

## Command Groups

### `kwi projects`

#### `kwi projects list`

List all projects.

**Arguments**: none
**Options**: none (inherits global)

**Table output**:

| Column | Source |
|--------|--------|
| ID | project.id |
| Project | project.project |

**JSON output**:
```json
[
  {"id": 1, "project": "kwi"}
]
```

**Exit codes**: 0 success

---

#### `kwi projects show <project>`

Show all fields of a project.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| project | string or int | yes | Short name or ID |

**Table output**: Key-value pairs (all project fields)

**JSON output**:
```json
{
  "id": 1,
  "project": "kwi",
  "gh_repo": "https://github.com/user/kwi",
  "cn_path": "~/src/kwi",
  "created": "2026-03-21T12:00:00Z",
  "updated": "2026-03-21T12:00:00Z",
  "description": "Ken's Work Items"
}
```

**Exit codes**: 0 success, 1 not found

**Errors**: `Project '<project>' not found.`

---

#### `kwi projects add`

Create a new project.

**Arguments**: none

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--name` | string | yes | Unique short name |
| `--path` | string | yes | Canonical filesystem path |
| `--repo` | string | no | GitHub repo URL |
| `--description` | string | no | Project description |

**Table output**: `Created project <name> (ID: <id>)`

**JSON output**:
```json
{"id": 1, "project": "kwi"}
```

**Exit codes**: 0 success, 1 duplicate name

**Errors**: `Project '<name>' already exists.`

---

#### `kwi projects areas --project <project>`

List areas for a project.

**Arguments**: none

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--project` | string or int | yes | Project short name or ID |

**Table output**:

| Column | Source |
|--------|--------|
| ID | area.id |
| Area | area.name |
| Description | area.description |

**JSON output**:
```json
[
  {"id": 1, "name": "backend", "description": "Server-side code"}
]
```

**Exit codes**: 0 success, 1 project not found

---

### `kwi areas`

#### `kwi areas add`

Create a new area under a project.

**Arguments**: none

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--project` | string or int | yes | Project short name or ID |
| `--name` | string | yes | Area name |
| `--description` | string | no | Area description |

**Table output**: `Created area '<name>' in project '<project>' (ID: <id>)`

**JSON output**:
```json
{"id": 1, "name": "backend", "project": "kwi"}
```

**Exit codes**: 0 success, 1 project not found, 1 duplicate area

**Errors**:
- `Project '<project>' not found.`
- `Area '<name>' already exists in project '<project>'.`

---

### `kwi work`

#### `kwi work list --project <project>`

List work items for a project.

**Arguments**: none

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--project` | string or int | yes | Project short name or ID |
| `--area` | string | no | Filter by area name |
| `--status` | string | no | Filter by status (comma-separated for multiple) |
| `--tshirt` | string | no | Filter by t-shirt size |

**Table output**:

| Column | Source |
|--------|--------|
| ID | workitem.id |
| Area | area.name (or blank) |
| Type | workitem_type.name |
| Status | workitem_status.name |
| Title | workitem.title |

**Default filter**: Excludes archived items unless `--status`
includes "archived".

**Sort**: By ID ascending.

**JSON output**:
```json
[
  {
    "id": 1,
    "area": "backend",
    "type": "bug",
    "status": "open",
    "title": "Fix login redirect"
  }
]
```

**Exit codes**: 0 success (empty list is success), 1 project not found

---

#### `kwi work show <id>`

Show all fields of a work item.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | int | yes | Work item ID |

**Table output**: Key-value pairs (all work item fields, with
content and details displayed as markdown text)

**JSON output**:
```json
{
  "id": 1,
  "project": "kwi",
  "area": "backend",
  "type": "bug",
  "status": "open",
  "tshirt": "M",
  "sprint": "001-kwi-db-cli",
  "title": "Fix login redirect",
  "content": "# Steps to reproduce\n...",
  "details": null,
  "parent_id": null,
  "created": "2026-03-21T12:00:00Z",
  "updated": "2026-03-21T12:00:00Z"
}
```

**Exit codes**: 0 success, 1 not found

**Errors**: `Work item <id> not found.`

---

#### `kwi work add <path>`

Create a work item from a markdown file with frontmatter.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| path | file path | yes | Path to markdown file with frontmatter |

**Frontmatter fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project | string | yes | Project short name |
| title | string | yes | Work item title |
| area | string | no | Area name |
| type | string | yes | Work item type (default: idea) |
| t-shirt | string | no | T-shirt size (default: Unknown) |
| status | string | yes | Status (default: open) |
| sprint | string | no | Sprint label |
| parent | int | no | Parent work item ID |

**Body**: Everything after the closing `---` is the `content` field.

**Table output**: `Created work item <id>: <title>`

**JSON output**:
```json
{"id": 1, "title": "Fix login redirect"}
```

**Exit codes**: 0 success, 1 validation error

**Errors**:
- `File not found: <path>`
- `Invalid frontmatter: missing required field '<field>'.`
- `Invalid type '<value>'. Valid types: bug, task, idea, ...`
- `Invalid status '<value>'. Valid statuses: open, active, ...`
- `Project '<project>' not found.`
- `Area '<area>' not found in project '<project>'.`

---

#### `kwi work template <path>`

Generate a blank work item template file.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| path | file path | yes | Path to create template (`.md` appended if missing) |

**Behavior**: Creates the file with default frontmatter and a
placeholder content section. Does not overwrite existing files.

**Exit codes**: 0 success, 1 file already exists

---

#### `kwi work set <id>`

Update one or more fields on an existing work item.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | int | yes | Work item ID |

**Options**:

| Option | Type | Description |
|--------|------|-------------|
| `--type` | string | New work item type |
| `--status` | string | New status |
| `--sprint` | string | New sprint label |
| `--title` | string | New title |
| `--content` | file path | Replace content from file |
| `--details` | file path | Replace details from file |

At least one option must be provided.

**Table output**: `Updated work item <id>.`

**JSON output**:
```json
{"id": 1, "updated_fields": ["status", "sprint"]}
```

**Exit codes**: 0 success, 1 not found, 1 validation error

**Errors**:
- `Work item <id> not found.`
- `No fields specified. Use --type, --status, --sprint, --title, --content, or --details.`
- `Invalid type/status '<value>'. Valid values: ...`

---

#### `kwi work archive <id>`

Archive a work item (set status to "archived").

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | int | yes | Work item ID |

**Table output**: `Archived work item <id>.`

**JSON output**:
```json
{"id": 1, "status": "archived"}
```

**Exit codes**: 0 success, 1 not found

---

#### `kwi work relate <id1> <id2> --relationship <text>`

Create a relationship between two work items.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id1 | int | yes | First work item ID |
| id2 | int | yes | Second work item ID |

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--relationship` | string | yes | Relationship label (e.g., "blocks", "duplicates") |

**Table output**: `Related work item <id1> → <id2> (<relationship>).`

**JSON output**:
```json
{"left_id": 1, "right_id": 2, "relationship": "blocks"}
```

**Exit codes**: 0 success, 1 not found, 1 self-reference

**Errors**:
- `Work item <id> not found.`
- `Cannot relate a work item to itself.`

---

#### `kwi work unrelate <id1> <id2>`

Remove a relationship between two work items.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id1 | int | yes | First work item ID |
| id2 | int | yes | Second work item ID |

**Table output**: `Removed relationship between <id1> and <id2>.`

**Exit codes**: 0 success, 1 no relationship found

**Errors**: `No relationship found between <id1> and <id2>.`

---

#### `kwi work related <id>`

List all items related to a work item.

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | int | yes | Work item ID |

**Table output**:

| Column | Source |
|--------|--------|
| ID | related workitem.id |
| Relationship | related.relationship |
| Title | related workitem.title |
| Direction | "→" or "←" |

**JSON output**:
```json
[
  {
    "id": 2,
    "relationship": "blocks",
    "title": "Deploy fix",
    "direction": "right"
  }
]
```

**Exit codes**: 0 success, 1 work item not found
