"""Tests for relationship management queries (US6)."""

import pytest

from kwi.queries import (
    QueryError,
    delete_related,
    insert_project,
    insert_related,
    insert_workitem,
    list_related,
)


@pytest.fixture
def two_items(db):
    """Create a project with two work items and return their IDs."""
    insert_project(db, name="relproj", cn_path="/tmp/rp")
    w1 = insert_workitem(db, project_name="relproj", title="Item 1", content="c")
    w2 = insert_workitem(db, project_name="relproj", title="Item 2", content="c")
    return w1.id, w2.id


class TestInsertRelated:
    def test_create_relationship(self, db, two_items):
        id1, id2 = two_items
        r = insert_related(db, left_id=id1, right_id=id2, relationship="blocks")
        assert r.left_id == id1
        assert r.right_id == id2
        assert r.relationship == "blocks"

    def test_self_reference_raises(self, db, two_items):
        id1, _ = two_items
        with pytest.raises(QueryError, match="itself"):
            insert_related(
                db,
                left_id=id1,
                right_id=id1,
                relationship="blocks",
            )

    def test_nonexistent_item_raises(self, db, two_items):
        id1, _ = two_items
        with pytest.raises(QueryError, match="not found"):
            insert_related(
                db,
                left_id=id1,
                right_id=999999,
                relationship="blocks",
            )


class TestListRelated:
    def test_list_bidirectional(self, db, two_items):
        id1, id2 = two_items
        insert_related(db, left_id=id1, right_id=id2, relationship="blocks")
        # Query from left side
        rels1 = list_related(db, id1)
        assert len(rels1) == 1
        assert rels1[0]["id"] == id2
        assert rels1[0]["direction"] == "right"
        # Query from right side
        rels2 = list_related(db, id2)
        assert len(rels2) == 1
        assert rels2[0]["id"] == id1
        assert rels2[0]["direction"] == "left"

    def test_list_empty(self, db, two_items):
        id1, _ = two_items
        assert list_related(db, id1) == []


class TestDeleteRelated:
    def test_delete_existing(self, db, two_items):
        id1, id2 = two_items
        insert_related(db, left_id=id1, right_id=id2, relationship="blocks")
        assert delete_related(db, id1, id2) is True
        assert list_related(db, id1) == []

    def test_delete_nonexistent(self, db, two_items):
        id1, id2 = two_items
        assert delete_related(db, id1, id2) is False

    def test_delete_reverse_direction(self, db, two_items):
        id1, id2 = two_items
        insert_related(db, left_id=id1, right_id=id2, relationship="blocks")
        # Delete using reversed IDs should still work
        assert delete_related(db, id2, id1) is True
        assert list_related(db, id1) == []
