"""Tests for output rendering helpers."""

import json
from datetime import UTC, datetime

from kwi.output import render_error, render_json, render_message, render_table


class TestRenderTable:
    def test_table_output_contains_headers(self, capsys):
        render_table(["ID", "Name"], [[1, "test"]])
        out = capsys.readouterr().out
        assert "ID" in out
        assert "Name" in out

    def test_table_output_contains_data(self, capsys):
        render_table(["ID", "Name"], [[1, "alpha"], [2, "beta"]])
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out

    def test_table_handles_none_values(self, capsys):
        render_table(["ID", "Name"], [[1, None]])
        out = capsys.readouterr().out
        assert "1" in out

    def test_empty_rows_shows_headers(self, capsys):
        render_table(["ID", "Name"], [])
        out = capsys.readouterr().out
        assert "ID" in out
        assert "Name" in out


class TestRenderJson:
    def test_json_list_output(self, capsys):
        render_json([{"id": 1, "name": "test"}])
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == [{"id": 1, "name": "test"}]

    def test_json_dict_output(self, capsys):
        render_json({"id": 1, "name": "test"})
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == {"id": 1, "name": "test"}

    def test_json_handles_datetime(self, capsys):
        dt = datetime(2026, 3, 21, 12, 0, 0, tzinfo=UTC)
        render_json({"created": dt})
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "2026" in parsed["created"]

    def test_json_handles_none(self, capsys):
        render_json({"value": None})
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed["value"] is None


class TestRenderMessage:
    def test_plain_message(self, capsys):
        render_message("Created project kwi (ID: 1)")
        out = capsys.readouterr().out
        assert "Created project kwi (ID: 1)" in out


class TestRenderError:
    def test_error_to_stderr(self, capsys):
        render_error("Something went wrong")
        err = capsys.readouterr().err
        assert "Something went wrong" in err

    def test_error_json_to_stderr(self, capsys):
        render_error("Something went wrong", use_json=True)
        err = capsys.readouterr().err
        parsed = json.loads(err)
        assert parsed == {"error": "Something went wrong"}

    def test_error_json_is_valid_json(self, capsys):
        render_error("Special chars: <>&\"'", use_json=True)
        err = capsys.readouterr().err
        parsed = json.loads(err)
        assert parsed["error"] == "Special chars: <>&\"'"
