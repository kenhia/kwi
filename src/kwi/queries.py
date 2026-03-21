"""SQL query functions for kwi entities."""

import psycopg

from kwi.models import Area, Project, Related, WorkItem


def insert_project(
    conn: psycopg.Connection,
    *,
    name: str,
    cn_path: str,
    gh_repo: str | None = None,
    description: str | None = None,
) -> Project:
    """Insert a new project and return it."""
    cur = conn.execute(
        "INSERT INTO project (project, cn_path, gh_repo, description) "
        "VALUES (%s, %s, %s, %s) "
        "RETURNING id, project, cn_path, gh_repo, description, "
        "created, updated",
        (name, cn_path, gh_repo, description),
    )
    row = cur.fetchone()
    assert row is not None
    return Project(
        id=row[0],
        project=row[1],
        cn_path=row[2],
        gh_repo=row[3],
        description=row[4],
        created=row[5],
        updated=row[6],
    )


def list_projects(conn: psycopg.Connection) -> list[Project]:
    """Return all projects ordered by ID."""
    cur = conn.execute(
        "SELECT id, project, cn_path, gh_repo, description, "
        "created, updated FROM project ORDER BY id"
    )
    return [
        Project(
            id=r[0],
            project=r[1],
            cn_path=r[2],
            gh_repo=r[3],
            description=r[4],
            created=r[5],
            updated=r[6],
        )
        for r in cur.fetchall()
    ]


def get_project(conn: psycopg.Connection, identifier: str) -> Project | None:
    """Get a project by name or numeric ID. Returns None if not found."""
    try:
        pid = int(identifier)
        cur = conn.execute(
            "SELECT id, project, cn_path, gh_repo, description, "
            "created, updated FROM project WHERE id = %s",
            (pid,),
        )
    except ValueError:
        cur = conn.execute(
            "SELECT id, project, cn_path, gh_repo, description, "
            "created, updated FROM project WHERE project = %s",
            (identifier,),
        )
    row = cur.fetchone()
    if row is None:
        return None
    return Project(
        id=row[0],
        project=row[1],
        cn_path=row[2],
        gh_repo=row[3],
        description=row[4],
        created=row[5],
        updated=row[6],
    )


def insert_area(
    conn: psycopg.Connection,
    *,
    project_id: int,
    name: str,
    description: str | None = None,
) -> Area:
    """Insert a new area and return it."""
    cur = conn.execute(
        "INSERT INTO area (project_id, name, description) "
        "VALUES (%s, %s, %s) "
        "RETURNING id, project_id, name, description",
        (project_id, name, description),
    )
    row = cur.fetchone()
    assert row is not None
    return Area(
        id=row[0],
        project_id=row[1],
        name=row[2],
        description=row[3],
    )


def list_areas(conn: psycopg.Connection, project_id: int) -> list[Area]:
    """Return all areas for a project ordered by ID."""
    cur = conn.execute(
        "SELECT id, project_id, name, description "
        "FROM area WHERE project_id = %s ORDER BY id",
        (project_id,),
    )
    return [
        Area(id=r[0], project_id=r[1], name=r[2], description=r[3])
        for r in cur.fetchall()
    ]


# --- Work item queries ---


