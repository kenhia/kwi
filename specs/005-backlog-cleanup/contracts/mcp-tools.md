# Contracts: MCP Tools (005-backlog-cleanup)

Surface: `src/kwi/mcp/server.py` (FastMCP). All tools return JSON strings.
Only additions/changes for this feature are listed.

## NEW: `create_project`

```python
@mcp.tool()
def create_project(
    name: str,
    cn_path: str,
    gh_repo: str | None = None,
    description: str | None = None,
) -> str
```

- **Behavior**: Wraps `queries.insert_project`. Creates the project, returns the
  serialized `Project` (id, project, cn_path, gh_repo, description, created,
  updated).
- **Errors**: Duplicate `name` (UNIQUE) → `{"error": "..."}`.
- **Maps to**: FR-013.

## NEW: `create_area`

```python
@mcp.tool()
def create_area(
    project: str,
    name: str,
    description: str | None = None,
) -> str
```

- **Behavior**: Resolves `project` (short name or numeric id) → project id, wraps
  `queries.insert_area`. Returns the serialized `Area` (id, project_id, name,
  description).
- **Errors**: Unknown project → `{"error": "..."}`; duplicate `(project_id,
  name)` (UNIQUE) → `{"error": "..."}`.
- **Maps to**: FR-014.

## CHANGED: `update_work_item`

Signature is unchanged (already accepts `tshirt`, `area`, `parent`), but the
implementation MUST now forward these into the `fields` dict so they persist:

```python
if tshirt is not None:
    fields["wi_tshirt"] = tshirt
if area is not None:
    fields["area_id"] = <resolved area id for the item's project>
if parent is not None:
    fields["parent_id"] = parent
```

- **Behavior**: Previously these three params were accepted and silently dropped
  (WI 41). Now they update the item. `area` is resolved to an `area_id`.
- **Validation**: invalid tshirt / unknown area / cycle-or-self parent →
  `{"error": "..."}` (no partial silent update).
- **Maps to**: FR-016, FR-017, FR-018.

## CHANGED: `archive_work_item`

```python
@mcp.tool()
def archive_work_item(id: int) -> str
```

- **Behavior**: Now sets `archived = true` and **preserves** the item's status
  (previously set status to `archived`). Idempotent (already archived ⇒ no-op).
- **Maps to**: FR-002, FR-005.

## NEW: `unarchive_work_item`

```python
@mcp.tool()
def unarchive_work_item(id: int) -> str
```

- **Behavior**: Sets `archived = false`, status unchanged. Idempotent
  (not archived ⇒ no-op). Returns the serialized work item.
- **Maps to**: FR-005, FR-007 (parity across surfaces).

## Serialization note

`_serialize(WorkItem)` MUST include the new `archived` boolean field.
