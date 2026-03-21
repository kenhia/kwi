"""Shared pytest fixtures for kwi tests."""

import asyncio
import json
import os
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import psycopg
import pytest
from typer.testing import CliRunner

from kwi.main import app
from kwi.mcp.server import mcp as mcp_server_instance

MIGRATION_DIR = Path(__file__).resolve().parent.parent / "migrations"


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CliRunner for CLI integration tests."""
    return CliRunner()


@pytest.fixture
def cli_invoke(cli_runner: CliRunner):
    """Return a callable that invokes the kwi CLI app."""

    def _invoke(*args: str, **kwargs):
        return cli_runner.invoke(app, list(args), **kwargs)

    return _invoke


def _get_test_db_url() -> str:
    """Resolve the test database URL from env or default."""
    return os.environ.get(
        "KWI_TEST_DATABASE_URL",
        "postgresql://ken:gUW%40Hfm5Cn%26%21IwEn@gratch:5432/workitems",
    )


@pytest.fixture(scope="session")
def db_url() -> str:
    """Return the test database connection URL."""
    return _get_test_db_url()


@pytest.fixture(scope="session")
def db_session(db_url: str):
    """Provide a psycopg connection for the test session.

    Applies the initial migration once, then yields the connection.
    The connection auto-commits so each test can see prior state.
    """
    conn = psycopg.connect(db_url, autocommit=True)
    # Apply migrations
    for sql_file in sorted(MIGRATION_DIR.glob("*.sql")):
        conn.execute(sql_file.read_text())  # type: ignore[arg-type]
    yield conn
    conn.close()


@pytest.fixture
def db(db_session):
    """Provide a per-test database connection that rolls back after each test.

    Uses a savepoint so tests are isolated without re-applying migrations.
    """
    db_session.autocommit = False
    db_session.execute("BEGIN")
    yield db_session
    db_session.execute("ROLLBACK")
    db_session.autocommit = True


@pytest.fixture
def sample_project(db):
    """Insert a sample project and return its row as a dict."""
    cur = db.execute(
        """
        INSERT INTO project (project, cn_path, description)
        VALUES ('testproj', '/tmp/testproj', 'A test project')
        ON CONFLICT DO NOTHING
        RETURNING id, project, cn_path, description
        """
    )
    row = cur.fetchone()
    if row is None:
        cur = db.execute(
            "SELECT id, project, cn_path, description"
            " FROM project WHERE project = 'testproj'"
        )
        row = cur.fetchone()
    return {
        "id": row[0],
        "project": row[1],
        "cn_path": row[2],
        "description": row[3],
    }


@pytest.fixture
def sample_area(db, sample_project):
    """Insert a sample area under the sample project and return its row as a dict."""
    cur = db.execute(
        """
        INSERT INTO area (project_id, name, description)
        VALUES (%s, 'testarea', 'A test area')
        ON CONFLICT DO NOTHING
        RETURNING id, project_id, name, description
        """,
        (sample_project["id"],),
    )
    row = cur.fetchone()
    if row is None:
        cur = db.execute(
            "SELECT id, project_id, name, description"
            " FROM area"
            " WHERE project_id = %s AND name = 'testarea'",
            (sample_project["id"],),
        )
        row = cur.fetchone()
    return {
        "id": row[0],
        "project_id": row[1],
        "name": row[2],
        "description": row[3],
    }


# --- MCP fixtures ---


@pytest.fixture
def mcp_instance():
    """Return the FastMCP server instance for direct testing."""
    return mcp_server_instance


@pytest.fixture
def call_tool(mcp_instance, db):
    """Return a helper that calls an MCP tool using the test DB connection.

    Patches get_connection to reuse the test's rolled-back transaction
    so MCP tool calls don't modify the real database.
    """

    @contextmanager
    def _fake_connection(_url):
        yield db

    def _call(name: str, arguments: dict | None = None):
        with patch("kwi.mcp.server.get_connection", _fake_connection):
            raw = asyncio.run(mcp_instance.call_tool(name, arguments or {}))
        # call_tool returns (list[TextContent], dict); extract text from first content
        content_list = raw[0] if isinstance(raw, tuple) else raw
        text = content_list[0].text
        return json.loads(text)

    return _call


@pytest.fixture
def list_tools(mcp_instance):
    """Return a helper that lists all registered MCP tools."""

    def _list():
        return asyncio.run(mcp_instance.list_tools())

    return _list
