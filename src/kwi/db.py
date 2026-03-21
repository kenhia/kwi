"""Database connection management and config resolution."""

import os
import tomllib
from contextlib import contextmanager
from pathlib import Path

import psycopg

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "kwi" / "config.toml"


class KwiConfigError(Exception):
    """Raised when database configuration cannot be resolved."""


def resolve_db_url(
    flag_value: str | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> str:
    """Resolve database URL from flag > env > config file.

    Raises KwiConfigError with actionable message if none found.
    """
    # 1. CLI flag
    if flag_value:
        return flag_value

    # 2. Environment variable
    env_url = os.environ.get("KWI_DATABASE_URL")
    if env_url:
        return env_url

    # 3. Config file
    if config_path.is_file():
        with config_path.open("rb") as f:
            config = tomllib.load(f)
        url = config.get("database_url")
        if url:
            return url

    raise KwiConfigError(
        "No database connection configured. Use one of:\n"
        "  1. --db-url flag:           kwi --db-url postgresql://... <command>\n"
        "  2. KWI_DATABASE_URL env var: export KWI_DATABASE_URL=postgresql://...\n"
        f"  3. Config file:             {config_path}\n"
        '     with: database_url = "postgresql://..."'
    )


@contextmanager
def get_connection(db_url: str):
    """Create a psycopg connection as a context manager.

    Usage:
        with get_connection(url) as conn:
            conn.execute("SELECT ...")
    """
    conn = psycopg.connect(db_url, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()
