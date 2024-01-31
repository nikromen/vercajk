import click
from click import Context, pass_context

from vercajk.ansible import AnsibleObj, run_ansible_playbook, setup_ansible_cmd
from vercajk.path import vercajk_path


@click.command("system")
@click.option(
    "-p",
    "--playbook-path",
    is_flag=True,
    help="Print on stdout the path of system playbook path.",
)
@pass_context
def system(ctx: Context, playbook_path: bool):
    """
    Run system playbook to set up the whole system globally.
    """
    playbook_path = vercajk_path() / "ansible" / "play_system.yml"
    if playbook_path:
        print(playbook_path)
        exit(0)

    obj: AnsibleObj = ctx.obj
    cmd = setup_ansible_cmd(obj)
    run_ansible_playbook(cmd, playbook_path, obj.user_host_dict)
