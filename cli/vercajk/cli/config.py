from __future__ import annotations

import getpass
from pathlib import Path

import click
import yaml

from vercajk.core.config import _USER_CONFIG_PATH


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@click.group("config")
def config():
    """Manage the vercajk configuration file."""


@config.command("init")
@click.option(
    "--repo-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Path to the vercajk repo. Prompted interactively if not given.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite the config file if it already exists.",
)
def init(repo_path: Path | None, force: bool) -> None:
    """Interactively create ~/.config/vercajk.yaml for this machine.

    Asks for the repo path, which users to provision here (e.g. both accounts
    on a shared desktop), and default ansible tags/skip-tags for this machine.
    """
    target = _USER_CONFIG_PATH
    if target.exists() and not force:
        raise click.ClickException(f"{target} already exists. Use --force to overwrite.")

    if repo_path is None:
        repo_path = (
            Path(
                click.prompt("Path to your vercajk repo", default=str(Path.cwd())),
            )
            .expanduser()
            .resolve()
        )

    users_str = click.prompt(
        "Target users on this machine (comma-separated)",
        default=getpass.getuser(),
    )
    target_users = _split_csv(users_str)

    tags_str = click.prompt(
        "Default ansible tags to run on this machine (comma-separated, empty = all)",
        default="",
        show_default=False,
    )
    tags = _split_csv(tags_str)

    skip_tags_str = click.prompt(
        "Default ansible tags to skip on this machine (comma-separated, empty = none)",
        default="",
        show_default=False,
    )
    skip_tags = _split_csv(skip_tags_str)

    data = {
        "repo_path": str(repo_path),
        "target_users": target_users,
        "tags": tags,
        "skip_tags": skip_tags,
    }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(data, sort_keys=False))

    click.echo(f"Wrote config to {target}")
