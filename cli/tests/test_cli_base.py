from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.config import Config


class TestVercajkCli:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(vercajk_cli, ["--help"])
        assert result.exit_code == 0
        assert "vercajk" in result.output
        assert "ansible" in result.output
        assert "image" in result.output
        assert "fish" in result.output

    def test_short_help(self):
        result = self.runner.invoke(vercajk_cli, ["-h"])
        assert result.exit_code == 0

    def test_path_command(self, tmp_repo: Path):
        config = Config(repo_path=tmp_repo)
        with patch("vercajk.core.config.get_config", return_value=config):
            result = self.runner.invoke(vercajk_cli, ["path"])
            assert result.exit_code == 0
            assert str(tmp_repo) in result.output


class TestAnsibleGroup:
    def setup_method(self):
        self.runner = CliRunner()

    def test_ansible_help(self):
        result = self.runner.invoke(vercajk_cli, ["ansible", "--help"])
        assert result.exit_code == 0
        assert "dotfiles" in result.output
        assert "one-timers" in result.output
        assert "update" in result.output

    def test_ansible_verbose_flag(self):
        result = self.runner.invoke(vercajk_cli, ["ansible", "-h"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_ansible_tag_choices(self):
        result = self.runner.invoke(vercajk_cli, ["ansible", "--help"])
        assert result.exit_code == 0
        assert "development_tools" in result.output


class TestImageGroup:
    def setup_method(self):
        self.runner = CliRunner()

    def test_image_help(self):
        result = self.runner.invoke(vercajk_cli, ["image", "--help"])
        assert result.exit_code == 0
        assert "kickstart" in result.output
        assert "iso" in result.output
        assert "usb" in result.output
        assert "vm" in result.output

    def test_image_vm_help(self):
        result = self.runner.invoke(vercajk_cli, ["image", "vm", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "destroy" in result.output
        assert "list" in result.output
