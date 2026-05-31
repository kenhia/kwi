"""Tests for the kwi MCP server tools."""

import pytest


class TestServerInit:
    """Smoke tests for MCP server initialization."""

    def test_server_has_name(self, mcp_instance):
        assert mcp_instance.name == "kwi"

    def test_list_tools_returns_list(self, list_tools):
        tools = list_tools()
        assert isinstance(tools, list)


class TestListProjects:
    """Tests for the list_projects MCP tool."""

    def test_returns_projects(self, call_tool, sample_project):
        result = call_tool("list_projects")
        assert isinstance(result, list)
        names = [p["project"] for p in result]
        assert "testproj" in names

    def test_project_has_expected_fields(self, call_tool, sample_project):
        result = call_tool("list_projects")
        proj = next(p for p in result if p["project"] == "testproj")
        assert "id" in proj
        assert "cn_path" in proj
        assert "description" in proj


class TestListAreas:
    """Tests for the list_areas MCP tool."""

    def test_returns_areas_for_project(self, call_tool, sample_area):
        result = call_tool("list_areas", {"project": "testproj"})
        assert isinstance(result, list)
        assert len(result) >= 1
        names = [a["name"] for a in result]
        assert "testarea" in names

    def test_invalid_project_returns_error(self, call_tool, db):
        result = call_tool("list_areas", {"project": "nonexistent"})
        assert "error" in result


class TestCreateProject:
    """Tests for the create_project MCP tool."""

    def test_create_succeeds(self, call_tool, db):
        result = call_tool(
            "create_project",
            {"name": "mcpproj", "cn_path": "/tmp/mcpproj"},
        )
        assert "error" not in result
        assert result["project"] == "mcpproj"
        assert "id" in result

    def test_duplicate_name_returns_error(self, call_tool, db):
        call_tool("create_project", {"name": "dupproj", "cn_path": "/tmp/dp"})
        result = call_tool("create_project", {"name": "dupproj", "cn_path": "/tmp/dp2"})
        assert "error" in result


class TestCreateArea:
    """Tests for the create_area MCP tool."""

    def test_create_succeeds(self, call_tool, db, sample_project):
        result = call_tool(
            "create_area",
            {"project": "testproj", "name": "mcparea"},
        )
        assert "error" not in result
        assert result["name"] == "mcparea"

    def test_unknown_project_returns_error(self, call_tool, db):
        result = call_tool("create_area", {"project": "nonexistent", "name": "x"})
        assert "error" in result

    def test_duplicate_area_returns_error(self, call_tool, db, sample_project):
        call_tool("create_area", {"project": "testproj", "name": "dupar"})
        result = call_tool("create_area", {"project": "testproj", "name": "dupar"})
        assert "error" in result


class TestListWorkItems:
    """Tests for the list_work_items MCP tool."""

    def test_returns_work_items(self, call_tool, db, sample_project, sample_area):
        # Insert a work item directly
        from kwi.queries import insert_workitem

        insert_workitem(
            db,
            project_name="testproj",
            title="Test item",
            content="Body text",
        )
        result = call_tool("list_work_items", {"project": "testproj"})
        assert isinstance(result, list)
        assert len(result) >= 1
        titles = [w["title"] for w in result]
        assert "Test item" in titles

    def test_status_filter(self, call_tool, db, sample_project, sample_area):
        from kwi.queries import insert_workitem

        insert_workitem(
            db,
            project_name="testproj",
            title="Open item",
            content="open",
            wi_status="open",
        )
        insert_workitem(
            db,
            project_name="testproj",
            title="Closed item",
            content="closed",
            wi_status="closed",
        )
        result = call_tool(
            "list_work_items", {"project": "testproj", "status": "closed"}
        )
        titles = [w["title"] for w in result]
        assert "Closed item" in titles
        assert "Open item" not in titles

    def test_area_filter(self, call_tool, db, sample_project, sample_area):
        from kwi.queries import insert_workitem

        insert_workitem(
            db,
            project_name="testproj",
            title="In area",
            content="area",
            area_name="testarea",
        )
        insert_workitem(
            db,
            project_name="testproj",
            title="No area",
            content="none",
        )
        result = call_tool(
            "list_work_items", {"project": "testproj", "area": "testarea"}
        )
        titles = [w["title"] for w in result]
        assert "In area" in titles
        assert "No area" not in titles

    def test_archived_excluded_by_default(
        self, call_tool, db, sample_project, sample_area
    ):
        from kwi.queries import archive_workitem, insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="Archived item",
            content="archived",
        )
        archive_workitem(db, wi.id)
        result = call_tool("list_work_items", {"project": "testproj"})
        titles = [w["title"] for w in result]
        assert "Archived item" not in titles


