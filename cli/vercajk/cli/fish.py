from dataclasses import dataclass
from typing import Optional

import click
from click import Context, pass_context

from vercajk.fish_converter import Converterator3000


@dataclass
class Obj:
    conventerator: Converterator3000


@click.group("fish")
@click.option(
    "-p",
    "--path",
    type=str,
    default=None,
    help="Store results to this directory",
)
@pass_context
def fish(ctx: Context, path: Optional[str]):
    """
    Migrate bash functions and vars to fish compatible files.
    """
    ctx.obj = Obj(conventerator=Converterator3000(store_to=path))


@fish.command("scripts")
@pass_context
def scripts(ctx: Context):
    """
    Migrate bash scripts to fish compatible file.
    """
    ctx.obj.conventerator.get_scripts()


@fish.command("variables")
@pass_context
def variables(ctx: Context):
    """
    Migrate bash variables to fish compatible file.
    """
    ctx.obj.conventerator.get_variables()
