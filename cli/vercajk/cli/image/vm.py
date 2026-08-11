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
        f.writelines(resp.iter_content(chunk_size=8 * 1024 * 1024))

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
@click.option(
    "--preset",
    type=str,
    default=None,
    help="Named preset for memory/vcpus/graphics, defined under vm_presets in "
    "~/.config/vercajk.yaml. Explicit -m/--vcpus/-g flags below always override it.",
)
@click.option("-m", "--memory", type=int, default=None, help="Memory in MB.")
@click.option("--vcpus", type=int, default=None, help="Number of virtual CPUs.")
@click.option("--os-variant", default="auto", help="OS variant for virt-install.")
@click.option("-n", "--network", default="bridge=virbr0", help="Network configuration.")
@click.option("-g", "--graphics", default=None, help="Graphics type.")
@click.option("--name", "virt_name", default=None, help="VM name.")
@click.option(
    "--fork/--prepare",
    default=False,
    help="Fork existing qcow2 (--fork) or install from ISO (--prepare).",
)
@click.option(
    "--ephemeral",
    is_flag=True,
    help="With --fork: use a copy-on-write overlay instead of a full copy. The "
    "base image stays untouched, ideal for repeated throwaway experiments",
)
@click.option(
    "-d",
    "--dest",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Destination directory for the created image.",
)
@click.pass_context
def create(
    ctx: click.Context,
    image_path: str,
    preset: str | None,
    memory: int | None,
    vcpus: int | None,
    os_variant: str,
    network: str,
    graphics: str | None,
    virt_name: str | None,
    fork: bool,
    ephemeral: bool,
    dest: Path,
) -> None:
    """Create a VM from an ISO or qcow2 image.

    IMAGE_PATH can be a local file path or a URL to download.
    """
    if ephemeral and not fork:
        raise click.UsageError("--ephemeral requires --fork (needs an existing qcow2 base image).")

    preset_values: dict[str, int | str] = {}
    if preset is not None:
        vm_presets = ctx.obj.config.vm_presets
        if preset not in vm_presets:
            available = ", ".join(sorted(vm_presets)) or "(none defined)"
            raise click.UsageError(
                f"Unknown preset '{preset}'. Add it under vm_presets in "
                f"~/.config/vercajk.yaml, or choose one of: {available}"
            )
        preset_values = vm_presets[preset]

    memory = memory if memory is not None else int(preset_values.get("memory", 2048))
    vcpus = vcpus if vcpus is not None else int(preset_values.get("vcpus", 2))
    graphics = graphics if graphics is not None else str(preset_values.get("graphics", "spice"))

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
                if ephemeral:
                    result_path = image.create_overlay(dest)
                    click.echo(f"Ephemeral overlay VM created: {result_path}")
                else:
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
@click.confirmation_option(prompt="This will destroy and undefine the VM. Continue?")
def destroy(name: str) -> None:
    """Destroy and undefine a VM by name."""
    try:
        Image.destroy_by_name(name)
        click.echo(f"VM '{name}' destroyed.")
    except VercajkImageException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@vm.command("snapshot")
@click.argument("name")
def snapshot(name: str) -> None:
    """Create a quick-revert snapshot of a VM (replaces any previous one)."""
    try:
        Image.create_snapshot(name)
    except VercajkImageException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Snapshot created for VM '{name}'.")
    click.echo(f"Revert anytime with: vercajk image vm revert {name}")


@vm.command("revert")
@click.argument("name")
def revert(name: str) -> None:
    """Revert a VM to its last snapshot."""
    try:
        Image.revert_to_snapshot(name)
        click.echo(f"VM '{name}' reverted to snapshot.")
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