class TestGetWorkItem:
    """Tests for the get_work_item MCP tool."""

    def test_returns_work_item(self, call_tool, db, sample_project, sample_area):
        from kwi.queries import insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="Detail item",
            content="Full content here",
        )
        result = call_tool("get_work_item", {"id": wi.id})
        assert result["id"] == wi.id
        assert result["title"] == "Detail item"
        assert result["content"] == "Full content here"

    def test_nonexistent_item_returns_error(self, call_tool, db):
        result = call_tool("get_work_item", {"id": 999999})
        assert "error" in result


class TestCreateWorkItem:
    """Tests for the create_work_item MCP tool."""

    def test_create_with_all_fields(self, call_tool, db, sample_project, sample_area):
        result = call_tool(
            "create_work_item",
            {
                "project": "testproj",
                "title": "New item",
                "content": "Body text",
                "area": "testarea",
                "type": "task",
                "status": "open",
                "tshirt": "M",
                "sprint": "sprint-1",
                "details": "Extra details",
            },
        )
        assert result["title"] == "New item"
        assert result["content"] == "Body text"
        assert result["wi_type"] == "task"
        assert result["wi_status"] == "open"
        assert result["area_name"] == "testarea"
        assert result["sprint"] == "sprint-1"
        assert "id" in result

    def test_create_with_defaults(self, call_tool, db, sample_project):
        result = call_tool(
            "create_work_item",
            {
                "project": "testproj",
                "title": "Minimal item",
                "content": "Just content",
            },
        )
        assert result["title"] == "Minimal item"
        assert "id" in result

    def test_create_invalid_project(self, call_tool, db):
        result = call_tool(
            "create_work_item",
            {
                "project": "nonexistent",
                "title": "Bad",
                "content": "body",
            },
        )
        assert "error" in result

    def test_create_invalid_type(self, call_tool, db, sample_project):
        result = call_tool(
            "create_work_item",
            {
                "project": "testproj",
                "title": "Bad type",
                "content": "body",
                "type": "invalid_type",
            },
        )
        assert "error" in result


class TestUpdateWorkItem:
    """Tests for the update_work_item MCP tool."""

    def _make_item(self, db):
        from kwi.queries import insert_workitem

        return insert_workitem(
            db,
            project_name="testproj",
            title="Original title",
            content="Original content",
        )

    def test_update_single_field(self, call_tool, db, sample_project):
        wi = self._make_item(db)
        result = call_tool("update_work_item", {"id": wi.id, "title": "Updated title"})
        assert result["id"] == wi.id
        assert "title" in result["updated_fields"]
        # Verify via get
        fetched = call_tool("get_work_item", {"id": wi.id})
        assert fetched["title"] == "Updated title"

    def test_update_multiple_fields(self, call_tool, db, sample_project):
        wi = self._make_item(db)
        call_tool(
            "update_work_item",
            {"id": wi.id, "title": "New title", "status": "closed"},
        )
        fetched = call_tool("get_work_item", {"id": wi.id})
        assert fetched["title"] == "New title"
        assert fetched["wi_status"] == "closed"

    def test_update_nonexistent(self, call_tool, db):
        result = call_tool("update_work_item", {"id": 999999, "title": "X"})
        assert "error" in result

    def test_update_invalid_status(self, call_tool, db, sample_project):
        wi = self._make_item(db)
        result = call_tool("update_work_item", {"id": wi.id, "status": "bad_status"})
        assert "error" in result

    def test_update_persists_tshirt_area_parent(
        self, call_tool, db, sample_project, sample_area
    ):
        """WI 41: tshirt, area, and parent were previously dropped."""
        parent = self._make_item(db)
        wi = self._make_item(db)
        result = call_tool(
            "update_work_item",
            {
                "id": wi.id,
                "tshirt": "L",
                "area": "testarea",
                "parent": parent.id,
            },
        )
        assert "error" not in result
        fetched = call_tool("get_work_item", {"id": wi.id})
        assert fetched["wi_tshirt"] == "L"
        assert fetched["area_name"] == "testarea"
        assert fetched["parent_id"] == parent.id


