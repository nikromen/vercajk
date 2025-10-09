import click
from click import Context, pass_context

from vercajk.ansible import run_ansible_playbook, setup_ansible_cmd


@click.command("one-timers")
@pass_context
def one_timers(ctx: Context):
    """
    Run one timers playbook to set up the whole system globally.
    """
    playbook_path = ctx.obj.config.repo_path / "ansible" / "play_one_timers.yml"
    print(playbook_path)

    run_ansible_playbook(setup_ansible_cmd(ctx.obj.ansible_ctx), playbook_path)
