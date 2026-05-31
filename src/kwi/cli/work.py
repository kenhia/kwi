"""Work item management CLI commands."""

from pathlib import Path

import frontmatter
import typer

from kwi.db import KwiConfigError, get_connection, resolve_db_url
from kwi.output import (
    render_detail,
    render_error,
    render_json,
    render_message,
    render_table,
)
from kwi.queries import (
    QueryError,
    archive_workitem,
    delete_related,
    get_project,
    get_workitem,
    insert_related,
    insert_workitem,
    list_related,
    list_workitems,
    unarchive_workitem,
    update_workitem,
)

app = typer.Typer(no_args_is_help=True)

TEMPLATE_CONTENT = """\
---
project:
title:
type: idea
status: open
t-shirt: Unknown
area:
sprint:
parent:
---

"""


def _get_ctx(ctx: typer.Context) -> tuple[str, bool]:
    """Extract db_url and json flag from context."""
    obj = ctx.ensure_object(dict)
    use_json = obj.get("json", False)
    try:
        db_url = resolve_db_url(flag_value=obj.get("db_url"))
    except KwiConfigError as e:
        render_error(str(e), use_json=use_json)
        raise typer.Exit(1) from e
    return db_url, use_json


@app.command("list")
def list_work(
    ctx: typer.Context,
    project: str = typer.Option(..., "--project", help="Project short name or ID."),
    area: str | None = typer.Option(None, "--area", help="Filter by area name."),
    status: str | None = typer.Option(
        None, "--status", help="Filter by status (comma-separated)."
    ),
    tshirt: str | None = typer.Option(None, "--tshirt", help="Filter by t-shirt size."),
    archived: bool = typer.Option(
        False, "--archived", help="Show only archived work items."
    ),
) -> None:
    """List work items for a project."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        p = get_project(conn, project)
        if p is None:
            render_error(f"Project '{project}' not found.", use_json=use_json)
            raise typer.Exit(1)
        status_list = [s.strip() for s in status.split(",")] if status else None
        items = list_workitems(
            conn,
            project_id=p.id,
            area_name=area,
            status_filter=status_list,
            tshirt_filter=tshirt,
            archived_only=archived,
        )
    if use_json:
        render_json(
            [
                {
                    "id": w.id,
                    "area": w.area_name,
                    "type": w.wi_type,
                    "status": w.wi_status,
                    "title": w.title,
                }
                for w in items
            ]
        )
    else:
        render_table(
            ["ID", "Area", "Type", "Status", "Title"],
            [
                [
                    w.id,
                    w.area_name or "",
                    w.wi_type,
                    w.wi_status,
                    w.title,
                ]
                for w in items
            ],
        )


@app.command("show")
def show_work(
    ctx: typer.Context,
    id: int = typer.Argument(..., help="Work item ID."),
) -> None:
    """Show all fields of a work item."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        w = get_workitem(conn, id)
    if w is None:
        render_error(f"Work item {id} not found.", use_json=use_json)
        raise typer.Exit(1)
    if use_json:
        render_json(
            {
                "id": w.id,
                "project": w.project_name,
                "area": w.area_name,
                "type": w.wi_type,
                "status": w.wi_status,
                "tshirt": w.wi_tshirt,
                "archived": w.archived,
                "sprint": w.sprint,
                "title": w.title,
                "content": w.content,
                "details": w.details,
                "parent_id": w.parent_id,
                "created": w.created,
                "updated": w.updated,
            }
        )
    else:
        render_detail(
            [
                ("ID", w.id),
                ("Project", w.project_name),
                ("Area", w.area_name),
                ("Type", w.wi_type),
                ("Status", w.wi_status),
                ("T-Shirt", w.wi_tshirt),
                ("Archived", w.archived),
                ("Sprint", w.sprint),
                ("Title", w.title),
                ("Content", w.content),
                ("Details", w.details),
                ("Parent", w.parent_id),
                ("Created", w.created),
                ("Updated", w.updated),
            ]
        )


@app.command("add")
def add_work(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to markdown file with frontmatter."),
) -> None:
    """Create a work item from a markdown file."""
    db_url, use_json = _get_ctx(ctx)

    file_path = Path(path)
    if not file_path.exists():
        render_error(f"File not found: {path}", use_json=use_json)
        raise typer.Exit(1)

    post = frontmatter.load(str(file_path))
    meta = post.metadata

    for field in ("project", "title"):
        if not meta.get(field):
            render_error(
                f"Invalid frontmatter: missing required field '{field}'.",
                use_json=use_json,
            )
            raise typer.Exit(1)

    with get_connection(db_url) as conn:
        try:
            w = insert_workitem(
                conn,
                project_name=str(meta["project"]),
                title=str(meta["title"]),
                content=post.content or "",
                wi_type=str(meta.get("type", "idea")),
                wi_status=str(meta.get("status", "open")),
                wi_tshirt=str(meta.get("t-shirt", "Unknown")),
                area_name=str(meta["area"]) if meta.get("area") else None,
                sprint=str(meta["sprint"]) if meta.get("sprint") else None,
                details=None,
                parent_id=int(str(meta["parent"])) if meta.get("parent") else None,
            )
        except QueryError as e:
            render_error(str(e), use_json=use_json)
            raise typer.Exit(1) from e

    if use_json:
        render_json({"id": w.id, "title": w.title})
    else:
        render_message(f"Created work item {w.id}: {w.title}")


