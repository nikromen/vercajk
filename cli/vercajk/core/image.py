"""Libvirt/QEMU image management for VM lifecycle."""

from __future__ import annotations

import subprocess
from pathlib import Path
from stat import S_IRWXU
from time import sleep
from typing import TYPE_CHECKING

import libvirt

from vercajk.core.constants import ISO_MIME, QCOW2_MIME
from vercajk.core.exceptions import VercajkImageException
from vercajk.core.utils import (
    find_fst_number_in_str,
    get_mime,
    get_temporary_dir,
    streaming_copy,
)

if TYPE_CHECKING:
    from libvirt import virDomain

_SNAPSHOT_NAME = "vercajk-snapshot"


class Image:
    def __init__(
        self,
        path: Path,
        memory: int = 2048,
        vcpus: int = 2,
        os_variant: str = "auto",
        network: str = "bridge=virbr0",
        graphics: str = "spice",
        console: str = "pty,target_type=serial",
        virt_name: str | None = None,
    ) -> None:
        self.path = path
        f_num = find_fst_number_in_str(path.name) or "unknown"
        self.virt_name = virt_name or f"fedora-minimal-{f_num}"
        self.memory = memory
        self.vcpus = vcpus
        self.os_variant = os_variant
        self.network = network
        self.graphics = graphics
        self.console = console

        self._connection: libvirt.virConnect | None = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = libvirt.open("qemu:///system")
        return self._connection

    def _destroy_and_undefine_domain(self) -> None:
        domain = self._domain
        if domain is None:
            return
        if domain.isActive():
            domain.destroy()
        domain.undefine()

    def _check_file(self, iso: bool) -> bool:
        mimetype = get_mime(self.path)
        return (mimetype == ISO_MIME and iso) or (mimetype == QCOW2_MIME and not iso)

    @staticmethod
    def get_ip(domain: virDomain) -> str | None:
        if not domain.isActive():
            return None

        interfaces = domain.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE,
        )
        for iface_name, iface_data in interfaces.items():
            if iface_name == "lo":
                continue
            addrs = iface_data.get("addrs", [])
            if addrs:
                return addrs[0]["addr"]
        return None

    @property
    def _domain(self) -> virDomain | None:
        try:
            return self.connection.lookupByName(self.virt_name)
        except libvirt.libvirtError:
            return None

    def _shutdown_domain_wait(self, max_attempts: int = 10) -> bool:
        wait_seconds = 3
        for _ in range(max_attempts):
            domain = self._domain
            if domain is None or not domain.isActive():
                return True

            domain.shutdown()
            sleep(wait_seconds)
            wait_seconds = min(wait_seconds * 2, 60)

        return False

    @property
    def _base_virt_install_cmd(self) -> list[str]:
        return [
            "virt-install",
            f"--name={self.virt_name}",
            f"--memory={self.memory}",
            f"--vcpus={self.vcpus}",
            f"--os-variant={self.os_variant}",
            f"--network={self.network}",
            f"--console={self.console}",
            f"--graphics={self.graphics}",
            "--noautoconsole",
        ]

    def prepare(self, dest: Path) -> Path:
        """Install from ISO into a new qcow2, return the final image path."""
        if not self._check_file(iso=True):
            raise VercajkImageException(f"Not an ISO file: {self.path}")

        with get_temporary_dir(S_IRWXU) as tmp_dir:
            tmp_img = tmp_dir / f"{self.virt_name}.qcow2"
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", str(tmp_img), "20G"],
                check=True,
            )

            cmd = (
                ["sudo"]
                + self._base_virt_install_cmd
                + [
                    "--boot=hd",
                    f"--location={self.path}",
                    f"--disk=path={tmp_img},format=qcow2,size=20",
                ]
            )

            try:
                subprocess.run(cmd, check=True)
                self._wait_for_install_completion()

                dest_path = dest / f"{self.virt_name}.qcow2"
                subprocess.run(
                    ["qemu-img", "convert", "-O", "qcow2", str(tmp_img), str(dest_path)],
                    check=True,
                )
                return dest_path
            finally:
                self._destroy_and_undefine_domain()

    def _wait_for_install_completion(self) -> None:
        """Wait for domain to shut down after installation."""
        if not self._shutdown_domain_wait(max_attempts=60):
            raise VercajkImageException(
                f"VM '{self.virt_name}' did not shut down after installation"
            )

    def _import_disk_and_boot(self, dest_path: Path) -> Path:
        cmd = (
            ["sudo"]
            + self._base_virt_install_cmd
            + [
                f"--disk=path={dest_path},format=qcow2",
                "--import",
            ]
        )
        subprocess.run(cmd, check=True)

        domain = self._domain
        if domain and domain.isActive():
            self._shutdown_domain_wait()

        return dest_path

    def fork_qcow2(self, dest: Path) -> Path:
        """Fork an existing qcow2 image (full copy) and boot a new VM from it."""
        if not self._check_file(iso=False):
            raise VercajkImageException(f"Not a qcow2 file: {self.path}")

        dest_path = dest / f"{self.virt_name}.qcow2"
        streaming_copy(self.path, dest_path)
        return self._import_disk_and_boot(dest_path)

    def create_overlay(self, dest: Path) -> Path:
        """Boot a VM from a copy-on-write overlay of this qcow2 (backing file).

        The base image is never touched - discard the (much smaller) overlay
        file to instantly get back to a clean state.
        """
        if not self._check_file(iso=False):
            raise VercajkImageException(f"Not a qcow2 file: {self.path}")

        dest_path = dest / f"{self.virt_name}.qcow2"
        subprocess.run(
            [
                "qemu-img",
                "create",
                "-f",
                "qcow2",
                "-b",
                str(self.path),
                "-F",
                "qcow2",
                str(dest_path),
            ],
            check=True,
        )
        return self._import_disk_and_boot(dest_path)

    @staticmethod
    def destroy_by_name(name: str) -> None:
        """Destroy and undefine a domain by name."""
        conn = libvirt.open("qemu:///system")
        try:
            domain = conn.lookupByName(name)
            if domain.isActive():
                domain.destroy()
            domain.undefine()
        except libvirt.libvirtError as e:
            raise VercajkImageException(f"Failed to destroy VM '{name}': {e}") from e
        finally:
            conn.close()

    @staticmethod
    def create_snapshot(name: str) -> None:
        """Create (or replace) a single named libvirt snapshot for quick revert.

        Single-snapshot pattern, analogous to the host-level Btrfs snapshot in
        core/btrfs.py: any previous vercajk snapshot for this VM is replaced.
        """
        # TODO: maybe could be exended with snapshots experimenting on
        # multiple VMs/levels
        conn = libvirt.open("qemu:///system")
        try:
            conn.lookupByName(name)
        except libvirt.libvirtError as e:
            conn.close()
            raise VercajkImageException(f"VM '{name}' not found: {e}") from e
        conn.close()

        subprocess.run(
            ["virsh", "snapshot-delete", name, _SNAPSHOT_NAME],
            check=False,
            capture_output=True,
        )
        result = subprocess.run(
            ["virsh", "snapshot-create-as", name, _SNAPSHOT_NAME],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise VercajkImageException(
                f"Failed to create snapshot for VM '{name}': {result.stderr.strip()}"
            )

    @staticmethod
    def revert_to_snapshot(name: str) -> None:
        """Revert a VM to its vercajk snapshot (created via create_snapshot)."""
        result = subprocess.run(
            ["virsh", "snapshot-revert", name, _SNAPSHOT_NAME],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise VercajkImageException(f"Failed to revert VM '{name}': {result.stderr.strip()}")

    @staticmethod
    def list_domains() -> list[dict[str, str]]:
        """List all libvirt domains with their status."""
        conn = libvirt.open("qemu:///system")
        try:
            domains = []
            for dom in conn.listAllDomains():
                state = "running" if dom.isActive() else "inactive"
                domains.append({"name": dom.name(), "state": state})
            return domains
        finally:
            conn.close()
