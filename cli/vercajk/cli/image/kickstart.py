from __future__ import annotations

import os
from pathlib import Path

import click

from vercajk.core.constants import KICKSTART_TAGS
from vercajk.core.utils import render_kickstart


@click.command("kickstart")
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
    type=click.Path(dir_okay=False, writable=True),
    default="./output.ks",
    help="Output kickstart file path.",
)
@click.option(
    "--fedora-version",
    type=int,
    default=43,
    help="Fedora version for the kickstart.",
)
@click.pass_context
def kickstart(ctx: click.Context, tag: tuple[str, ...], output: str, fedora_version: int) -> None:
    """Generate a kickstart file for Fedora installation."""
    config = ctx.obj.config
    rendered_content = render_kickstart(config.kickstart_template, list(tag), fedora_version)

    output_path = Path(output).resolve()
    output_path.write_text(rendered_content)

    click.echo(f"Kickstart file generated: {output_path}")
    click.echo()
    click.echo("To use this kickstart file:")
    click.echo("  1. Copy it to the boot USB or make it network-accessible")
    click.echo("  2. At boot, press 'e' to edit boot options")
    click.echo(f"  3. Append: inst.ks=file:/path/to/{os.path.basename(output)}")
    click.echo("  4. Press Ctrl+X to boot")
    click.echo()
    click.echo("Or use 'vercajk image iso' to embed it directly into an ISO.")