@app.command("template")
def template_work(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to create template file."),
) -> None:
    """Generate a blank work item template file."""
    file_path = Path(path)
    if not file_path.suffix:
        file_path = file_path.with_suffix(".md")

    obj = ctx.ensure_object(dict)
    use_json = obj.get("json", False)

    if file_path.exists():
        render_error(f"File already exists: {file_path}", use_json=use_json)
        raise typer.Exit(1)

    try:
        file_path.write_text(TEMPLATE_CONTENT)
    except OSError as e:
        render_error(f"{e}", use_json=use_json)
        raise typer.Exit(1) from None
    render_message(f"Created template: {file_path}")


@app.command("set")
def set_work(
    ctx: typer.Context,
    id: int = typer.Argument(..., help="Work item ID."),
    wi_type: str | None = typer.Option(None, "--type", help="New work item type."),
    status: str | None = typer.Option(None, "--status", help="New status."),
    sprint: str | None = typer.Option(None, "--sprint", help="New sprint label."),
    tshirt: str | None = typer.Option(None, "--tshirt", help="New t-shirt size."),
    area: str | None = typer.Option(None, "--area", help="New area name."),
    parent: int | None = typer.Option(None, "--parent", help="New parent ID."),
    title: str | None = typer.Option(None, "--title", help="New title."),
    content: str | None = typer.Option(
        None, "--content", help="Path to file with new content."
    ),
    details: str | None = typer.Option(
        None, "--details", help="Path to file with new details."
    ),
) -> None:
    """Update fields on an existing work item."""
    db_url, use_json = _get_ctx(ctx)

    fields: dict[str, str | int | None] = {}
    if wi_type is not None:
        fields["wi_type"] = wi_type
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
    if title is not None:
        fields["title"] = title
    if content is not None:
        cp = Path(content)
        if not cp.exists():
            render_error(f"File not found: {content}", use_json=use_json)
            raise typer.Exit(1)
        fields["content"] = cp.read_text()
    if details is not None:
        dp = Path(details)
        if not dp.exists():
            render_error(f"File not found: {details}", use_json=use_json)
            raise typer.Exit(1)
        fields["details"] = dp.read_text()

    if not fields:
        render_error(
            "No fields specified. Use --type, --status, "
            "--sprint, --tshirt, --area, --parent, "
            "--title, --content, or --details.",
            use_json=use_json,
        )
        raise typer.Exit(1)

    with get_connection(db_url) as conn:
        try:
            updated = update_workitem(conn, id, **fields)
        except QueryError as e:
            render_error(str(e), use_json=use_json)
            raise typer.Exit(1) from e

    if use_json:
        render_json({"id": id, "updated_fields": updated})
    else:
        render_message(f"Updated work item {id}.")


@app.command("archive")
def archive_work(
    ctx: typer.Context,
    id: int = typer.Argument(..., help="Work item ID."),
) -> None:
    """Archive a work item."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        try:
            archive_workitem(conn, id)
        except QueryError as e:
            render_error(str(e), use_json=use_json)
            raise typer.Exit(1) from e
    if use_json:
        render_json({"id": id, "status": "archived"})
    else:
        render_message(f"Archived work item {id}.")


@app.command("unarchive")
def unarchive_work(
    ctx: typer.Context,
    id: int = typer.Argument(..., help="Work item ID."),
) -> None:
    """Un-archive a work item."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        try:
            unarchive_workitem(conn, id)
        except QueryError as e:
            render_error(str(e), use_json=use_json)
            raise typer.Exit(1) from e
    if use_json:
        render_json({"id": id, "archived": False})
    else:
        render_message(f"Un-archived work item {id}.")


@app.command("relate")
def relate_work(
    ctx: typer.Context,
    id1: int = typer.Argument(..., help="First work item ID."),
    id2: int = typer.Argument(..., help="Second work item ID."),
    relationship: str = typer.Option(..., "--relationship", help="Relationship label."),
) -> None:
    """Create a relationship between two work items."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        try:
            r = insert_related(
                conn,
                left_id=id1,
                right_id=id2,
                relationship=relationship,
            )
        except QueryError as e:
            render_error(str(e), use_json=use_json)
            raise typer.Exit(1) from e
    if use_json:
        render_json(
            {
                "left_id": r.left_id,
                "right_id": r.right_id,
                "relationship": r.relationship,
            }
        )
    else:
        render_message(f"Related work item {id1} \u2192 {id2} ({relationship}).")


@app.command("unrelate")
def unrelate_work(
    ctx: typer.Context,
    id1: int = typer.Argument(..., help="First work item ID."),
    id2: int = typer.Argument(..., help="Second work item ID."),
) -> None:
    """Remove a relationship between two work items."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        deleted = delete_related(conn, id1, id2)
    if not deleted:
        render_error(
            f"No relationship found between {id1} and {id2}.",
            use_json=use_json,
        )
        raise typer.Exit(1)
    if use_json:
        render_json({"left_id": id1, "right_id": id2})
    else:
        render_message(f"Removed relationship between {id1} and {id2}.")


@app.command("related")
def related_work(
    ctx: typer.Context,
    id: int = typer.Argument(..., help="Work item ID."),
) -> None:
    """List all items related to a work item."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        items = list_related(conn, id)
    if use_json:
        render_json(items)
    else:
        render_table(
            ["ID", "Relationship", "Title", "Direction"],
            [
                [
                    i["id"],
                    i["relationship"],
                    i["title"],
                    "\u2192" if i["direction"] == "right" else "\u2190",
                ]
                for i in items
            ],
        )
