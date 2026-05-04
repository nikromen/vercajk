from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import click

from vercajk.core.ansible import AnsibleObj
from vercajk.core.config import Config, get_config
from vercajk.cli.ansible.base import ansible
from vercajk.cli.fish import fish
from vercajk.cli.image.base import image
from vercajk.cli.snapshot.base import snapshot
from vercajk.cli.test.base import test


@dataclass
class Obj:
    config: Config
    ansible_ctx: AnsibleObj = field(default_factory=AnsibleObj)


@click.group("vercajk", context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the vercajk repository (overrides config file).",
)
@click.pass_context
def vercajk_cli(ctx: click.Context, repo_path: Path | None) -> None:
    """Personal toolbox for Fedora/Rocky system provisioning."""
    try:
        config = get_config(repo_path_override=repo_path)
    except FileNotFoundError as e:
        if ctx.invoked_subcommand not in (None, "path"):
            raise click.ClickException(str(e))
        config = Config(repo_path=Path("."))

    ctx.obj = Obj(config=config)


@vercajk_cli.command("path")
@click.pass_context
def path(ctx: click.Context) -> None:
    """Print the configured vercajk repo path."""
    click.echo(ctx.obj.config.repo_path)


@vercajk_cli.command("version")
def version() -> None:
    """Print vercajk CLI version."""
    from importlib.metadata import version as pkg_version

    try:
        ver = pkg_version("vercajk")
    except Exception:
        ver = "development"
    click.echo(f"vercajk {ver}")


vercajk_cli.add_command(ansible)
vercajk_cli.add_command(fish)
vercajk_cli.add_command(image)
vercajk_cli.add_command(snapshot)
vercajk_cli.add_command(test)


if __name__ == "__main__":
    vercajk_cli()
