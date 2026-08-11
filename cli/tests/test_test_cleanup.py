from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.exceptions import VercajkImageException


class TestCleanupConfirmation:
    def setup_method(self):
        self.runner = CliRunner()

    def test_aborts_without_confirmation(self):
        with patch("vercajk.cli.test.base.Image.destroy_by_name") as mock_destroy:
            result = self.runner.invoke(vercajk_cli, ["test", "cleanup"], input="n\n")
        assert result.exit_code != 0
        mock_destroy.assert_not_called()

    def test_cleans_up_with_yes_flag(self, tmp_path: Path):
        with (
            patch("vercajk.cli.test.base.Image.destroy_by_name") as mock_destroy,
            patch(
                "vercajk.cli.test.base._LIBVIRT_DIR",
                tmp_path,
            ),
        ):
            result = self.runner.invoke(vercajk_cli, ["test", "cleanup", "--yes"])
        assert result.exit_code == 0
        mock_destroy.assert_called_once()

    def test_handles_already_cleaned_up_vm(self, tmp_path: Path):
        with (
            patch(
                "vercajk.cli.test.base.Image.destroy_by_name",
                side_effect=VercajkImageException("not found"),
            ),
            patch("vercajk.cli.test.base._LIBVIRT_DIR", tmp_path),
        ):
            result = self.runner.invoke(vercajk_cli, ["test", "cleanup", "--yes"])
        assert result.exit_code == 0
        assert "already cleaned up" in result.output
