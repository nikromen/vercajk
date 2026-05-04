from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.config import Config


class TestKickstartCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_kickstart_generates_file(self, tmp_repo: Path, tmp_path: Path):
        output_file = tmp_path / "test.ks"
        config = Config(repo_path=tmp_repo)
        with patch("vercajk.core.config.get_config", return_value=config):
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "kickstart", "-o", str(output_file)],
            )
            assert result.exit_code == 0
            assert output_file.exists()
            assert "Kickstart file generated" in result.output

    def test_kickstart_with_tags(self, tmp_repo: Path, tmp_path: Path):
        output_file = tmp_path / "test.ks"
        config = Config(repo_path=tmp_repo)
        with patch("vercajk.core.config.get_config", return_value=config):
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "kickstart", "-t", "desktop", "-t", "kde", "-o", str(output_file)],
            )
            assert result.exit_code == 0
            content = output_file.read_text()
            assert "desktop" in content

    def test_kickstart_invalid_tag(self):
        result = self.runner.invoke(
            vercajk_cli,
            ["image", "kickstart", "-t", "nonexistent"],
        )
        assert result.exit_code != 0
