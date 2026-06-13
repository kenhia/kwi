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


class TestWorkCLI:
    """CLI tests for work set/archive/unarchive (US1, US4, US7)."""

    def _setup_item(self, tmp_path, *, area: str | None = None):
        import uuid

        name = f"workcli-{uuid.uuid4().hex[:8]}"
        invoke("projects", "add", "--name", name, "--path", f"/tmp/{name}")
        if area:
            invoke("areas", "add", "--project", name, "--name", area)
        md = tmp_path / "item.md"
        md.write_text(
            f"---\nproject: {name}\ntitle: CLI item\ntype: task\n"
            f"status: active\nt-shirt: Unknown\n---\n\nBody\n"
        )
        result = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "add", str(md)]
        )
        assert result.exit_code == 0, result.output
        wid = json.loads(result.output)["id"]
        return name, wid

    def test_set_tshirt(self, tmp_path):
        _name, wid = self._setup_item(tmp_path)
        result = invoke("work", "set", str(wid), "--tshirt", "L")
        assert result.exit_code == 0
        show = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "show", str(wid)]
        )
        assert json.loads(show.output)["tshirt"] == "L"

    def test_set_area(self, tmp_path):
        _name, wid = self._setup_item(tmp_path, area="backend")
        result = invoke("work", "set", str(wid), "--area", "backend")
        assert result.exit_code == 0
        show = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "show", str(wid)]
        )
        assert json.loads(show.output)["area"] == "backend"

    def test_set_parent(self, tmp_path):
        _name, parent = self._setup_item(tmp_path)
        _name2, child = self._setup_item(tmp_path)
        result = invoke("work", "set", str(child), "--parent", str(parent))
        assert result.exit_code == 0
        show = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "show", str(child)]
        )
        assert json.loads(show.output)["parent_id"] == parent

    def test_archive_preserves_status(self, tmp_path):
        _name, wid = self._setup_item(tmp_path)
        result = invoke("work", "archive", str(wid))
        assert result.exit_code == 0
        show = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "show", str(wid)]
        )
        data = json.loads(show.output)
        assert data["archived"] is True
        assert data["status"] == "active"

    def test_unarchive(self, tmp_path):
        _name, wid = self._setup_item(tmp_path)
        invoke("work", "archive", str(wid))
        result = invoke("work", "unarchive", str(wid))
        assert result.exit_code == 0
        show = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "show", str(wid)]
        )
        assert json.loads(show.output)["archived"] is False

    def test_list_archived_only(self, tmp_path):
        name, wid = self._setup_item(tmp_path)
        invoke("work", "archive", str(wid))
        # Default listing hides the archived item.
        default = runner.invoke(
            app, ["--db-url", DB_URL, "--json", "work", "list", "--project", name]
        )
        assert wid not in [w["id"] for w in json.loads(default.output)]
        # --archived shows only archived items.
        archived = runner.invoke(
            app,
            [
                "--db-url",
                DB_URL,
                "--json",
                "work",
                "list",
                "--project",
                name,
                "--archived",
            ],
        )
        rows = json.loads(archived.output)
        assert [w["id"] for w in rows] == [wid]
