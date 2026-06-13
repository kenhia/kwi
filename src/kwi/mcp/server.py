"""MCP tool definitions for kwi."""

import json
from dataclasses import asdict
from typing import Any

from mcp.server.fastmcp import FastMCP

from kwi.db import get_connection, resolve_db_url
from kwi.queries import (
    QueryError,
    archive_workitem,
    delete_related,
    get_project,
    get_workitem,
    insert_area,
    insert_project,
    insert_related,
    insert_workitem,
    list_workitems,
    unarchive_workitem,
    update_workitem,
)
from kwi.queries import (
    list_areas as query_list_areas,
)
from kwi.queries import (
    list_projects as query_list_projects,
)
from kwi.queries import (
    list_related as query_list_related,
)
from kwi.queries import (
    search_work_items as query_search_work_items,
)

mcp = FastMCP("kwi")


def _db_url() -> str:
    """Resolve the database URL using kwi config precedence."""
    return resolve_db_url()


def _serialize(obj: Any) -> str:
    """Serialize a dataclass or list of dataclasses to JSON."""
    if isinstance(obj, list):
        return json.dumps([asdict(o) for o in obj], default=str)
    return json.dumps(asdict(obj), default=str)


@mcp.tool()
def list_projects() -> str:
    """List all projects in the database."""
    with get_connection(_db_url()) as conn:
        projects = query_list_projects(conn)
    return _serialize(projects)


@mcp.tool()
def list_areas(project: str) -> str:
    """List areas for a given project.

    Args:
        project: Project short name or numeric ID.
    """
    with get_connection(_db_url()) as conn:
        proj = get_project(conn, project)
        if proj is None:
            return json.dumps({"error": f"Project '{project}' not found."})
        areas = query_list_areas(conn, proj.id)
    return _serialize(areas)


@mcp.tool()
def create_project(
    name: str,
    cn_path: str,
    gh_repo: str | None = None,
    description: str | None = None,
) -> str:
    """Create a new project.

    Args:
        name: Project short name (must be unique).
        cn_path: Canonical filesystem path for the project.
        gh_repo: Optional GitHub repository (owner/name).
        description: Optional project description.
    """
    with get_connection(_db_url()) as conn:
        try:
            project = insert_project(
                conn,
                name=name,
                cn_path=cn_path,
                gh_repo=gh_repo,
                description=description,
            )
        except Exception as e:  # noqa: BLE001 - surface DB/uniqueness errors as data
            return json.dumps({"error": str(e)})
    return _serialize(project)


@mcp.tool()
def create_area(
    project: str,
    name: str,
    description: str | None = None,
) -> str:
    """Create a new area under a project.

    Args:
        project: Project short name or numeric ID.
        name: Area name (must be unique within the project).
        description: Optional area description.
    """
    with get_connection(_db_url()) as conn:
        proj = get_project(conn, project)
        if proj is None:
            return json.dumps({"error": f"Project '{project}' not found."})
        try:
            area = insert_area(
                conn,
                project_id=proj.id,
                name=name,
                description=description,
            )
        except Exception as e:  # noqa: BLE001 - surface DB/uniqueness errors as data
            return json.dumps({"error": str(e)})
    return _serialize(area)


@mcp.tool()
def list_work_items(
    project: str,
    area: str | None = None,
    status: str | None = None,
    tshirt: str | None = None,
) -> str:
    """List work items with optional filters. Archived items excluded by default.

    Args:
        project: Project short name or numeric ID.
        area: Filter by area name.
        status: Filter by status (comma-separated for multiple).
        tshirt: Filter by t-shirt size.
    """
    with get_connection(_db_url()) as conn:
        proj = get_project(conn, project)
        if proj is None:
            return json.dumps({"error": f"Project '{project}' not found."})
        status_filter = [s.strip() for s in status.split(",")] if status else None
        items = list_workitems(
            conn,
            project_id=proj.id,
            area_name=area,
            status_filter=status_filter,
            tshirt_filter=tshirt,
        )
    return _serialize(items)


@mcp.tool()
def get_work_item(id: int) -> str:
    """Get full details of a single work item.

    Args:
        id: Work item ID.
    """
    with get_connection(_db_url()) as conn:
        wi = get_workitem(conn, id)
        if wi is None:
            return json.dumps({"error": f"Work item {id} not found."})
    return _serialize(wi)


