import click
from click import Choice, Context, pass_context

from vercajk.ansible import AnsibleObj
from vercajk.cli.ansible.dotfiles import dotfiles
from vercajk.cli.ansible.one_timers import one_timers
from vercajk.cli.ansible.update import update


@click.group("ansible")
@click.option(
    "-v",
    "--verbose",
    count=True,
    help=(
        "Ansible will be more verbose. Multiple -v will increase verbosity,"
        " max verbosity is at -vvvvvv."
    ),
)
@click.option(
    "-t",
    "--tag",
    type=Choice([]),
    multiple=True,
    help="Select tags to be passed to ansible playbook.",
)
@click.option(
    "--skip-tag",
    "-s",
    type=Choice([]),
    multiple=True,
    help="Select tags to be skipped in ansible playbook.",
)
@pass_context
def ansible(ctx: Context, verbose: int, tag: tuple[str], skip_tag: tuple[str]):
    """
    Run different ansible playbooks to the localhost.
    """
    verbose_str = ""
    if verbose != 0:
        verbose_str = "-" + (verbose * "v")

    ctx.obj.ansible_ctx = AnsibleObj(verbose_str, tag, skip_tag)


ansible.add_command(dotfiles)
ansible.add_command(one_timers)
ansible.add_command(update)
