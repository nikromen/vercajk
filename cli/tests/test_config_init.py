from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml
from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli


class TestConfigInit:
    def setup_method(self):
        self.runner = CliRunner()

    def test_creates_config_file(self, tmp_path: Path):
        target = tmp_path / "vercajk.yaml"
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        with patch("vercajk.cli.config._USER_CONFIG_PATH", target):
            result = self.runner.invoke(
                vercajk_cli,
                ["config", "init", "--repo-path", str(repo_dir)],
                input="alice,bob\ndesktop\ngames\n",
            )

        assert result.exit_code == 0, result.output
        assert target.exists()
        data = yaml.safe_load(target.read_text())
        assert data["repo_path"] == str(repo_dir)
        assert data["target_users"] == ["alice", "bob"]
        assert data["tags"] == ["desktop"]
        assert data["skip_tags"] == ["games"]

    def test_refuses_to_overwrite_without_force(self, tmp_path: Path):
        target = tmp_path / "vercajk.yaml"
        target.write_text("repo_path: /existing\n")
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        with patch("vercajk.cli.config._USER_CONFIG_PATH", target):
            result = self.runner.invoke(
                vercajk_cli,
                ["config", "init", "--repo-path", str(repo_dir)],
            )

        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_force_overwrites_existing(self, tmp_path: Path):
        target = tmp_path / "vercajk.yaml"
        target.write_text("repo_path: /existing\n")
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        with patch("vercajk.cli.config._USER_CONFIG_PATH", target):
            result = self.runner.invoke(
                vercajk_cli,
                ["config", "init", "--repo-path", str(repo_dir), "--force"],
                input="\n\n\n",
            )

        assert result.exit_code == 0, result.output
        data = yaml.safe_load(target.read_text())
        assert data["repo_path"] == str(repo_dir)
