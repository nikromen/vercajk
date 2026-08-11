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
    # Store the raw path only; resolving config (and thus dotfiles_dir) happens
    # lazily in each subcommand, so `vercajk fish scripts --help` works without a
    # config file.
    ctx.obj.fish_store_to = Path(path or getcwd())


@fish.command("scripts")
@pass_context
def scripts(ctx: Context) -> None:
    """Generate fish function wrappers for bash scripts."""
    bash_dir = ctx.obj.config.dotfiles_dir / ".config" / "bash"
    convert_scripts(bash_dir, ctx.obj.fish_store_to)
    click.echo("Fish scripts generated.")


@fish.command("variables")
@pass_context
def variables(ctx: Context) -> None:
    """Convert bash variables to fish format."""
    bash_dir = ctx.obj.config.dotfiles_dir / ".config" / "bash"
    convert_variables(bash_dir, ctx.obj.fish_store_to)
    click.echo("Fish variables generated.")
