"""kwi CLI application entry point."""

import typer

from kwi import __version__
from kwi.cli import areas, projects, work

app = typer.Typer(
    name="kwi",
    help="Ken's Work Items — CLI for work item tracking.",
    no_args_is_help=True,
)

app.add_typer(projects.app, name="projects", help="Manage projects.")
app.add_typer(areas.app, name="areas", help="Manage areas.")
app.add_typer(work.app, name="work", help="Manage work items.")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"kwi {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON.",
    ),
    db_url: str | None = typer.Option(
        None,
        "--db-url",
        help="PostgreSQL connection URL.",
        envvar="KWI_DATABASE_URL",
    ),
) -> None:
    """Global options for kwi."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["db_url"] = db_url