class TestArchiveWorkItem:
    """Tests for the archive_work_item MCP tool."""

    def test_archive_succeeds(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="To archive",
            content="body",
            wi_status="active",
        )
        result = call_tool("archive_work_item", {"id": wi.id})
        assert "error" not in result
        assert result["archived"] is True
        assert result["wi_status"] == "active"

    def test_archived_excluded_from_default_list(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="Will be archived",
            content="body",
        )
        call_tool("archive_work_item", {"id": wi.id})
        items = call_tool("list_work_items", {"project": "testproj"})
        titles = [w["title"] for w in items]
        assert "Will be archived" not in titles

    def test_archive_nonexistent(self, call_tool, db):
        result = call_tool("archive_work_item", {"id": 999999})
        assert "error" in result


class TestUnarchiveWorkItem:
    """Tests for the unarchive_work_item MCP tool."""

    def test_unarchive_clears_flag(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="Restore me",
            content="body",
            wi_status="active",
        )
        call_tool("archive_work_item", {"id": wi.id})
        result = call_tool("unarchive_work_item", {"id": wi.id})
        assert "error" not in result
        assert result["archived"] is False
        assert result["wi_status"] == "active"

    def test_unarchive_nonexistent(self, call_tool, db):
        result = call_tool("unarchive_work_item", {"id": 999999})
        assert "error" in result


class TestRelateWorkItems:
    """Tests for relate_work_items, list_related, unrelate_work_items tools."""

    def _make_two_items(self, db):
        from kwi.queries import insert_workitem

        wi1 = insert_workitem(
            db,
            project_name="testproj",
            title="Item A",
            content="a",
        )
        wi2 = insert_workitem(
            db,
            project_name="testproj",
            title="Item B",
            content="b",
        )
        return wi1, wi2

    def test_relate_and_list(self, call_tool, db, sample_project):
        wi1, wi2 = self._make_two_items(db)
        result = call_tool(
            "relate_work_items",
            {"left_id": wi1.id, "right_id": wi2.id, "relationship": "blocks"},
        )
        assert "error" not in result

        related = call_tool("list_related", {"id": wi1.id})
        assert isinstance(related, list)
        assert len(related) >= 1
        related_ids = [r["id"] for r in related]
        assert wi2.id in related_ids

    def test_unrelate(self, call_tool, db, sample_project):
        wi1, wi2 = self._make_two_items(db)
        call_tool(
            "relate_work_items",
            {"left_id": wi1.id, "right_id": wi2.id, "relationship": "blocks"},
        )
        result = call_tool(
            "unrelate_work_items", {"left_id": wi1.id, "right_id": wi2.id}
        )
        assert "error" not in result

        related = call_tool("list_related", {"id": wi1.id})
        assert len(related) == 0

    def test_list_related_empty(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        wi = insert_workitem(
            db,
            project_name="testproj",
            title="Lonely",
            content="none",
        )
        related = call_tool("list_related", {"id": wi.id})
        assert related == []


class TestSearchWorkItems:
    """Tests for the search_work_items MCP tool."""

    def test_title_match(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        insert_workitem(
            db,
            project_name="testproj",
            title="Unique banana title",
            content="nothing special",
        )
        result = call_tool(
            "search_work_items", {"project": "testproj", "query": "banana"}
        )
        assert isinstance(result, list)
        assert len(result) >= 1
        titles = [w["title"] for w in result]
        assert "Unique banana title" in titles

    def test_content_match(self, call_tool, db, sample_project):
        from kwi.queries import insert_workitem

        insert_workitem(
            db,
            project_name="testproj",
            title="Plain title",
            content="Contains zebra keyword",
        )
        result = call_tool(
            "search_work_items", {"project": "testproj", "query": "zebra"}
        )
        assert len(result) >= 1
        titles = [w["title"] for w in result]
        assert "Plain title" in titles

    def test_no_results(self, call_tool, db, sample_project):
        result = call_tool(
            "search_work_items",
            {"project": "testproj", "query": "xyznonexistent123"},
        )
        assert result == []

    def test_invalid_project(self, call_tool, db):
        result = call_tool(
            "search_work_items",
            {"project": "nonexistent", "query": "test"},
        )
        assert "error" in result


class TestDBConnectionFailure:
    """Test that DB connection failures produce ToolError."""

    def test_connection_failure_raises_tool_error(self, mcp_instance):
        import asyncio
        from contextlib import contextmanager
        from unittest.mock import patch

        from mcp.server.fastmcp.exceptions import ToolError

        @contextmanager
        def _bad_connection(_url):
            raise ConnectionError("DB unreachable")

        with (
            patch("kwi.mcp.server.get_connection", _bad_connection),
            pytest.raises(ToolError, match="DB unreachable"),
        ):
            asyncio.run(mcp_instance.call_tool("list_projects", {}))
