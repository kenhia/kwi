"""Project management CLI commands."""

import typer

from kwi.db import KwiConfigError, get_connection, resolve_db_url
from kwi.output import (
    render_detail,
    render_error,
    render_json,
    render_message,
    render_table,
)
from kwi.queries import get_project, insert_project, list_areas, list_projects

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


@app.command("list")
def list_projects_cmd(ctx: typer.Context) -> None:
    """List all projects."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        projects = list_projects(conn)
    if use_json:
        render_json([{"id": p.id, "project": p.project} for p in projects])
    else:
        render_table(
            ["ID", "Project"],
            [[p.id, p.project] for p in projects],
        )


@app.command("show")
def show_project(
    ctx: typer.Context,
    project: str = typer.Argument(..., help="Project short name or ID."),
) -> None:
    """Show all fields of a project."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        p = get_project(conn, project)
    if p is None:
        render_error(f"Project '{project}' not found.", use_json=use_json)
        raise typer.Exit(1)
    if use_json:
        render_json(
            {
                "id": p.id,
                "project": p.project,
                "gh_repo": p.gh_repo,
                "cn_path": p.cn_path,
                "created": p.created,
                "updated": p.updated,
                "description": p.description,
            }
        )
    else:
        render_detail(
            [
                ("ID", p.id),
                ("Project", p.project),
                ("GitHub Repo", p.gh_repo),
                ("Path", p.cn_path),
                ("Created", p.created),
                ("Updated", p.updated),
                ("Description", p.description),
            ]
        )


@app.command("add")
def add_project(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", help="Unique short name."),
    path: str = typer.Option(..., "--path", help="Canonical filesystem path."),
    repo: str | None = typer.Option(None, "--repo", help="GitHub repo URL."),
    description: str | None = typer.Option(
        None, "--description", help="Project description."
    ),
) -> None:
    """Create a new project."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        try:
            p = insert_project(
                conn,
                name=name,
                cn_path=path,
                gh_repo=repo,
                description=description,
            )
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                render_error(
                    f"Project '{name}' already exists.",
                    use_json=use_json,
                )
                raise typer.Exit(1) from e
            raise
    if use_json:
        render_json({"id": p.id, "project": p.project})
    else:
        render_message(f"Created project {p.project} (ID: {p.id})")


@app.command("areas")
def list_project_areas(
    ctx: typer.Context,
    project: str = typer.Option(..., "--project", help="Project short name or ID."),
) -> None:
    """List areas for a project."""
    db_url, use_json = _get_ctx(ctx)
    with get_connection(db_url) as conn:
        p = get_project(conn, project)
        if p is None:
            render_error(f"Project '{project}' not found.", use_json=use_json)
            raise typer.Exit(1)
        areas = list_areas(conn, p.id)
    if use_json:
        render_json(
            [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                }
                for a in areas
            ]
        )
    else:
        render_table(
            ["ID", "Area", "Description"],
            [[a.id, a.name, a.description] for a in areas],
        )
