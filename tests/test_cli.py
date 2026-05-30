"""CLI integration tests using CliRunner (US2+)."""

import json

from typer.testing import CliRunner

from kwi.main import app

runner = CliRunner()

# Use the test database — same URL as conftest.py
DB_URL = "postgresql://ken@gratch:5432/workitems_test"


def invoke(*args: str):
    return runner.invoke(app, ["--db-url", DB_URL, *args])


class TestProjectsCLI:
    def test_projects_list(self):
        result = invoke("projects", "list")
        assert result.exit_code == 0
        assert "ID" in result.output
        assert "Project" in result.output

    def test_projects_list_json(self):
        result = runner.invoke(
            app,
            ["--db-url", DB_URL, "--json", "projects", "list"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_projects_show_not_found(self):
        result = invoke("projects", "show", "nonexistent_proj_xyz")
        assert result.exit_code == 1

    def test_projects_add_and_show(self):
        import uuid

        name = f"clitest-{uuid.uuid4().hex[:8]}"
        result = invoke(
            "projects",
            "add",
            "--name",
            name,
            "--path",
            f"/tmp/{name}",
        )
        assert result.exit_code == 0
        assert name in result.output

        # Show it
        result = invoke("projects", "show", name)
        assert result.exit_code == 0
        assert name in result.output

        # Cleanup: we can't easily delete so just verify it doesn't
        # break listing
        result = invoke("projects", "list")
        assert result.exit_code == 0

    def test_projects_areas_not_found(self):
        result = invoke("projects", "areas", "--project", "nonexistent_xyz")
        assert result.exit_code == 1


class TestAreasCLI:
    def test_areas_add_project_not_found(self):
        result = invoke(
            "areas",
            "add",
            "--project",
            "nonexistent_xyz",
            "--name",
            "test",
        )
        assert result.exit_code == 1
