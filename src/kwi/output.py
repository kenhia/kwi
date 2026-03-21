"""Output rendering helpers for table and JSON output."""

import json
import sys
from typing import Any

from rich.console import Console
from rich.table import Table

err_console = Console(stderr=True)


def render_table(
    columns: list[str],
    rows: list[list[Any]],
) -> None:
    """Render rows as a Rich table to stdout."""
    console = Console()
    table = Table(show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(v) if v is not None else "" for v in row])
    console.print(table)


def render_json(data: Any) -> None:
    """Render data as JSON to stdout."""
    print(json.dumps(data, default=str))


def render_detail(pairs: list[tuple[str, Any]]) -> None:
    """Render key-value pairs for show commands."""
    console = Console()
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Key", style="bold", min_width=12)
    table.add_column("Value")
    for key, value in pairs:
        table.add_row(key, str(value) if value is not None else "")
    console.print(table)


def render_message(message: str) -> None:
    """Print a plain text message to stdout."""
    print(message)


def render_error(message: str, *, use_json: bool = False) -> None:
    """Print an error message to stderr, optionally as JSON."""
    if use_json:
        print(json.dumps({"error": message}), file=sys.stderr)
    else:
        err_console.print(f"[red]Error:[/red] {message}")
