from __future__ import annotations

import tempfile
from pathlib import Path

import click

from vercajk.cli.image.iso import iso
from vercajk.cli.image.kickstart import kickstart
from vercajk.cli.image.usb import usb
from vercajk.core.constants import KICKSTART_TAGS


@click.command("burn")
@click.option(
    "--iso",
    "base_iso",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Base Fedora netinst ISO.",
)
@click.option(
    "--fedora-version",
    type=int,
    default=43,
    help="Fedora version for the kickstart.",
)
@click.option(
    "-t",
    "--tag",
    type=click.Choice(KICKSTART_TAGS),
    multiple=True,
    help="Tags to include in kickstart (repeatable).",
)
@click.option(
    "--device",
    type=str,
    default=None,
    help="Target USB device (e.g. /dev/sdb). If not specified, shows available devices.",
)
@click.pass_context
def burn(
    ctx: click.Context,
    base_iso: Path,
    fedora_version: int,
    tag: tuple[str, ...],
    device: str | None,
) -> None:
    """Generate kickstart, embed into ISO, and write to USB in one step."""
    with tempfile.TemporaryDirectory(prefix="vercajk-burn-") as tmpdir:
        ks_path = str(Path(tmpdir) / "output.ks")
        custom_iso = Path(tmpdir) / "custom.iso"

        ctx.invoke(kickstart, tag=tag, output=ks_path, fedora_version=fedora_version)
        ctx.invoke(iso, ks=Path(ks_path), base_iso=base_iso, output=custom_iso)
        ctx.invoke(usb, iso_path=custom_iso, device=device, force=False)
