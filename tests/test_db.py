"""Tests for database connection config resolution."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from kwi.db import KwiConfigError, resolve_db_url


def _env_without_kwi(**extra: str) -> dict[str, str]:
    """Return a copy of os.environ without KWI_DATABASE_URL, plus extras."""
    env = os.environ.copy()
    env.pop("KWI_DATABASE_URL", None)
    env.update(extra)
    return env


class TestResolveDbUrl:
    """Test config resolution: flag > env > config file > error."""

    def test_flag_takes_precedence_over_env_and_config(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('database_url = "postgresql://config@host/db"\n')

        with patch.dict(os.environ, {"KWI_DATABASE_URL": "postgresql://env@host/db"}):
            result = resolve_db_url(
                flag_value="postgresql://flag@host/db",
                config_path=config_file,
            )
        assert result == "postgresql://flag@host/db"

    def test_env_takes_precedence_over_config(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('database_url = "postgresql://config@host/db"\n')

        with patch.dict(os.environ, {"KWI_DATABASE_URL": "postgresql://env@host/db"}):
            result = resolve_db_url(flag_value=None, config_path=config_file)
        assert result == "postgresql://env@host/db"

    def test_config_file_used_when_no_flag_or_env(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('database_url = "postgresql://config@host/db"\n')

        with patch.dict(os.environ, _env_without_kwi(), clear=True):
            result = resolve_db_url(flag_value=None, config_path=config_file)
        assert result == "postgresql://config@host/db"

    def test_error_when_no_config_found(self, tmp_path: Path):
        missing_config = tmp_path / "nonexistent" / "config.toml"

        with (
            patch.dict(os.environ, _env_without_kwi(), clear=True),
            pytest.raises(KwiConfigError) as exc_info,
        ):
            resolve_db_url(flag_value=None, config_path=missing_config)

        error_msg = str(exc_info.value)
        assert "--db-url" in error_msg
        assert "KWI_DATABASE_URL" in error_msg
        assert "config.toml" in error_msg

    def test_config_file_missing_key_raises_error(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('other_key = "value"\n')

        with (
            patch.dict(os.environ, _env_without_kwi(), clear=True),
            pytest.raises(KwiConfigError),
        ):
            resolve_db_url(flag_value=None, config_path=config_file)

    def test_empty_flag_is_treated_as_none(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('database_url = "postgresql://config@host/db"\n')

        with patch.dict(os.environ, _env_without_kwi(), clear=True):
            result = resolve_db_url(flag_value="", config_path=config_file)
        assert result == "postgresql://config@host/db"
