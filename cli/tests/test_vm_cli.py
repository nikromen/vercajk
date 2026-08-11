from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli
from vercajk.core.config import Config
from vercajk.core.exceptions import VercajkImageException


class TestVmCreatePresets:
    def setup_method(self):
        self.runner = CliRunner()

    def test_preset_sets_memory_vcpus_graphics(self, tmp_repo: Path, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()
        config = Config(
            repo_path=tmp_repo,
            vm_presets={"heavy": {"memory": 8192, "vcpus": 4, "graphics": "spice,gl=on"}},
        )

        mock_image_instance = MagicMock()
        mock_image_instance.fork_qcow2.return_value = dest / "vm.qcow2"

        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.cli.image.vm.Image", return_value=mock_image_instance) as mock_image_cls,
        ):
            result = self.runner.invoke(
                vercajk_cli,
                [
                    "image",
                    "vm",
                    "create",
                    str(image_file),
                    "--fork",
                    "--preset",
                    "heavy",
                    "-d",
                    str(dest),
                ],
            )

        assert result.exit_code == 0, result.output
        _, kwargs = mock_image_cls.call_args
        assert kwargs["memory"] == 8192
        assert kwargs["vcpus"] == 4
        assert kwargs["graphics"] == "spice,gl=on"

    def test_explicit_flag_overrides_preset(self, tmp_repo: Path, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()
        config = Config(repo_path=tmp_repo, vm_presets={"heavy": {"memory": 8192}})

        mock_image_instance = MagicMock()
        mock_image_instance.fork_qcow2.return_value = dest / "vm.qcow2"

        with (
            patch("vercajk.core.config.get_config", return_value=config),
            patch("vercajk.cli.image.vm.Image", return_value=mock_image_instance) as mock_image_cls,
        ):
            result = self.runner.invoke(
                vercajk_cli,
                [
                    "image",
                    "vm",
                    "create",
                    str(image_file),
                    "--fork",
                    "--preset",
                    "heavy",
                    "-m",
                    "1024",
                    "-d",
                    str(dest),
                ],
            )

        assert result.exit_code == 0, result.output
        _, kwargs = mock_image_cls.call_args
        assert kwargs["memory"] == 1024

    def test_unknown_preset_errors_with_available_list(self, tmp_repo: Path, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()
        config = Config(repo_path=tmp_repo, vm_presets={"heavy": {"memory": 8192}})

        with patch("vercajk.core.config.get_config", return_value=config):
            result = self.runner.invoke(
                vercajk_cli,
                [
                    "image",
                    "vm",
                    "create",
                    str(image_file),
                    "--fork",
                    "--preset",
                    "nonexistent",
                    "-d",
                    str(dest),
                ],
            )

        assert result.exit_code != 0
        assert "Unknown preset 'nonexistent'" in result.output
        assert "heavy" in result.output

    def test_preset_without_any_configured_shows_none_defined(self, tmp_repo: Path, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()
        config = Config(repo_path=tmp_repo)

        with patch("vercajk.core.config.get_config", return_value=config):
            result = self.runner.invoke(
                vercajk_cli,
                [
                    "image",
                    "vm",
                    "create",
                    str(image_file),
                    "--fork",
                    "--preset",
                    "anything",
                    "-d",
                    str(dest),
                ],
            )

        assert result.exit_code != 0
        assert "(none defined)" in result.output

    def test_no_preset_uses_hardcoded_defaults(self, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()

        mock_image_instance = MagicMock()
        mock_image_instance.fork_qcow2.return_value = dest / "vm.qcow2"

        with patch(
            "vercajk.cli.image.vm.Image", return_value=mock_image_instance
        ) as mock_image_cls:
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "vm", "create", str(image_file), "--fork", "-d", str(dest)],
            )

        assert result.exit_code == 0, result.output
        _, kwargs = mock_image_cls.call_args
        assert kwargs["memory"] == 2048
        assert kwargs["graphics"] == "spice"

    def test_ephemeral_uses_create_overlay(self, tmp_path: Path):
        image_file = tmp_path / "base.qcow2"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()

        mock_image_instance = MagicMock()
        mock_image_instance.create_overlay.return_value = dest / "vm.qcow2"

        with patch("vercajk.cli.image.vm.Image", return_value=mock_image_instance):
            result = self.runner.invoke(
                vercajk_cli,
                [
                    "image",
                    "vm",
                    "create",
                    str(image_file),
                    "--fork",
                    "--ephemeral",
                    "-d",
                    str(dest),
                ],
            )

        assert result.exit_code == 0, result.output
        mock_image_instance.create_overlay.assert_called_once_with(dest)
        mock_image_instance.fork_qcow2.assert_not_called()

    def test_ephemeral_without_fork_errors(self, tmp_path: Path):
        image_file = tmp_path / "image.iso"
        image_file.write_bytes(b"data")
        dest = tmp_path / "dest"
        dest.mkdir()

        result = self.runner.invoke(
            vercajk_cli,
            ["image", "vm", "create", str(image_file), "--ephemeral", "-d", str(dest)],
        )
        assert result.exit_code != 0
        assert "--ephemeral requires --fork" in result.output


class TestVmDestroyConfirmation:
    def setup_method(self):
        self.runner = CliRunner()

    def test_aborts_without_confirmation(self):
        with patch("vercajk.cli.image.vm.Image.destroy_by_name") as mock_destroy:
            result = self.runner.invoke(
                vercajk_cli, ["image", "vm", "destroy", "my-vm"], input="n\n"
            )
        assert result.exit_code != 0
        mock_destroy.assert_not_called()

    def test_destroys_with_explicit_confirmation(self):
        with patch("vercajk.cli.image.vm.Image.destroy_by_name") as mock_destroy:
            result = self.runner.invoke(
                vercajk_cli, ["image", "vm", "destroy", "my-vm"], input="y\n"
            )
        assert result.exit_code == 0
        mock_destroy.assert_called_once_with("my-vm")

    def test_destroys_with_yes_flag_no_prompt(self):
        with patch("vercajk.cli.image.vm.Image.destroy_by_name") as mock_destroy:
            result = self.runner.invoke(vercajk_cli, ["image", "vm", "destroy", "my-vm", "--yes"])
        assert result.exit_code == 0
        mock_destroy.assert_called_once_with("my-vm")


class TestVmSnapshotCommands:
    def setup_method(self):
        self.runner = CliRunner()

    def test_snapshot_success(self):
        with patch("vercajk.cli.image.vm.Image.create_snapshot") as mock_create:
            result = self.runner.invoke(vercajk_cli, ["image", "vm", "snapshot", "my-vm"])
        assert result.exit_code == 0
        mock_create.assert_called_once_with("my-vm")
        assert "Snapshot created" in result.output

    def test_snapshot_failure(self):
        with patch(
            "vercajk.cli.image.vm.Image.create_snapshot",
            side_effect=VercajkImageException("VM 'my-vm' not found"),
        ):
            result = self.runner.invoke(vercajk_cli, ["image", "vm", "snapshot", "my-vm"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_revert_success(self):
        with patch("vercajk.cli.image.vm.Image.revert_to_snapshot") as mock_revert:
            result = self.runner.invoke(vercajk_cli, ["image", "vm", "revert", "my-vm"])
        assert result.exit_code == 0
        mock_revert.assert_called_once_with("my-vm")
        assert "reverted" in result.output

    def test_revert_failure(self):
        with patch(
            "vercajk.cli.image.vm.Image.revert_to_snapshot",
            side_effect=VercajkImageException("boom"),
        ):
            result = self.runner.invoke(vercajk_cli, ["image", "vm", "revert", "my-vm"])
        assert result.exit_code != 0
