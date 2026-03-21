"""Tests for area query functions (US2)."""

import psycopg
import pytest

from kwi.queries import insert_area, insert_project, list_areas


class TestInsertArea:
    def test_create_area(self, db):
        p = insert_project(db, name="areaproj", cn_path="/tmp/ap")
        a = insert_area(db, project_id=p.id, name="backend")
        assert a.id > 0
        assert a.project_id == p.id
        assert a.name == "backend"
        assert a.description is None

    def test_create_area_with_description(self, db):
        p = insert_project(db, name="areaproj2", cn_path="/tmp/ap2")
        a = insert_area(
            db,
            project_id=p.id,
            name="frontend",
            description="UI components",
        )
        assert a.description == "UI components"

    def test_duplicate_area_in_same_project(self, db):
        p = insert_project(db, name="duparea", cn_path="/tmp/da")
        insert_area(db, project_id=p.id, name="dup")
        with pytest.raises(psycopg.errors.UniqueViolation):
            insert_area(db, project_id=p.id, name="dup")

    def test_same_area_name_in_different_projects(self, db):
        p1 = insert_project(db, name="proj_a", cn_path="/tmp/pa")
        p2 = insert_project(db, name="proj_b", cn_path="/tmp/pb")
        a1 = insert_area(db, project_id=p1.id, name="shared")
        a2 = insert_area(db, project_id=p2.id, name="shared")
        assert a1.id != a2.id


class TestListAreas:
    def test_list_areas_for_project(self, db):
        p = insert_project(db, name="listareas", cn_path="/tmp/la")
        insert_area(db, project_id=p.id, name="area1")
        insert_area(db, project_id=p.id, name="area2")
        areas = list_areas(db, p.id)
        names = [a.name for a in areas]
        assert "area1" in names
        assert "area2" in names
        assert len(areas) == 2

    def test_list_areas_empty(self, db):
        p = insert_project(db, name="noareas", cn_path="/tmp/na")
        areas = list_areas(db, p.id)
        assert areas == []

    def test_list_areas_scoped_to_project(self, db):
        p1 = insert_project(db, name="scope1", cn_path="/tmp/s1")
        p2 = insert_project(db, name="scope2", cn_path="/tmp/s2")
        insert_area(db, project_id=p1.id, name="only_in_p1")
        insert_area(db, project_id=p2.id, name="only_in_p2")
        areas1 = list_areas(db, p1.id)
        names1 = [a.name for a in areas1]
        assert "only_in_p1" in names1
        assert "only_in_p2" not in names1
