from __future__ import annotations

import subprocess
import sys

import click
from click import Context, pass_context

from vercajk.core.ansible import run_ansible_playbook, setup_ansible_cmd
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
    inventory = repo_path / "inventory"

    maybe_create_snapshot(repo_path, ctx.obj.ansible_ctx.tags, auto_snapshot)

    if pull:
        click.echo("Pulling latest changes...")
        result = subprocess.run(
            ["git", "pull", "--ff-only", "--recurse-submodules"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"Git pull failed: {result.stderr}", err=True)
            sys.exit(1)
        click.echo(result.stdout.strip())

    if system:
        click.echo("Upgrading system packages...")
        dnf_result = subprocess.run(["sudo", "dnf", "upgrade", "--refresh", "-y"])
        if dnf_result.returncode != 0:
            click.echo("Warning: dnf upgrade failed.", err=True)

        click.echo("Updating flatpak apps...")
        flatpak_result = subprocess.run(["flatpak", "update", "-y"])
        if flatpak_result.returncode != 0:
            click.echo("Warning: flatpak update failed.", err=True)

    click.echo("Running one-timers playbook...")
    cmd = setup_ansible_cmd(ctx.obj.ansible_ctx, inventory=inventory)
    run_ansible_playbook(cmd, config.ansible_dir / "play_one_timers.yml")

    click.echo("Running dotfiles playbook...")
    run_ansible_playbook(cmd, config.ansible_dir / "play_dotfiles.yml")

    click.echo("Update complete.")
