from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vercajk.core.constants import ISO_MIME, QCOW2_MIME
from vercajk.core.exceptions import VercajkImageException
from vercajk.core.image import Image


class FakeLibvirtError(Exception):
    pass


@pytest.fixture
def mock_libvirt():
    fake = MagicMock()
    fake.libvirtError = FakeLibvirtError
    with patch("vercajk.core.image.libvirt", fake):
        yield fake


class TestImageInit:
    def test_defaults(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42-x86_64.iso"))
        assert image.memory == 2048
        assert image.vcpus == 2
        assert image.virt_name == "fedora-minimal-42"

    def test_unknown_version_when_no_number_in_name(self, mock_libvirt):
        image = Image(Path("/tmp/custom.iso"))
        assert image.virt_name == "fedora-minimal-unknown"

    def test_explicit_virt_name_overrides(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"), virt_name="my-vm")
        assert image.virt_name == "my-vm"


class TestImageConnection:
    def test_connection_opens_lazily_once(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        assert mock_libvirt.open.call_count == 0
        conn1 = image.connection
        conn2 = image.connection
        assert conn1 is conn2
        mock_libvirt.open.assert_called_once_with("qemu:///system")


class TestCheckFile:
    def test_iso_file_matches_iso_check(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        with patch("vercajk.core.image.get_mime", return_value=ISO_MIME):
            assert image._check_file(iso=True) is True
            assert image._check_file(iso=False) is False

    def test_qcow2_file_matches_qcow2_check(self, mock_libvirt):
        image = Image(Path("/tmp/disk.qcow2"))
        with patch("vercajk.core.image.get_mime", return_value=QCOW2_MIME):
            assert image._check_file(iso=False) is True
            assert image._check_file(iso=True) is False


class TestGetIp:
    def test_returns_none_when_domain_inactive(self, mock_libvirt):
        domain = MagicMock()
        domain.isActive.return_value = False
        assert Image.get_ip(domain) is None

    def test_skips_loopback_and_returns_first_real_addr(self, mock_libvirt):
        domain = MagicMock()
        domain.isActive.return_value = True
        domain.interfaceAddresses.return_value = {
            "lo": {"addrs": [{"addr": "127.0.0.1"}]},
            "eth0": {"addrs": [{"addr": "192.168.1.5"}]},
        }
        assert Image.get_ip(domain) == "192.168.1.5"

    def test_returns_none_when_no_addrs(self, mock_libvirt):
        domain = MagicMock()
        domain.isActive.return_value = True
        domain.interfaceAddresses.return_value = {"eth0": {"addrs": []}}
        assert Image.get_ip(domain) is None


class TestDomainProperty:
    def test_returns_domain_when_found(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        found = MagicMock()
        image.connection.lookupByName.return_value = found
        assert image._domain is found

    def test_returns_none_when_not_found(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        image.connection.lookupByName.side_effect = FakeLibvirtError("not found")
        assert image._domain is None


class TestShutdownDomainWait:
    def test_returns_true_immediately_when_no_domain(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        with patch.object(Image, "_domain", new=None):
            assert image._shutdown_domain_wait() is True

    def test_returns_true_when_domain_already_inactive(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        domain = MagicMock()
        domain.isActive.return_value = False
        with patch.object(Image, "_domain", new=domain):
            assert image._shutdown_domain_wait() is True

    def test_shuts_down_after_a_few_attempts(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        domain = MagicMock()
        domain.isActive.side_effect = [True, True, False]
        with (
            patch.object(Image, "_domain", new=domain),
            patch("vercajk.core.image.sleep") as mock_sleep,
        ):
            assert image._shutdown_domain_wait(max_attempts=5) is True
        assert domain.shutdown.call_count == 2
        assert mock_sleep.call_count == 2

    def test_returns_false_when_never_shuts_down(self, mock_libvirt):
        image = Image(Path("/tmp/Fedora-42.iso"))
        domain = MagicMock()
        domain.isActive.return_value = True
        with (
            patch.object(Image, "_domain", new=domain),
            patch("vercajk.core.image.sleep"),
        ):
            assert image._shutdown_domain_wait(max_attempts=3) is False
        assert domain.shutdown.call_count == 3


class TestPrepare:
    def test_raises_when_not_iso(self, mock_libvirt, tmp_path: Path):
        image = Image(tmp_path / "disk.qcow2")
        with patch("vercajk.core.image.get_mime", return_value=QCOW2_MIME):
            with pytest.raises(VercajkImageException, match="Not an ISO file"):
                image.prepare(tmp_path)

    def test_happy_path_creates_and_converts_image(self, mock_libvirt, tmp_path: Path):
        image = Image(tmp_path / "Fedora-42.iso", virt_name="test-vm")
        dest = tmp_path / "dest"
        dest.mkdir()

        with (
            patch("vercajk.core.image.get_mime", return_value=ISO_MIME),
            patch("vercajk.core.image.subprocess.run") as mock_run,
            patch.object(Image, "_wait_for_install_completion"),
            patch.object(Image, "_destroy_and_undefine_domain") as mock_destroy,
        ):
            result_path = image.prepare(dest)

        assert result_path == dest / "test-vm.qcow2"
        assert mock_run.call_count == 3  # qemu-img create, virt-install, qemu-img convert
        mock_destroy.assert_called_once()


class TestForkQcow2:
    def test_raises_when_not_qcow2(self, mock_libvirt, tmp_path: Path):
        image = Image(tmp_path / "image.iso")
        with patch("vercajk.core.image.get_mime", return_value=ISO_MIME):
            with pytest.raises(VercajkImageException, match="Not a qcow2 file"):
                image.fork_qcow2(tmp_path)

    def test_happy_path_copies_and_boots(self, mock_libvirt, tmp_path: Path):
        src = tmp_path / "base.qcow2"
        src.write_bytes(b"fake-qcow2-data")
        dest = tmp_path / "dest"
        dest.mkdir()
        image = Image(src, virt_name="forked-vm")

        domain = MagicMock()
        domain.isActive.return_value = False

        with (
            patch("vercajk.core.image.get_mime", return_value=QCOW2_MIME),
            patch("vercajk.core.image.subprocess.run") as mock_run,
            patch.object(Image, "_domain", new=domain),
        ):
            result_path = image.fork_qcow2(dest)

        assert result_path == dest / "forked-vm.qcow2"
        assert result_path.read_bytes() == b"fake-qcow2-data"
        mock_run.assert_called_once()


class TestCreateOverlay:
    def test_raises_when_not_qcow2(self, mock_libvirt, tmp_path: Path):
        image = Image(tmp_path / "image.iso")
        with patch("vercajk.core.image.get_mime", return_value=ISO_MIME):
            with pytest.raises(VercajkImageException, match="Not a qcow2 file"):
                image.create_overlay(tmp_path)

    def test_creates_backing_file_overlay_without_copying(self, mock_libvirt, tmp_path: Path):
        src = tmp_path / "base.qcow2"
        src.write_bytes(b"fake-qcow2-data")
        dest = tmp_path / "dest"
        dest.mkdir()
        image = Image(src, virt_name="overlay-vm")

        domain = MagicMock()
        domain.isActive.return_value = False

        with (
            patch("vercajk.core.image.get_mime", return_value=QCOW2_MIME),
            patch("vercajk.core.image.subprocess.run") as mock_run,
            patch.object(Image, "_domain", new=domain),
        ):
            result_path = image.create_overlay(dest)

        assert result_path == dest / "overlay-vm.qcow2"
        # Overlay uses qemu-img create -b (backing file), not a full copy.
        assert not result_path.exists()
        overlay_cmd = mock_run.call_args_list[0].args[0]
        assert overlay_cmd[:3] == ["qemu-img", "create", "-f"]
        assert "-b" in overlay_cmd
        assert str(src) in overlay_cmd
        # Second call boots the VM via virt-install --import.
        boot_cmd = mock_run.call_args_list[1].args[0]
        assert "--import" in boot_cmd


class TestSnapshotAndRevert:
    def test_create_snapshot_success(self, mock_libvirt):
        conn = MagicMock()
        mock_libvirt.open.return_value = conn

        with patch(
            "vercajk.core.image.subprocess.run",
            return_value=MagicMock(returncode=0, stderr=""),
        ) as mock_run:
            Image.create_snapshot("some-vm")

        conn.lookupByName.assert_called_once_with("some-vm")
        conn.close.assert_called_once()
        # First call deletes any pre-existing snapshot, second creates the new one.
        assert mock_run.call_args_list[0].args[0][:2] == ["virsh", "snapshot-delete"]
        assert mock_run.call_args_list[1].args[0][:2] == ["virsh", "snapshot-create-as"]

    def test_create_snapshot_raises_when_vm_not_found(self, mock_libvirt):
        conn = MagicMock()
        conn.lookupByName.side_effect = FakeLibvirtError("no such domain")
        mock_libvirt.open.return_value = conn

        with pytest.raises(VercajkImageException, match="not found"):
            Image.create_snapshot("missing-vm")
        conn.close.assert_called_once()

    def test_create_snapshot_raises_when_virsh_fails(self, mock_libvirt):
        conn = MagicMock()
        mock_libvirt.open.return_value = conn

        def fake_run(cmd, **kwargs):
            if cmd[1] == "snapshot-create-as":
                return MagicMock(returncode=1, stderr="boom")
            return MagicMock(returncode=0, stderr="")

        with patch("vercajk.core.image.subprocess.run", side_effect=fake_run):
            with pytest.raises(VercajkImageException, match="Failed to create snapshot"):
                Image.create_snapshot("some-vm")

    def test_revert_to_snapshot_success(self, mock_libvirt):
        with patch(
            "vercajk.core.image.subprocess.run",
            return_value=MagicMock(returncode=0, stderr=""),
        ) as mock_run:
            Image.revert_to_snapshot("some-vm")

        cmd = mock_run.call_args.args[0]
        assert cmd == ["virsh", "snapshot-revert", "some-vm", "vercajk-snapshot"]

    def test_revert_to_snapshot_raises_on_failure(self, mock_libvirt):
        with patch(
            "vercajk.core.image.subprocess.run",
            return_value=MagicMock(returncode=1, stderr="no snapshot"),
        ):
            with pytest.raises(VercajkImageException, match="Failed to revert"):
                Image.revert_to_snapshot("some-vm")


class TestDestroyByName:
    def test_destroys_active_domain(self, mock_libvirt):
        conn = MagicMock()
        domain = MagicMock()
        domain.isActive.return_value = True
        conn.lookupByName.return_value = domain
        mock_libvirt.open.return_value = conn

        Image.destroy_by_name("some-vm")

        domain.destroy.assert_called_once()
        domain.undefine.assert_called_once()
        conn.close.assert_called_once()

    def test_raises_wrapped_exception_when_not_found(self, mock_libvirt):
        conn = MagicMock()
        conn.lookupByName.side_effect = FakeLibvirtError("no such domain")
        mock_libvirt.open.return_value = conn

        with pytest.raises(VercajkImageException, match="Failed to destroy VM"):
            Image.destroy_by_name("missing-vm")

        conn.close.assert_called_once()


class TestListDomains:
    def test_lists_running_and_inactive_domains(self, mock_libvirt):
        conn = MagicMock()
        running = MagicMock()
        running.name.return_value = "vm1"
        running.isActive.return_value = True
        inactive = MagicMock()
        inactive.name.return_value = "vm2"
        inactive.isActive.return_value = False
        conn.listAllDomains.return_value = [running, inactive]
        mock_libvirt.open.return_value = conn

        domains = Image.list_domains()

        assert domains == [
            {"name": "vm1", "state": "running"},
            {"name": "vm2", "state": "inactive"},
        ]
        conn.close.assert_called_once()

    def test_empty_when_no_domains(self, mock_libvirt):
        conn = MagicMock()
        conn.listAllDomains.return_value = []
        mock_libvirt.open.return_value = conn

        assert Image.list_domains() == []
