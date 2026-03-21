"""Tests for work item query functions and frontmatter parsing (US3-US5)."""

import pytest

from kwi.queries import (
    QueryError,
    archive_workitem,
    get_workitem,
    insert_area,
    insert_project,
    insert_workitem,
    list_workitems,
    update_workitem,
)


class TestInsertWorkitem:
    def test_create_basic_workitem(self, db):
        insert_project(db, name="witest", cn_path="/tmp/wi")
        w = insert_workitem(
            db,
            project_name="witest",
            title="Test item",
            content="Some content",
        )
        assert w.id > 0
        assert w.title == "Test item"
        assert w.wi_type == "idea"
        assert w.wi_status == "open"
        assert w.wi_tshirt == "Unknown"

    def test_create_workitem_with_all_fields(self, db):
        p = insert_project(db, name="wifull", cn_path="/tmp/wf")
        insert_area(db, project_id=p.id, name="backend")
        w = insert_workitem(
            db,
            project_name="wifull",
            title="Full item",
            content="# Content",
            wi_type="bug",
            wi_status="active",
            wi_tshirt="M",
            area_name="backend",
            sprint="001-test",
            details="Details here",
        )
        assert w.wi_type == "bug"
        assert w.wi_status == "active"
        assert w.wi_tshirt == "M"
        assert w.area_name == "backend"
        assert w.sprint == "001-test"

    def test_invalid_project_raises(self, db):
        with pytest.raises(QueryError, match="not found"):
            insert_workitem(
                db,
                project_name="nonexistent",
                title="test",
                content="c",
            )

    def test_invalid_type_raises(self, db):
        insert_project(db, name="typeerr", cn_path="/tmp/te")
        with pytest.raises(QueryError, match="Invalid type"):
            insert_workitem(
                db,
                project_name="typeerr",
                title="test",
                content="c",
                wi_type="invalid_type",
            )

    def test_invalid_status_raises(self, db):
        insert_project(db, name="staterr", cn_path="/tmp/se")
        with pytest.raises(QueryError, match="Invalid status"):
            insert_workitem(
                db,
                project_name="staterr",
                title="test",
                content="c",
                wi_status="nonexistent",
            )

    def test_invalid_area_raises(self, db):
        insert_project(db, name="areaerr", cn_path="/tmp/ae")
        with pytest.raises(QueryError, match="Area.*not found"):
            insert_workitem(
                db,
                project_name="areaerr",
                title="test",
                content="c",
                area_name="nonexistent",
            )


class TestListWorkitems:
    def test_list_empty_project(self, db):
        p = insert_project(db, name="emptylist", cn_path="/tmp/el")
        items = list_workitems(db, project_id=p.id)
        assert items == []

    def test_list_excludes_archived(self, db):
        p = insert_project(db, name="archlist", cn_path="/tmp/al")
        insert_workitem(
            db,
            project_name="archlist",
            title="Active",
            content="c",
        )
        insert_workitem(
            db,
            project_name="archlist",
            title="Archived",
            content="c",
            wi_status="archived",
        )
        items = list_workitems(db, project_id=p.id)
        titles = [w.title for w in items]
        assert "Active" in titles
        assert "Archived" not in titles

    def test_list_with_status_filter(self, db):
        p = insert_project(db, name="statfilt", cn_path="/tmp/sf")
        insert_workitem(
            db,
            project_name="statfilt",
            title="Open",
            content="c",
            wi_status="open",
        )
        insert_workitem(
            db,
            project_name="statfilt",
            title="Active",
            content="c",
            wi_status="active",
        )
        items = list_workitems(
            db,
            project_id=p.id,
            status_filter=["active"],
        )
        assert len(items) == 1
        assert items[0].title == "Active"

    def test_list_with_archived_status(self, db):
        p = insert_project(db, name="archfilt", cn_path="/tmp/af")
        insert_workitem(
            db,
            project_name="archfilt",
            title="Archived",
            content="c",
            wi_status="archived",
        )
        items = list_workitems(
            db,
            project_id=p.id,
            status_filter=["archived"],
        )
        assert len(items) == 1


class TestGetWorkitem:
    def test_get_existing(self, db):
        insert_project(db, name="gettest", cn_path="/tmp/gt")
        w = insert_workitem(
            db,
            project_name="gettest",
            title="Get me",
            content="content",
        )
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.title == "Get me"
        assert found.project_name == "gettest"

    def test_get_not_found(self, db):
        assert get_workitem(db, 999999) is None


class TestUpdateWorkitem:
    def test_update_status(self, db):
        insert_project(db, name="updtest", cn_path="/tmp/ut")
        w = insert_workitem(
            db,
            project_name="updtest",
            title="Update me",
            content="c",
        )
        updated = update_workitem(db, w.id, wi_status="active")
        assert "status" in updated
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.wi_status == "active"

    def test_update_not_found(self, db):
        with pytest.raises(QueryError, match="not found"):
            update_workitem(db, 999999, title="x")

    def test_update_invalid_type(self, db):
        insert_project(db, name="invtype", cn_path="/tmp/it")
        w = insert_workitem(
            db,
            project_name="invtype",
            title="test",
            content="c",
        )
        with pytest.raises(QueryError, match="Invalid type"):
            update_workitem(db, w.id, wi_type="bogus")


class TestArchiveWorkitem:
    def test_archive(self, db):
        insert_project(db, name="archtest", cn_path="/tmp/at")
        w = insert_workitem(
            db,
            project_name="archtest",
            title="Archive me",
            content="c",
        )
        archive_workitem(db, w.id)
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.wi_status == "archived"

    def test_archive_not_found(self, db):
        with pytest.raises(QueryError, match="not found"):
            archive_workitem(db, 999999)
