"""Tests for database migration (US1)."""

import psycopg
import pytest

EXPECTED_TABLES = [
    "workitem_type",
    "workitem_status",
    "project",
    "area",
    "workitem",
    "related",
]

EXPECTED_TYPES = [
    "bug",
    "task",
    "idea",
    "research",
    "tweak",
    "issue",
    "feature",
    "epic",
    "story",
]

EXPECTED_STATUSES = [
    "open",
    "active",
    "resolved",
    "closed",
    "draft",
]


class TestMigration:
    """Verify the initial migration creates all tables and seed data."""

    def test_all_tables_exist(self, db):
        cur = db.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' "
            "ORDER BY table_name"
        )
        tables = [row[0] for row in cur.fetchall()]
        for table in EXPECTED_TABLES:
            assert table in tables, f"Table '{table}' not found"

    def test_workitem_type_columns(self, db):
        cur = db.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'workitem_type' "
            "ORDER BY ordinal_position"
        )
        cols = [row[0] for row in cur.fetchall()]
        assert "id" in cols
        assert "name" in cols

    def test_workitem_columns(self, db):
        cur = db.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'workitem' "
            "ORDER BY ordinal_position"
        )
        cols = [row[0] for row in cur.fetchall()]
        expected = [
            "id",
            "project_id",
            "area_id",
            "wi_type_id",
            "wi_status_id",
            "wi_tshirt",
            "archived",
            "sprint",
            "title",
            "content",
            "details",
            "parent_id",
            "created",
            "updated",
        ]
        for col in expected:
            assert col in cols, f"Column '{col}' not in workitem"

    def test_seed_types(self, db):
        cur = db.execute("SELECT name FROM workitem_type ORDER BY name")
        types = sorted(row[0] for row in cur.fetchall())
        assert types == sorted(EXPECTED_TYPES)

    def test_seed_statuses(self, db):
        cur = db.execute("SELECT name FROM workitem_status ORDER BY name")
        statuses = sorted(row[0] for row in cur.fetchall())
        assert statuses == sorted(EXPECTED_STATUSES)

    def test_seed_type_count(self, db):
        cur = db.execute("SELECT COUNT(*) FROM workitem_type")
        assert cur.fetchone()[0] == 9

    def test_seed_status_count(self, db):
        cur = db.execute("SELECT COUNT(*) FROM workitem_status")
        assert cur.fetchone()[0] == 5

    def test_migration_is_idempotent(self, db):
        """Re-applying the initial migration should not error or duplicate data.

        Note: 001 alone re-seeds the legacy 'archived' status (ON CONFLICT DO
        NOTHING), so the status count returns to 6 inside this transaction. In
        normal operation migration 002 runs afterward and removes it again.
        """
        from pathlib import Path

        migration = (
            Path(__file__).resolve().parent.parent
            / "migrations"
            / "001_initial_schema.sql"
        )
        # Should not raise
        db.execute(migration.read_text())

        cur = db.execute("SELECT COUNT(*) FROM workitem_type")
        assert cur.fetchone()[0] == 9

        cur = db.execute("SELECT COUNT(*) FROM workitem_status")
        assert cur.fetchone()[0] == 6

    def test_project_table_columns(self, db):
        cur = db.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'project' "
            "ORDER BY ordinal_position"
        )
        cols = [row[0] for row in cur.fetchall()]
        expected = [
            "id",
            "project",
            "gh_repo",
            "cn_path",
            "created",
            "updated",
            "description",
        ]
        for col in expected:
            assert col in cols, f"Column '{col}' not in project"

    def test_area_unique_constraint(self, db):
        """Duplicate area name in same project should fail."""
        cur = db.execute(
            "INSERT INTO project (project, cn_path) "
            "VALUES ('constrainttest', '/tmp/ct') "
            "RETURNING id"
        )
        pid = cur.fetchone()[0]

        db.execute(
            "INSERT INTO area (project_id, name) VALUES (%s, 'dup')",
            (pid,),
        )

        with pytest.raises(psycopg.errors.UniqueViolation):
            db.execute(
                "INSERT INTO area (project_id, name) VALUES (%s, 'dup')",
                (pid,),
            )

    def test_workitem_tshirt_check_constraint(self, db):
        """Invalid t-shirt size should fail the CHECK constraint."""
        cur = db.execute(
            "INSERT INTO project (project, cn_path) "
            "VALUES ('tshirttest', '/tmp/tt') "
            "RETURNING id"
        )
        pid = cur.fetchone()[0]
        cur = db.execute("SELECT id FROM workitem_type LIMIT 1")
        type_id = cur.fetchone()[0]
        cur = db.execute("SELECT id FROM workitem_status LIMIT 1")
        status_id = cur.fetchone()[0]

        with pytest.raises(psycopg.errors.CheckViolation):
            db.execute(
                "INSERT INTO workitem "
                "(project_id, wi_type_id, wi_status_id, "
                "wi_tshirt, title, content) "
                "VALUES (%s, %s, %s, 'INVALID', 'test', 'content')",
                (pid, type_id, status_id),
            )


