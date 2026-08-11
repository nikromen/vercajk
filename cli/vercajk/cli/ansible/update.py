from __future__ import annotations

import subprocess
import sys

import click
from click import Context, pass_context

from vercajk.cli.ansible.dotfiles import dotfiles
from vercajk.cli.ansible.one_timers import one_timers
from vercajk.core.ansible import apply_config_defaults
from vercajk.core.btrfs import maybe_create_snapshot


@click.command("update")
@click.option("--pull/--no-pull", default=True, help="Git pull the repo before running.")
@click.option("--system/--no-system", default=False, help="Also run dnf upgrade + flatpak update.")
@click.option(
    "--auto-snapshot/--no-auto-snapshot",
    default=False,
    help="Create a Btrfs snapshot before provisioning (allows rollback).",
)
@pass_context
def update(ctx: Context, pull: bool, system: bool, auto_snapshot: bool) -> None:
    """Update system: pull repo, run playbooks, optionally upgrade packages."""
    config = ctx.obj.config
    repo_path = config.repo_path

    apply_config_defaults(ctx.obj.ansible_ctx, config)
    maybe_create_snapshot(repo_path, ctx.obj.ansible_ctx.tags, auto_snapshot)

    if pull:
        click.echo("Pulling latest changes...")
        result = subprocess.run(
            ["git", "pull", "--ff-only", "--recurse-submodules"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            click.echo(f"Git pull failed: {result.stderr}", err=True)
            sys.exit(1)
        click.echo(result.stdout.strip())

    if system:
        click.echo("Upgrading system packages...")
        dnf_result = subprocess.run(["sudo", "dnf", "upgrade", "--refresh", "-y"], check=False)
        if dnf_result.returncode != 0:
            click.echo("Warning: dnf upgrade failed.", err=True)

        click.echo("Updating flatpak apps...")
        flatpak_result = subprocess.run(["flatpak", "update", "-y"], check=False)
        if flatpak_result.returncode != 0:
            click.echo("Warning: flatpak update failed.", err=True)

    # The snapshot was already handled above, so the sub-commands shouldn't create
    # their own (that would just delete-and-recreate it a second time for nothing).
    click.echo("Running one-timers playbook...")
    ctx.invoke(one_timers, auto_snapshot=False)

    click.echo("Running dotfiles playbook...")
    ctx.invoke(dotfiles, auto_snapshot=False)

    click.echo("Update complete.")
