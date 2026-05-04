from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli


class TestUsbSafetyGuards:
    def setup_method(self):
        self.runner = CliRunner()

    def test_rejects_sda(self):
        with patch("vercajk.cli.image.usb.Path.exists", return_value=True):
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "usb", "--iso", "/dev/null", "--device", "/dev/sda"],
            )
        assert result.exit_code != 0
        assert "primary system disk" in result.output

    def test_rejects_nvme0n1(self):
        with patch("vercajk.cli.image.usb.Path.exists", return_value=True):
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "usb", "--iso", "/dev/null", "--device", "/dev/nvme0n1"],
            )
        assert result.exit_code != 0
        assert "primary system disk" in result.output

    def test_rejects_vda(self):
        with patch("vercajk.cli.image.usb.Path.exists", return_value=True):
            result = self.runner.invoke(
                vercajk_cli,
                ["image", "usb", "--iso", "/dev/null", "--device", "/dev/vda"],
            )
        assert result.exit_code != 0
        assert "primary system disk" in result.output

    def test_rejects_nonexistent_device(self):
        result = self.runner.invoke(
            vercajk_cli,
            ["image", "usb", "--iso", "/dev/null", "--device", "/dev/nonexistent_xyz"],
        )
        assert result.exit_code != 0
        assert "does not exist" in result.output


class TestUsbListDevices:
    def test_lists_devices_when_no_device_specified(self, tmp_path: Path):
        iso_file = tmp_path / "test.iso"
        iso_file.write_bytes(b"\x00" * 100)
        runner = CliRunner()

        mock_devices = [{"name": "/dev/sdb", "size": "8G", "model": "USB Drive"}]
        with patch("vercajk.cli.image.usb._list_block_devices", return_value=mock_devices):
            result = runner.invoke(
                vercajk_cli,
                ["image", "usb", "--iso", str(iso_file)],
            )
        assert result.exit_code == 0
        assert "/dev/sdb" in result.output
        assert "USB Drive" in result.output

    def test_no_devices_found(self, tmp_path: Path):
        iso_file = tmp_path / "test.iso"
        iso_file.write_bytes(b"\x00" * 100)
        runner = CliRunner()

        with patch("vercajk.cli.image.usb._list_block_devices", return_value=[]):
            result = runner.invoke(
                vercajk_cli,
                ["image", "usb", "--iso", str(iso_file)],
            )
        assert result.exit_code != 0
        assert "No removable USB devices found" in result.output