class TestArchivedFlagMigration:
    """Verify migration 002 decouples archived from status (US1)."""

    def test_archived_column_exists_with_default(self, db):
        cur = db.execute(
            "SELECT column_default, is_nullable, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = 'workitem' AND column_name = 'archived'"
        )
        row = cur.fetchone()
        assert row is not None, "workitem.archived column missing"
        column_default, is_nullable, data_type = row
        assert data_type == "boolean"
        assert is_nullable == "NO"
        assert "false" in (column_default or "").lower()

    def test_archived_status_removed(self, db):
        cur = db.execute("SELECT name FROM workitem_status ORDER BY name")
        statuses = [row[0] for row in cur.fetchall()]
        assert "archived" not in statuses
        assert len(statuses) == 5

    def test_archived_index_exists(self, db):
        cur = db.execute(
            "SELECT indexname FROM pg_indexes "
            "WHERE tablename = 'workitem' AND indexname = 'idx_workitem_archived'"
        )
        assert cur.fetchone() is not None

    def test_legacy_archived_rows_repointed(self, db):
        """A row seeded with the legacy 'archived' status migrates to closed+flag."""
        from pathlib import Path

        cur = db.execute(
            "INSERT INTO project (project, cn_path) "
            "VALUES ('legacyarch', '/tmp/la') RETURNING id"
        )
        pid = cur.fetchone()[0]
        cur = db.execute("SELECT id FROM workitem_type LIMIT 1")
        type_id = cur.fetchone()[0]
        # Re-create the legacy 'archived' status to simulate a pre-002 row.
        cur = db.execute(
            "INSERT INTO workitem_status (name) VALUES ('archived') RETURNING id"
        )
        arch_status_id = cur.fetchone()[0]
        cur = db.execute(
            "INSERT INTO workitem "
            "(project_id, wi_type_id, wi_status_id, title, content) "
            "VALUES (%s, %s, %s, 'legacy', 'c') RETURNING id",
            (pid, type_id, arch_status_id),
        )
        wid = cur.fetchone()[0]

        migration = (
            Path(__file__).resolve().parent.parent
            / "migrations"
            / "002_archived_flag.sql"
        )
        db.execute(migration.read_text())

        cur = db.execute(
            "SELECT s.name, w.archived FROM workitem w "
            "JOIN workitem_status s ON w.wi_status_id = s.id "
            "WHERE w.id = %s",
            (wid,),
        )
        status_name, archived = cur.fetchone()
        assert status_name == "closed"
        assert archived is True

    def test_migration_002_is_idempotent(self, db):
        """Re-applying 002 should not error or change the status count."""
        from pathlib import Path

        migration = (
            Path(__file__).resolve().parent.parent
            / "migrations"
            / "002_archived_flag.sql"
        )
        db.execute(migration.read_text())

        cur = db.execute("SELECT COUNT(*) FROM workitem_status")
        assert cur.fetchone()[0] == 5
