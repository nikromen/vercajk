from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import click
import requests

from vercajk.core.constants import ISO_MIME, QCOW2_MIME
from vercajk.core.exceptions import VercajkImageException
from vercajk.core.image import Image
from vercajk.core.utils import get_mime, get_temporary_dir


def _download_image(url: str, dest: Path) -> Path:
    """Download an image from URL, detect type, and return local path."""
    click.echo(f"Downloading image from {url}...")
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    unknown_file = dest / "image.download"
    with open(unknown_file, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8 * 1024 * 1024):
            f.write(chunk)

    mimetype = get_mime(unknown_file)
    if mimetype == ISO_MIME:
        img_name = dest / "image.iso"
    elif mimetype == QCOW2_MIME:
        img_name = dest / "image.qcow2"
    else:
        raise VercajkImageException(f"Unknown image type: {mimetype}")

    unknown_file.rename(img_name)
    return img_name


@click.group("vm")
def vm():
    """Manage virtual machines for testing."""


@vm.command("create")
@click.argument("image_path", type=str)
@click.option("-m", "--memory", default=2048, help="Memory in MB.")
@click.option("--vcpus", default=2, help="Number of virtual CPUs.")
@click.option("--os-variant", default="auto", help="OS variant for virt-install.")
@click.option("-n", "--network", default="bridge=virbr0", help="Network configuration.")
@click.option("-g", "--graphics", default="spice", help="Graphics type.")
@click.option("--name", "virt_name", default=None, help="VM name.")
@click.option(
    "--fork/--prepare",
    default=False,
    help="Fork existing qcow2 (--fork) or install from ISO (--prepare).",
)
@click.option(
    "-d",
    "--dest",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Destination directory for the created image.",
)
def create(
    image_path: str,
    memory: int,
    vcpus: int,
    os_variant: str,
    network: str,
    graphics: str,
    virt_name: str | None,
    fork: bool,
    dest: Path,
) -> None:
    """Create a VM from an ISO or qcow2 image.

    IMAGE_PATH can be a local file path or a URL to download.
    """

    def _run(src: Path) -> None:
        image = Image(
            src,
            memory=memory,
            vcpus=vcpus,
            os_variant=os_variant,
            network=network,
            graphics=graphics,
            virt_name=virt_name,
        )
        try:
            if fork:
                result_path = image.fork_qcow2(dest)
                click.echo(f"Forked image created: {result_path}")
            else:
                result_path = image.prepare(dest)
                click.echo(f"Prepared image created: {result_path}")
        except VercajkImageException as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    if urlparse(image_path).scheme:
        with get_temporary_dir() as tmp_dir:
            local_path = _download_image(image_path, tmp_dir)
            _run(local_path)
    else:
        _run(Path(image_path))


@vm.command("destroy")
@click.argument("name")
def destroy(name: str) -> None:
    """Destroy and undefine a VM by name."""
    try:
        Image.destroy_by_name(name)
        click.echo(f"VM '{name}' destroyed.")
    except VercajkImageException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@vm.command("list")
def list_vms() -> None:
    """List all libvirt VMs."""
    try:
        domains = Image.list_domains()
    except VercajkImageException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not domains:
        click.echo("No VMs found.")
        return

    click.echo(f"{'NAME':<30} {'STATE':<10}")
    click.echo("-" * 40)
    for d in domains:
        click.echo(f"{d['name']:<30} {d['state']:<10}")
