from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import click

from vercajk.core import config as config_module
from vercajk.core.ansible import AnsibleObj
from vercajk.cli.ansible.base import ansible
from vercajk.cli.completion import completion
from vercajk.cli.config import config as config_group
from vercajk.cli.fish import fish
from vercajk.cli.image.base import image
from vercajk.cli.snapshot.base import snapshot
from vercajk.cli.test.base import test


@dataclass
class Obj:
    repo_path_override: Path | None = None
    ansible_ctx: AnsibleObj = field(default_factory=AnsibleObj)
    # Set by the `fish` command group for its subcommands (scripts/variables).
    fish_store_to: Path | None = None
    _config: config_module.Config | None = field(default=None, repr=False, init=False)

    @property
    def config(self) -> config_module.Config:
        """Resolve the config lazily, so commands that don't need it (e.g. --help
        on any subcommand) work even without a config file present."""
        if self._config is None:
            try:
                self._config = config_module.get_config(
                    repo_path_override=self.repo_path_override,
                )
            except FileNotFoundError as e:
                raise click.ClickException(str(e)) from e
        return self._config


@click.group("vercajk", context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the vercajk repository (overrides config file).",
)
@click.pass_context
def vercajk_cli(ctx: click.Context, repo_path: Path | None) -> None:
    """Personal toolbox for Fedora/Rocky system provisioning."""
    ctx.obj = Obj(repo_path_override=repo_path)


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
vercajk_cli.add_command(completion)
vercajk_cli.add_command(config_group)
vercajk_cli.add_command(fish)
vercajk_cli.add_command(image)
vercajk_cli.add_command(snapshot)
vercajk_cli.add_command(test)


if __name__ == "__main__":
    vercajk_cli()
