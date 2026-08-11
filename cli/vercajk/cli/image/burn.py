from __future__ import annotations

import tempfile
from pathlib import Path

import click

from vercajk.cli.image.iso import iso
from vercajk.cli.image.kickstart import kickstart
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
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default="./custom.iso",
    help="Output ISO path.",
)
@click.pass_context
def burn(
    ctx: click.Context,
    base_iso: Path,
    fedora_version: int,
    tag: tuple[str, ...],
    output: Path,
) -> None:
    """Generate a kickstart and embed it into a custom ISO in one step.

    Writing the resulting ISO to a USB drive is left as a manual step -
    use `dd`, GNOME Disks, Fedora Media Writer, or similar.
    """
    output = output.resolve()
    with tempfile.TemporaryDirectory(prefix="vercajk-burn-") as tmpdir:
        ks_path = str(Path(tmpdir) / "output.ks")
        ctx.invoke(kickstart, tag=tag, output=ks_path, fedora_version=fedora_version)
        ctx.invoke(iso, ks=Path(ks_path), base_iso=base_iso, output=output)

    click.echo()
    click.echo(f"Custom ISO created: {output}")
    click.echo("Write it to a USB drive manually, e.g.:")
    click.echo(f"  sudo dd if={output} of=/dev/sdX bs=4M status=progress oflag=sync")
    click.echo("(or use GNOME Disks / usbimager / Fedora Media Writer)")
