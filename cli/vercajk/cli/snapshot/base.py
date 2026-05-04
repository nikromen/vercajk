"""CLI commands for Btrfs snapshot management."""

from __future__ import annotations

import click
from click import Context, pass_context

from vercajk.core.btrfs import (
    create_snapshot,
    delete_snapshot,
    get_snapshot_meta,
    is_btrfs,
    revert_snapshot,
)
from vercajk.core.exceptions import VercajkSnapshotException


@click.group("snapshot")
def snapshot():
    """Manage Btrfs snapshots for safe provisioning rollback."""


@snapshot.command("create")
@pass_context
def snapshot_create(ctx: Context) -> None:
    """Create a snapshot of the current system state.

    Replaces any existing vercajk snapshot (single-snapshot pattern).
    """
    if not is_btrfs("/"):
        raise click.ClickException("Root filesystem is not Btrfs. Cannot create snapshot.")

    config = ctx.obj.config
    ansible_ctx = ctx.obj.ansible_ctx

    click.echo("Creating Btrfs snapshot...")
    try:
        meta = create_snapshot(config.repo_path, tags=ansible_ctx.tags)
    except VercajkSnapshotException as e:
        raise click.ClickException(str(e)) from e

    click.echo(f"  Commit: {meta.commit}")
    click.echo(f"  Time:   {meta.timestamp}")
    click.echo("Snapshot created. Use 'vercajk snapshot revert' to rollback if needed.")


@snapshot.command("revert")
@click.confirmation_option(
    prompt="This will set the snapshot as boot default. Continue?",
)
def snapshot_revert() -> None:
    """Rollback to the last snapshot (requires reboot)."""
    try:
        message = revert_snapshot()
    except VercajkSnapshotException as e:
        raise click.ClickException(str(e)) from e

    click.echo(message)


@snapshot.command("status")
def snapshot_status() -> None:
    """Show the current snapshot status."""
    if not is_btrfs("/"):
        click.echo("Root filesystem is not Btrfs. Snapshots unavailable.")
        return

    meta = get_snapshot_meta()
    if meta is None:
        click.echo("No vercajk snapshot exists.")
        click.echo("Run 'vercajk snapshot create' or use --auto-snapshot with ansible commands.")
        return

    click.echo("Active snapshot:")
    click.echo(f"  Commit: {meta.commit}")
    click.echo(f"  Time:   {meta.timestamp}")
    if meta.tags:
        click.echo(f"  Tags:   {', '.join(meta.tags)}")
    click.echo()
    click.echo("To rollback: vercajk snapshot revert")
    click.echo("To delete:   vercajk snapshot delete")


@snapshot.command("delete")
@click.confirmation_option(prompt="Delete the current snapshot?")
def snapshot_delete() -> None:
    """Delete the existing snapshot to free disk space."""
    try:
        delete_snapshot()
    except VercajkSnapshotException as e:
        raise click.ClickException(str(e)) from e

    click.echo("Snapshot deleted.")
