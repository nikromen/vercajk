from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.config import Config


class TestMultiUserProvisioning:
    def setup_method(self):
        self.runner = CliRunner()

    def test_target_users_from_config_reach_ansible_cmd(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo, target_users=["alice", "bob"])
        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.core.ansible.subprocess.run") as mock_run,
        ):
            result = self.runner.invoke(vercajk_cli, ["ansible", "dotfiles"])
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert "-e" in cmd
            assert 'target_users=["alice", "bob"]' in cmd

    def test_cli_user_flag_overrides_config(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo, target_users=["alice", "bob"])
        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.core.ansible.subprocess.run") as mock_run,
        ):
            result = self.runner.invoke(
                vercajk_cli,
                ["ansible", "--user", "carol", "dotfiles"],
            )
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert 'target_users=["carol"]' in cmd

    def test_tags_from_config_reach_ansible_cmd(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo, tags=["desktop"], skip_tags=["games"])
        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.core.ansible.subprocess.run") as mock_run,
        ):
            result = self.runner.invoke(vercajk_cli, ["ansible", "one-timers"])
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert "--tags=desktop" in cmd
            assert "--skip-tags=games" in cmd

    def test_explicit_cli_tags_override_config(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo, tags=["desktop"])
        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.core.ansible.subprocess.run") as mock_run,
        ):
            result = self.runner.invoke(vercajk_cli, ["ansible", "-t", "rpm", "one-timers"])
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert "--tags=rpm" in cmd
