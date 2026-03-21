"""Tests for project query functions (US2)."""

import psycopg
import pytest

from kwi.queries import get_project, insert_project, list_projects


class TestInsertProject:
    def test_create_project(self, db):
        p = insert_project(db, name="myproj", cn_path="/home/test/myproj")
        assert p.id > 0
        assert p.project == "myproj"
        assert p.cn_path == "/home/test/myproj"
        assert p.gh_repo is None
        assert p.created is not None

    def test_create_project_with_all_fields(self, db):
        p = insert_project(
            db,
            name="fullproj",
            cn_path="/home/test/fullproj",
            gh_repo="https://github.com/user/fullproj",
            description="A project with all fields",
        )
        assert p.gh_repo == "https://github.com/user/fullproj"
        assert p.description == "A project with all fields"

    def test_duplicate_name_raises(self, db):
        insert_project(db, name="duptest", cn_path="/tmp/dup1")
        with pytest.raises(psycopg.errors.UniqueViolation):
            insert_project(db, name="duptest", cn_path="/tmp/dup2")


class TestListProjects:
    def test_list_empty(self, db):
        # In a rolled-back transaction, no projects exist
        projects = list_projects(db)
        assert isinstance(projects, list)

    def test_list_returns_created_projects(self, db):
        insert_project(db, name="proj1", cn_path="/tmp/p1")
        insert_project(db, name="proj2", cn_path="/tmp/p2")
        projects = list_projects(db)
        names = [p.project for p in projects]
        assert "proj1" in names
        assert "proj2" in names

    def test_list_ordered_by_id(self, db):
        p1 = insert_project(db, name="first", cn_path="/tmp/f")
        p2 = insert_project(db, name="second", cn_path="/tmp/s")
        projects = list_projects(db)
        ids = [p.id for p in projects]
        assert ids.index(p1.id) < ids.index(p2.id)


class TestGetProject:
    def test_get_by_name(self, db):
        created = insert_project(db, name="findme", cn_path="/tmp/find")
        found = get_project(db, "findme")
        assert found is not None
        assert found.id == created.id

    def test_get_by_id(self, db):
        created = insert_project(db, name="findid", cn_path="/tmp/findid")
        found = get_project(db, str(created.id))
        assert found is not None
        assert found.project == "findid"

    def test_get_not_found(self, db):
        result = get_project(db, "nonexistent")
        assert result is None

    def test_get_not_found_by_id(self, db):
        result = get_project(db, "999999")
        assert result is None
