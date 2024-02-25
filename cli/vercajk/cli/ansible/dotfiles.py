import click
from click import Context

from vercajk.ansible import AnsibleObj, run_ansible_playbook
from vercajk.path import vercajk_path


@click.command("dotfiles")
@click.option(
    "-p",
    "--playbook-path",
    is_flag=True,
    help="Print on stdout the path of dotfile playbook path.",
)
@click.pass_context
def dotfiles(ctx: Context, playbook_path: bool):
    """
    Run dotfiles playbook to sync user specific dotfiles in home folder.
    """
    dotfile_playbook_path = vercajk_path() / "ansible" / "play_dotfiles.yml"
    if playbook_path:
        print(dotfile_playbook_path)
        exit(0)

    obj: AnsibleObj = ctx.obj

    base_cmd = ["ansible-playbook"]
    if obj.verbose:
        base_cmd.append(obj.verbose)

    if obj.tags:
        base_cmd.append(obj.tags)

    run_ansible_playbook(base_cmd, dotfile_playbook_path, obj.user_host_dict)
