from __future__ import annotations

from os import getcwd
from pathlib import Path

import click
from click import Context, pass_context

from vercajk.core.fish_converter import convert_scripts, convert_variables


@click.group("fish")
@click.option(
    "-p",
    "--path",
    type=click.Path(file_okay=False),
    default=None,
    help="Directory to store generated fish files.",
)
@pass_context
def fish(ctx: Context, path: str | None) -> None:
    """Migrate bash functions and variables to fish-compatible files."""
    config = ctx.obj.config
    ctx.obj.fish_store_to = Path(path or getcwd())
    ctx.obj.fish_bash_dir = config.dotfiles_dir / ".config" / "bash"


@fish.command("scripts")
@pass_context
def scripts(ctx: Context) -> None:
    """Generate fish function wrappers for bash scripts."""
    convert_scripts(ctx.obj.fish_bash_dir, ctx.obj.fish_store_to)
    click.echo("Fish scripts generated.")


@fish.command("variables")
@pass_context
def variables(ctx: Context) -> None:
    """Convert bash variables to fish format."""
    convert_variables(ctx.obj.fish_bash_dir, ctx.obj.fish_store_to)
    click.echo("Fish variables generated.")
