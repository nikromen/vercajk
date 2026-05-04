from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from vercajk.core.config import Config, get_config


class TestConfig:
    def test_repo_path_resolves(self, tmp_path: Path):
        config = Config(repo_path=tmp_path)
        assert config.repo_path == tmp_path.resolve()

    def test_repo_path_expands_user(self):
        config = Config(repo_path="~/test")
        assert "~" not in str(config.repo_path)

    def test_ansible_dir(self, tmp_path: Path):
        config = Config(repo_path=tmp_path)
        assert config.ansible_dir == tmp_path / "ansible"

    def test_kickstart_template(self, tmp_path: Path):
        config = Config(repo_path=tmp_path)
        assert config.kickstart_template == tmp_path / "files" / "image_template.ks.j2"

    def test_dotfiles_dir(self, tmp_path: Path):
        config = Config(repo_path=tmp_path)
        assert config.dotfiles_dir == tmp_path / "dotfiles"


class TestGetConfig:
    def test_override_takes_priority(self, tmp_path: Path):
        config = get_config(repo_path_override=tmp_path)
        assert config.repo_path == tmp_path.resolve()

    def test_env_var_fallback(self, tmp_path: Path):
        with patch.dict(os.environ, {"VERCAJK_REPO_PATH": str(tmp_path)}):
            config = get_config()
            assert config.repo_path == tmp_path.resolve()

    def test_yaml_file_fallback(self, tmp_path: Path):
        config_file = tmp_path / "vercajk.yaml"
        config_file.write_text(f"repo_path: {tmp_path}\n")

        with patch("vercajk.core.config._USER_CONFIG_PATH", config_file):
            config = get_config()
            assert config.repo_path == tmp_path.resolve()

    def test_no_config_raises(self, tmp_path: Path):
        fake_path = tmp_path / "nonexistent.yaml"
        with (
            patch("vercajk.core.config._USER_CONFIG_PATH", fake_path),
            patch("vercajk.core.config._SYSTEM_CONFIG_PATH", fake_path),
            patch.dict(os.environ, {}, clear=True),
        ):
            with pytest.raises(FileNotFoundError):
                get_config()
