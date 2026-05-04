from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

from vercajk.core.utils import require_tool


@click.command("iso")
@click.option(
    "--ks",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Kickstart file to embed into the ISO.",
)
@click.option(
    "--base-iso",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Base Fedora ISO to modify.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    default="./custom.iso",
    help="Output ISO path.",
)
def iso(ks: Path, base_iso: Path, output: Path) -> None:
    """Create a custom ISO with an embedded kickstart file.

    Uses mkksiso to inject the kickstart into a Fedora ISO, making it
    fully automated on boot without needing to pass kernel parameters manually.
    """
    require_tool("mkksiso", "sudo dnf install mkksiso")

    output = output.resolve()
    click.echo("Creating custom ISO with kickstart embedded...")
    click.echo(f"  Base ISO:   {base_iso}")
    click.echo(f"  Kickstart:  {ks}")
    click.echo(f"  Output:     {output}")

    cmd = ["mkksiso", "--ks", str(ks), str(base_iso), str(output)]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: mkksiso failed with exit code {e.returncode}", err=True)
        sys.exit(1)

    click.echo()
    click.echo(f"Custom ISO created: {output}")
    click.echo("You can now write it to USB with: vercajk image usb --iso <path>")
