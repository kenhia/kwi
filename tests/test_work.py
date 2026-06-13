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
    unarchive_workitem,
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
        archived = insert_workitem(
            db,
            project_name="archlist",
            title="Archived",
            content="c",
        )
        archive_workitem(db, archived.id)
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

    def test_list_with_archived_included(self, db):
        p = insert_project(db, name="archfilt", cn_path="/tmp/af")
        archived = insert_workitem(
            db,
            project_name="archfilt",
            title="Archived",
            content="c",
        )
        archive_workitem(db, archived.id)
        items = list_workitems(
            db,
            project_id=p.id,
            include_archived=True,
        )
        assert len(items) == 1
        assert items[0].archived is True

    def test_list_archived_only(self, db):
        p = insert_project(db, name="archonly", cn_path="/tmp/ao")
        insert_workitem(
            db,
            project_name="archonly",
            title="Active",
            content="c",
        )
        archived = insert_workitem(
            db,
            project_name="archonly",
            title="Archived",
            content="c",
        )
        archive_workitem(db, archived.id)
        items = list_workitems(
            db,
            project_id=p.id,
            archived_only=True,
        )
        titles = [w.title for w in items]
        assert titles == ["Archived"]
        assert items[0].archived is True


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
    def test_archive_sets_flag_preserves_status(self, db):
        insert_project(db, name="archtest", cn_path="/tmp/at")
        w = insert_workitem(
            db,
            project_name="archtest",
            title="Archive me",
            content="c",
            wi_status="active",
        )
        archive_workitem(db, w.id)
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.archived is True
        assert found.wi_status == "active"

    def test_archive_twice_is_noop(self, db):
        insert_project(db, name="archtwice", cn_path="/tmp/atw")
        w = insert_workitem(
            db,
            project_name="archtwice",
            title="Archive me twice",
            content="c",
        )
        archive_workitem(db, w.id)
        archive_workitem(db, w.id)
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.archived is True

    def test_archive_not_found(self, db):
        with pytest.raises(QueryError, match="not found"):
            archive_workitem(db, 999999)


class TestUnarchiveWorkitem:
    def test_unarchive_clears_flag_preserves_status(self, db):
        insert_project(db, name="unarch", cn_path="/tmp/un")
        w = insert_workitem(
            db,
            project_name="unarch",
            title="Restore me",
            content="c",
            wi_status="active",
        )
        archive_workitem(db, w.id)
        unarchive_workitem(db, w.id)
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.archived is False
        assert found.wi_status == "active"

    def test_unarchive_non_archived_is_noop(self, db):
        insert_project(db, name="unarchnoop", cn_path="/tmp/unn")
        w = insert_workitem(
            db,
            project_name="unarchnoop",
            title="Already active",
            content="c",
        )
        unarchive_workitem(db, w.id)
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.archived is False

    def test_unarchive_not_found(self, db):
        with pytest.raises(QueryError, match="not found"):
            unarchive_workitem(db, 999999)


class TestUpdateWorkitemFields:
    """US7: tshirt, area, and parent updates with validation (WI 41)."""

    def test_update_tshirt(self, db):
        insert_project(db, name="tsupd", cn_path="/tmp/tsu")
        w = insert_workitem(db, project_name="tsupd", title="t", content="c")
        updated = update_workitem(db, w.id, wi_tshirt="L")
        assert "tshirt" in updated
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.wi_tshirt == "L"

    def test_update_invalid_tshirt_raises(self, db):
        insert_project(db, name="tsbad", cn_path="/tmp/tsb")
        w = insert_workitem(db, project_name="tsbad", title="t", content="c")
        with pytest.raises(QueryError, match="Invalid t-shirt"):
            update_workitem(db, w.id, wi_tshirt="Gigantic")

    def test_update_area(self, db):
        p = insert_project(db, name="arupd", cn_path="/tmp/aru")
        insert_area(db, project_id=p.id, name="backend")
        w = insert_workitem(db, project_name="arupd", title="t", content="c")
        updated = update_workitem(db, w.id, area="backend")
        assert "area" in updated
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.area_name == "backend"

    def test_update_unknown_area_raises(self, db):
        insert_project(db, name="arbad", cn_path="/tmp/arb")
        w = insert_workitem(db, project_name="arbad", title="t", content="c")
        with pytest.raises(QueryError, match="Area.*not found"):
            update_workitem(db, w.id, area="nope")

    def test_update_parent(self, db):
        insert_project(db, name="paupd", cn_path="/tmp/pau")
        parent = insert_workitem(db, project_name="paupd", title="p", content="c")
        child = insert_workitem(db, project_name="paupd", title="ch", content="c")
        updated = update_workitem(db, child.id, parent_id=parent.id)
        assert "parent" in updated
        found = get_workitem(db, child.id)
        assert found is not None
        assert found.parent_id == parent.id

    def test_update_omitted_fields_unchanged(self, db):
        insert_project(db, name="omit", cn_path="/tmp/om")
        w = insert_workitem(
            db,
            project_name="omit",
            title="keep",
            content="c",
            wi_tshirt="M",
        )
        update_workitem(db, w.id, title="changed")
        found = get_workitem(db, w.id)
        assert found is not None
        assert found.title == "changed"
        assert found.wi_tshirt == "M"

    def test_self_parent_rejected(self, db):
        insert_project(db, name="selfpar", cn_path="/tmp/sp")
        w = insert_workitem(db, project_name="selfpar", title="t", content="c")
        with pytest.raises(QueryError, match="own parent"):
            update_workitem(db, w.id, parent_id=w.id)

    def test_cycle_parent_rejected(self, db):
        insert_project(db, name="cycle", cn_path="/tmp/cy")
        a = insert_workitem(db, project_name="cycle", title="a", content="c")
        b = insert_workitem(db, project_name="cycle", title="b", content="c")
        update_workitem(db, b.id, parent_id=a.id)
        with pytest.raises(QueryError, match="cycle"):
            update_workitem(db, a.id, parent_id=b.id)

    def test_unknown_parent_rejected(self, db):
        insert_project(db, name="nopar", cn_path="/tmp/np")
        w = insert_workitem(db, project_name="nopar", title="t", content="c")
        with pytest.raises(QueryError, match="Parent.*not found"):
            update_workitem(db, w.id, parent_id=999999)
