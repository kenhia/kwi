# kwi CLI Reference

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
