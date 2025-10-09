from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import click

from vercajk.ansible import AnsibleObj
from vercajk.cli.ansible.base import ansible
from vercajk.cli.ci import ci
from vercajk.cli.fish import fish
from vercajk.cli.kickstart import kickstart
from vercajk.config import Config, ConfigManager


@dataclass
class Obj:
    config: Config
    ansible_ctx: Optional[AnsibleObj] = None


def _get_context_settings() -> dict[str, Any]:
    return {"help_option_names": ["-h", "--help"]}


@click.group("vercajk", context_settings=_get_context_settings())
@click.option(
    "--repo-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the vercajk repository.",
)
@click.pass_context
def vercajk_cli(ctx: click.Context, repo_path: Path):
    config = ConfigManager.get_config()
    if repo_path:
        config.repo_path = repo_path
    
    ctx.obj = Obj(config=config)


@vercajk_cli.command("path")
@click.pass_context
def path(ctx: click.Context):
    """
    Get vercajk repo path.
    """
    print(ctx.obj.config.repo_path)


vercajk_cli.add_command(ansible)
vercajk_cli.add_command(ci)
vercajk_cli.add_command(fish)
vercajk_cli.add_command(kickstart)


if __name__ == "__main__":
    vercajk_cli()
