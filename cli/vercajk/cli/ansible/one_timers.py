import click
from click import Context, pass_context

from vercajk.core.ansible import run_ansible_playbook, setup_ansible_cmd
from vercajk.core.btrfs import maybe_create_snapshot


@click.command("one-timers")
@click.option(
    "--auto-snapshot/--no-auto-snapshot",
    default=False,
    help="Create a Btrfs snapshot before provisioning (allows rollback).",
)
@pass_context
def one_timers(ctx: Context, auto_snapshot: bool) -> None:
    """Run one-timers playbook for system-wide setup."""
    config = ctx.obj.config
    maybe_create_snapshot(config.repo_path, ctx.obj.ansible_ctx.tags, auto_snapshot)

    cmd = setup_ansible_cmd(ctx.obj.ansible_ctx)
    run_ansible_playbook(cmd, config.ansible_dir / "play_one_timers.yml")
