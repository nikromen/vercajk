"""Libvirt/QEMU image management for VM lifecycle."""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from stat import S_IRWXU
from time import sleep
from typing import TYPE_CHECKING

from vercajk.core.constants import ISO_MIME, QCOW2_MIME
from vercajk.core.exceptions import VercajkImageException
from vercajk.core.utils import (
    find_fst_number_in_str,
    get_mime,
    get_temporary_dir,
    streaming_copy,
)

if TYPE_CHECKING:
    import libvirt
    from libvirt import virDomain


def _get_libvirt():
    try:
        import libvirt

        return libvirt
    except ImportError:
        raise VercajkImageException(
            "libvirt-python is not installed. Install with: "
            "pip install libvirt-python (or poetry install --with vm)"
        )


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

        self._libvirt = _get_libvirt()
        self._connection: libvirt.virConnect | None = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = self._libvirt.open("qemu:///system")
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

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

        _libvirt = _get_libvirt()
        interfaces = domain.interfaceAddresses(
            _libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE,
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
        except self._libvirt.libvirtError:
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

    def fork_qcow2(self, dest: Path) -> Path:
        """Fork an existing qcow2 image and boot a new VM from it."""
        if not self._check_file(iso=False):
            raise VercajkImageException(f"Not a qcow2 file: {self.path}")

        dest_path = dest / f"{self.virt_name}.qcow2"
        streaming_copy(self.path, dest_path)

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

    @contextmanager
    def fork_qcow2_tmp(self) -> Iterator[tuple[virDomain, Path]]:
        """Fork qcow2 into a temp dir, yield domain + path, clean up after."""
        tmp_dest_path: Path | None = None
        try:
            with get_temporary_dir(S_IRWXU) as tmp_dir:
                tmp_dest_path = self.fork_qcow2(tmp_dir)
                domain = self._domain
                if domain is None:
                    raise VercajkImageException("Failed to find domain after fork")
                yield domain, tmp_dest_path
        finally:
            self._destroy_and_undefine_domain()
            if tmp_dest_path and tmp_dest_path.exists():
                tmp_dest_path.unlink()

    def destroy(self) -> None:
        """Destroy and undefine the domain."""
        self._destroy_and_undefine_domain()

    @staticmethod
    def destroy_by_name(name: str) -> None:
        """Destroy and undefine a domain by name."""
        libvirt = _get_libvirt()
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
    def list_domains() -> list[dict[str, str]]:
        """List all libvirt domains with their status."""
        libvirt = _get_libvirt()
        conn = libvirt.open("qemu:///system")
        try:
            domains = []
            for dom in conn.listAllDomains():
                state = "running" if dom.isActive() else "inactive"
                domains.append({"name": dom.name(), "state": state})
            return domains
        finally:
            conn.close()
