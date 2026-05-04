from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.config import Config


class TestUpdateCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_update_help(self):
        result = self.runner.invoke(vercajk_cli, ["ansible", "update", "--help"])
        assert result.exit_code == 0
        assert "--pull" in result.output
        assert "--system" in result.output

    def test_update_pulls_repo(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Already up to date."

        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("subprocess.run", return_value=mock_result),
            patch("vercajk.core.ansible.run_ansible_playbook"),
        ):
            result = self.runner.invoke(
                vercajk_cli,
                ["ansible", "update", "--no-system"],
            )
            assert result.exit_code == 0
            assert "Pulling latest changes" in result.output

    def test_update_no_pull(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo)
        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("subprocess.run"),
            patch("vercajk.core.ansible.run_ansible_playbook"),
        ):
            result = self.runner.invoke(
                vercajk_cli,
                ["ansible", "update", "--no-pull", "--no-system"],
            )
            assert result.exit_code == 0
            assert "Pulling" not in result.output

    def test_update_git_pull_failure(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: Not a git repository"

        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = self.runner.invoke(
                vercajk_cli,
                ["ansible", "update", "--no-system"],
            )
            assert result.exit_code != 0
            assert "Git pull failed" in result.output