def _resolve_type_id(conn: psycopg.Connection, type_name: str) -> int | None:
    """Resolve a workitem_type name to its ID."""
    cur = conn.execute(
        "SELECT id FROM workitem_type WHERE name = %s",
        (type_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _resolve_status_id(conn: psycopg.Connection, status_name: str) -> int | None:
    """Resolve a workitem_status name to its ID."""
    cur = conn.execute(
        "SELECT id FROM workitem_status WHERE name = %s",
        (status_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _resolve_area_id(
    conn: psycopg.Connection, project_id: int, area_name: str
) -> int | None:
    """Resolve an area name to its ID within a project."""
    cur = conn.execute(
        "SELECT id FROM area WHERE project_id = %s AND name = %s",
        (project_id, area_name),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_valid_types(conn: psycopg.Connection) -> list[str]:
    """Return all valid workitem type names."""
    cur = conn.execute("SELECT name FROM workitem_type ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def get_valid_statuses(conn: psycopg.Connection) -> list[str]:
    """Return all valid workitem status names."""
    cur = conn.execute("SELECT name FROM workitem_status ORDER BY name")
    return [r[0] for r in cur.fetchall()]


class QueryError(Exception):
    """Raised when a query validation fails."""


def insert_workitem(
    conn: psycopg.Connection,
    *,
    project_name: str,
    title: str,
    content: str,
    wi_type: str = "idea",
    wi_status: str = "open",
    wi_tshirt: str = "Unknown",
    area_name: str | None = None,
    sprint: str | None = None,
    details: str | None = None,
    parent_id: int | None = None,
) -> WorkItem:
    """Insert a new work item and return it."""
    # Resolve project
    project = get_project(conn, project_name)
    if project is None:
        raise QueryError(f"Project '{project_name}' not found.")

    # Resolve type
    type_id = _resolve_type_id(conn, wi_type)
    if type_id is None:
        valid = get_valid_types(conn)
        raise QueryError(f"Invalid type '{wi_type}'. Valid types: {', '.join(valid)}")

    # Resolve status
    status_id = _resolve_status_id(conn, wi_status)
    if status_id is None:
        valid = get_valid_statuses(conn)
        raise QueryError(
            f"Invalid status '{wi_status}'. Valid statuses: {', '.join(valid)}"
        )

    # Resolve area
    area_id = None
    if area_name:
        area_id = _resolve_area_id(conn, project.id, area_name)
        if area_id is None:
            raise QueryError(
                f"Area '{area_name}' not found in project '{project.project}'."
            )

    cur = conn.execute(
        "INSERT INTO workitem "
        "(project_id, area_id, wi_type_id, wi_status_id, "
        "wi_tshirt, sprint, title, content, details, parent_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING id, created, updated",
        (
            project.id,
            area_id,
            type_id,
            status_id,
            wi_tshirt,
            sprint,
            title,
            content,
            details,
            parent_id,
        ),
    )
    row = cur.fetchone()
    assert row is not None
    return WorkItem(
        id=row[0],
        project_id=project.id,
        project_name=project.project,
        title=title,
        content=content,
        wi_type=wi_type,
        wi_status=wi_status,
        wi_tshirt=wi_tshirt,
        area_id=area_id,
        area_name=area_name,
        sprint=sprint,
        details=details,
        parent_id=parent_id,
        created=row[1],
        updated=row[2],
    )


def list_workitems(
    conn: psycopg.Connection,
    *,
    project_id: int,
    area_name: str | None = None,
    status_filter: list[str] | None = None,
    tshirt_filter: str | None = None,
) -> list[WorkItem]:
    """List work items for a project with optional filters."""
    query = (
        "SELECT w.id, a.name, t.name, s.name, w.title, "
        "w.wi_tshirt, w.sprint, w.content, w.details, "
        "w.parent_id, w.created, w.updated, "
        "w.project_id, w.area_id "
        "FROM workitem w "
        "JOIN workitem_type t ON w.wi_type_id = t.id "
        "JOIN workitem_status s ON w.wi_status_id = s.id "
        "LEFT JOIN area a ON w.area_id = a.id "
        "WHERE w.project_id = %s"
    )
    params: list = [project_id]

    # Exclude archived by default
    if status_filter:
        placeholders = ", ".join(["%s"] * len(status_filter))
        query += f" AND s.name IN ({placeholders})"
        params.extend(status_filter)
    else:
        query += " AND s.name != 'archived'"

    if area_name:
        query += " AND a.name = %s"
        params.append(area_name)

    if tshirt_filter:
        query += " AND w.wi_tshirt = %s"
        params.append(tshirt_filter)

    query += " ORDER BY w.id ASC"

    cur = conn.execute(query, params)  # type: ignore[arg-type]
    return [
        WorkItem(
            id=r[0],
            area_name=r[1],
            wi_type=r[2],
            wi_status=r[3],
            title=r[4],
            wi_tshirt=r[5],
            sprint=r[6],
            content=r[7],
            details=r[8],
            parent_id=r[9],
            created=r[10],
            updated=r[11],
            project_id=r[12],
            area_id=r[13],
        )
        for r in cur.fetchall()
    ]


def get_workitem(conn: psycopg.Connection, workitem_id: int) -> WorkItem | None:
    """Get a single work item by ID with resolved names."""
    cur = conn.execute(
        "SELECT w.id, p.project, a.name, t.name, s.name, "
        "w.wi_tshirt, w.sprint, w.title, w.content, "
        "w.details, w.parent_id, w.created, w.updated, "
        "w.project_id, w.area_id "
        "FROM workitem w "
        "JOIN project p ON w.project_id = p.id "
        "JOIN workitem_type t ON w.wi_type_id = t.id "
        "JOIN workitem_status s ON w.wi_status_id = s.id "
        "LEFT JOIN area a ON w.area_id = a.id "
        "WHERE w.id = %s",
        (workitem_id,),
    )
    r = cur.fetchone()
    if r is None:
        return None
    return WorkItem(
        id=r[0],
        project_name=r[1],
        area_name=r[2],
        wi_type=r[3],
        wi_status=r[4],
        wi_tshirt=r[5],
        sprint=r[6],
        title=r[7],
        content=r[8],
        details=r[9],
        parent_id=r[10],
        created=r[11],
        updated=r[12],
        project_id=r[13],
        area_id=r[14],
    )


def update_workitem(
    conn: psycopg.Connection,
    workitem_id: int,
    **fields: str | int | None,
) -> list[str]:
    """Update fields on a work item. Returns list of updated field names."""
    # Verify work item exists
    existing = get_workitem(conn, workitem_id)
    if existing is None:
        raise QueryError(f"Work item {workitem_id} not found.")

    set_clauses = []
    params: list = []
    updated_fields: list[str] = []

    field_map = {
        "wi_type": "wi_type_id",
        "wi_status": "wi_status_id",
        "sprint": "sprint",
        "title": "title",
        "content": "content",
        "details": "details",
    }

    for field_name, value in fields.items():
        if value is None:
            continue

        if field_name == "wi_type":
            type_id = _resolve_type_id(conn, str(value))
            if type_id is None:
                valid = get_valid_types(conn)
                raise QueryError(
                    f"Invalid type '{value}'. Valid types: {', '.join(valid)}"
                )
            set_clauses.append("wi_type_id = %s")
            params.append(type_id)
            updated_fields.append("type")
        elif field_name == "wi_status":
            status_id = _resolve_status_id(conn, str(value))
            if status_id is None:
                valid = get_valid_statuses(conn)
                raise QueryError(
                    f"Invalid status '{value}'. Valid statuses: {', '.join(valid)}"
                )
            set_clauses.append("wi_status_id = %s")
            params.append(status_id)
            updated_fields.append("status")
        elif field_name in field_map:
            col = field_map[field_name]
            set_clauses.append(f"{col} = %s")
            params.append(value)
            updated_fields.append(field_name)

    if not set_clauses:
        return []

    set_clauses.append("updated = NOW()")
    params.append(workitem_id)

    sql = f"UPDATE workitem SET {', '.join(set_clauses)} WHERE id = %s"
    conn.execute(sql, params)  # type: ignore[arg-type]
    return updated_fields


def archive_workitem(conn: psycopg.Connection, workitem_id: int) -> None:
    """Set a work item's status to 'archived'."""
    existing = get_workitem(conn, workitem_id)
    if existing is None:
        raise QueryError(f"Work item {workitem_id} not found.")

    status_id = _resolve_status_id(conn, "archived")
    assert status_id is not None
    conn.execute(
        "UPDATE workitem SET wi_status_id = %s, updated = NOW() WHERE id = %s",
        (status_id, workitem_id),
    )


# --- Related item queries ---


def insert_related(
    conn: psycopg.Connection,
    *,
    left_id: int,
    right_id: int,
    relationship: str,
) -> Related:
    """Create a relationship between two work items."""
    if left_id == right_id:
        raise QueryError("Cannot relate a work item to itself.")

    # Verify both exist
    if get_workitem(conn, left_id) is None:
        raise QueryError(f"Work item {left_id} not found.")
    if get_workitem(conn, right_id) is None:
        raise QueryError(f"Work item {right_id} not found.")

    cur = conn.execute(
        "INSERT INTO related (left_id, right_id, relationship) "
        "VALUES (%s, %s, %s) RETURNING id",
        (left_id, right_id, relationship),
    )
    row = cur.fetchone()
    assert row is not None
    return Related(
        id=row[0],
        left_id=left_id,
        right_id=right_id,
        relationship=relationship,
    )


def delete_related(conn: psycopg.Connection, left_id: int, right_id: int) -> bool:
    """Remove a relationship. Returns True if deleted, False if not found."""
    cur = conn.execute(
        "DELETE FROM related "
        "WHERE (left_id = %s AND right_id = %s) "
        "OR (left_id = %s AND right_id = %s) "
        "RETURNING id",
        (left_id, right_id, right_id, left_id),
    )
    return cur.fetchone() is not None


def list_related(conn: psycopg.Connection, workitem_id: int) -> list[dict]:
    """List all items related to a work item (bidirectional)."""
    cur = conn.execute(
        "SELECT r.id, r.left_id, r.right_id, r.relationship, "
        "w.title "
        "FROM related r "
        "JOIN workitem w ON w.id = CASE "
        "  WHEN r.left_id = %s THEN r.right_id "
        "  ELSE r.left_id END "
        "WHERE r.left_id = %s OR r.right_id = %s "
        "ORDER BY r.id",
        (workitem_id, workitem_id, workitem_id),
    )
    results = []
    for r in cur.fetchall():
        related_id = r[2] if r[1] == workitem_id else r[1]
        direction = "right" if r[1] == workitem_id else "left"
        results.append(
            {
                "id": related_id,
                "relationship": r[3],
                "title": r[4],
                "direction": direction,
            }
        )
    return results
