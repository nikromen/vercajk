import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from stat import S_IRGRP, S_IROTH, S_IRWXU, S_IXGRP, S_IXOTH
from time import sleep
from typing import Optional

import libvirt
from libvirt import virDomain

from vercajk.constants import ISO_MIME, QCOW2_MIME
from vercajk.exceptions import VercajkImageException
from vercajk.spells import find_fst_number_in_str, get_mime, get_temporary_dir


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
        virt_name: Optional[str] = None,
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
        self.connection = libvirt.open("qemu:///system")

        if self._domain is not None:
            self._destroy_and_undefine_domain()

    def __del__(self) -> None:
        self.connection.close()

    def _destroy_and_undefine_domain(self) -> None:
        if self._domain.isActive():
            self._domain.destroy()

        self._domain.undefine()

    def _check_file(self, iso: bool) -> bool:
        mimetype = get_mime(self.path)
        return (mimetype == ISO_MIME and iso) or (mimetype == QCOW2_MIME and not iso)

    @staticmethod
    def ip(domain) -> Optional[str]:
        if not domain.isActive():
            return None

        interface = domain.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE,
        )
        print(interface.items())
        for key, val in interface.items():
            if key != "lo":
                return key["addrs"][0]["addr"]
        return None

    @property
    def _domain(self) -> Optional[virDomain]:
        try:
            return self.connection.lookupByName(self.virt_name)
        except libvirt.libvirtError:
            return None

    def _shutdown_domain_wait(self, max_limit: int = 10) -> bool:
        wait_seconds = 3
        for _ in range(10):
            if not self._domain.isActive():
                return True

            self._domain.shutdown()
            print(
                f"Waiting for {wait_seconds} seconds to shutdown domain {self._domain.name()}",
            )
            wait_seconds *= 2
            sleep(wait_seconds)

        return False

    def _img_console(self) -> int:
        if not self._domain.isActive():
            self._domain.create()

        if self.graphics in ["vnc", "spice"]:
            cmd = f"virt-viewer {self.virt_name}"
        else:
            cmd = f"virsh console {self.virt_name}"

        process = subprocess.run("sudo " + cmd, shell=True, check=True)
        return process.returncode

    def _img_console_loop(self) -> int:
        while True:
            retval = self._img_console()
            if retval != 0:
                return retval

            inp = None
            while inp is None:
                inp = input("Do you want to spawn console again? [y/n]")
                if inp.lower() not in ["y", "n"]:
                    inp = None

            if inp and inp.lower() == "n":
                break

        return retval

    @property
    def _base_virt_install_cmd(self) -> list[str]:
        return [
            "virt-install",
            f"--name={self.virt_name}",
            f"--memory={self.memory}",
            f"--vcpus={self.vcpus}",
            f"--os-variant={self.os_variant}",
            f"--network {self.network}",
            f"--console {self.console}",
            f"--graphics {self.graphics}",
            "--noautoconsole",
        ]

    def prepare(self, dest: Path) -> None:
        if not self._check_file(iso=True):
            raise VercajkImageException(f"Not an iso file: {self.path}")

        with get_temporary_dir(
            S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH,
        ) as tmp_dir:
            tmp_img = tmp_dir / f"{self.virt_name}.qcow2"
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", tmp_img, "20G"],
                check=True,
            )

            cmd = (
                ["sudo"]
                + self._base_virt_install_cmd
                + [
                    "--boot hd",
                    f"--location {self.path}",
                    f"--disk path={tmp_img},format=qcow2,size=20",
                ]
            )

            try:
                subprocess.run(" ".join(cmd), check=True, shell=True)

                retval = self._img_console_loop()
                if retval != 0:
                    raise VercajkImageException(f"Console exited with status {retval}")

                subprocess.run(
                    [
                        "qemu-img",
                        "convert",
                        "-O",
                        "qcow2",
                        tmp_img,
                        f"{dest!s}/{self.virt_name}.qcow2",
                    ],
                    check=True,
                )
            finally:
                self._destroy_and_undefine_domain()

    def fork_qcow2(self, dest: Path) -> Path:
        if not self._check_file(iso=False):
            raise VercajkImageException(f"Not a qcow2 file: {self.path}")

        dest_path = dest / f"{self.virt_name}.qcow2"
        dest_path.write_bytes(self.path.read_bytes())
        cmd = (
            ["sudo"]
            + self._base_virt_install_cmd
            + [
                f"--disk path={dest_path!s},format=qcow2",
                "--import",
            ]
        )

        subprocess.run(" ".join(cmd), check=True, shell=True)

        if self._domain.isActive():
            print("vole")
            input("haha")
            self._shutdown_domain_wait()

        return dest_path

    @contextmanager
    def fork_qcow2_tmp(self) -> Iterator[tuple[virDomain, Path]]:
        try:
            with get_temporary_dir(
                S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH,
            ) as tmp_dir:
                tmp_dest_path = self.fork_qcow2(tmp_dir)
                yield self._domain, tmp_dest_path
        finally:
            self._destroy_and_undefine_domain()
            tmp_dest_path.unlink()
