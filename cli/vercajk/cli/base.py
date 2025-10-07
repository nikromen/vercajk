from typing import Any

import click

from vercajk.cli.ansible.base import ansible
from vercajk.cli.ci import ci
from vercajk.cli.fish import fish
from vercajk.cli.kickstart import kickstart
from vercajk.path import vercajk_path


def _get_context_settings() -> dict[str, Any]:
    return {"help_option_names": ["-h", "--help"]}


@click.group("vercajk", context_settings=_get_context_settings())
def vercajk_cli():
    pass


@vercajk_cli.command("path")
def path():
    """
    Get vercajk repo path.
    """
    print(vercajk_path())


vercajk_cli.add_command(ansible)
vercajk_cli.add_command(ci)
vercajk_cli.add_command(fish)
vercajk_cli.add_command(kickstart)


if __name__ == "__main__":
    vercajk_cli()