@mcp.tool()
def create_work_item(
    project: str,
    title: str,
    content: str,
    area: str | None = None,
    type: str = "task",
    status: str = "open",
    tshirt: str = "Unknown",
    sprint: str | None = None,
    details: str | None = None,
    parent: int | None = None,
) -> str:
    """Create a new work item.

    Args:
        project: Project short name or numeric ID.
        title: Work item title.
        content: Markdown body.
        area: Area name.
        type: Work item type.
        status: Work item status.
        tshirt: T-shirt size.
        sprint: Sprint label.
        details: Additional markdown.
        parent: Parent work item ID.
    """
    with get_connection(_db_url()) as conn:
        try:
            wi = insert_workitem(
                conn,
                project_name=project,
                title=title,
                content=content,
                wi_type=type,
                wi_status=status,
                wi_tshirt=tshirt,
                area_name=area,
                sprint=sprint,
                details=details,
                parent_id=parent,
            )
        except QueryError as e:
            return json.dumps({"error": str(e)})
    return _serialize(wi)


@mcp.tool()
def update_work_item(
    id: int,
    title: str | None = None,
    content: str | None = None,
    details: str | None = None,
    type: str | None = None,
    status: str | None = None,
    tshirt: str | None = None,
    sprint: str | None = None,
    area: str | None = None,
    parent: int | None = None,
) -> str:
    """Update one or more fields on an existing work item.

    Args:
        id: Work item ID.
        title: New title.
        content: New markdown body.
        details: New additional markdown.
        type: New work item type.
        status: New status.
        tshirt: New t-shirt size.
        sprint: New sprint label.
        area: New area name.
        parent: New parent work item ID.
    """
    fields: dict[str, str | int | None] = {}
    if title is not None:
        fields["title"] = title
    if content is not None:
        fields["content"] = content
    if details is not None:
        fields["details"] = details
    if type is not None:
        fields["wi_type"] = type
    if status is not None:
        fields["wi_status"] = status
    if sprint is not None:
        fields["sprint"] = sprint
    if tshirt is not None:
        fields["wi_tshirt"] = tshirt
    if area is not None:
        fields["area"] = area
    if parent is not None:
        fields["parent_id"] = parent

    with get_connection(_db_url()) as conn:
        try:
            updated = update_workitem(conn, id, **fields)
        except QueryError as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"id": id, "updated_fields": updated})


@mcp.tool()
def archive_work_item(id: int) -> str:
    """Archive a work item (sets the archived flag; status is preserved).

    Args:
        id: Work item ID.
    """
    with get_connection(_db_url()) as conn:
        try:
            archive_workitem(conn, id)
        except QueryError as e:
            return json.dumps({"error": str(e)})
        wi = get_workitem(conn, id)
    return _serialize(wi)


@mcp.tool()
def unarchive_work_item(id: int) -> str:
    """Un-archive a work item (clears the archived flag; status is preserved).

    Args:
        id: Work item ID.
    """
    with get_connection(_db_url()) as conn:
        try:
            unarchive_workitem(conn, id)
        except QueryError as e:
            return json.dumps({"error": str(e)})
        wi = get_workitem(conn, id)
    return _serialize(wi)


@mcp.tool()
def relate_work_items(left_id: int, right_id: int, relationship: str) -> str:
    """Create a labeled relationship between two work items.

    Args:
        left_id: First work item ID.
        right_id: Second work item ID.
        relationship: Relationship label (e.g., 'blocks').
    """
    with get_connection(_db_url()) as conn:
        try:
            rel = insert_related(
                conn, left_id=left_id, right_id=right_id, relationship=relationship
            )
        except (QueryError, Exception) as e:
            return json.dumps({"error": str(e)})
    return json.dumps(
        {
            "id": rel.id,
            "left_id": left_id,
            "right_id": right_id,
            "relationship": relationship,
        }
    )


@mcp.tool()
def unrelate_work_items(left_id: int, right_id: int) -> str:
    """Remove a relationship between two work items.

    Args:
        left_id: First work item ID.
        right_id: Second work item ID.
    """
    with get_connection(_db_url()) as conn:
        deleted = delete_related(conn, left_id, right_id)
    if not deleted:
        return json.dumps({"error": "Relationship not found."})
    return json.dumps({"left_id": left_id, "right_id": right_id, "removed": True})


@mcp.tool()
def list_related(id: int) -> str:
    """List all work items related to a given item.

    Args:
        id: Work item ID.
    """
    with get_connection(_db_url()) as conn:
        related = query_list_related(conn, id)
    return json.dumps(related)


@mcp.tool()
def search_work_items(project: str, query: str) -> str:
    """Search work items by keyword across title and content.

    Args:
        project: Project short name or numeric ID.
        query: Search term.
    """
    with get_connection(_db_url()) as conn:
        proj = get_project(conn, project)
        if proj is None:
            return json.dumps({"error": f"Project '{project}' not found."})
        items = query_search_work_items(conn, project_id=proj.id, query=query)
    return _serialize(items)
