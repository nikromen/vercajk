import click
from click import Context

from vercajk.ansible import run_ansible_playbook, setup_ansible_cmd


@click.command("dotfiles")
@click.pass_context
def dotfiles(ctx: Context):
    """
    Run dotfiles playbook to sync user specific dotfiles in home folder.
    """
    dotfile_playbook_path = ctx.obj.config.repo_path / "ansible" / "play_dotfiles.yml"
    print(dotfile_playbook_path)

    run_ansible_playbook(setup_ansible_cmd(ctx.ansible_ctx), dotfile_playbook_path)
