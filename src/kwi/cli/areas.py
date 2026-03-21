"""Area management CLI commands."""

import typer

from kwi.db import KwiConfigError, get_connection, resolve_db_url
from kwi.output import render_error, render_json, render_message
from kwi.queries import get_project, insert_area

app = typer.Typer(no_args_is_help=True)


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


@app.command("add")
def add_area(
    ctx: typer.Context,
    project: str = typer.Option(..., "--project", help="Project short name or ID."),
    name: str = typer.Option(..., "--name", help="Area name."),
    description: str | None = typer.Option(
        None, "--description", help="Area description."
    ),
) -> None:
    """Create a new area under a project."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        p = get_project(conn, project)
        if p is None:
            render_error(f"Project '{project}' not found.", use_json=use_json)
            raise typer.Exit(1)
        try:
            a = insert_area(
                conn,
                project_id=p.id,
                name=name,
                description=description,
            )
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                render_error(
                    f"Area '{name}' already exists in project '{p.project}'.",
                    use_json=use_json,
                )
                raise typer.Exit(1) from e
            raise
    if use_json:
        render_json({"id": a.id, "name": a.name, "project": p.project})
    else:
        render_message(f"Created area '{a.name}' in project '{p.project}' (ID: {a.id})")
