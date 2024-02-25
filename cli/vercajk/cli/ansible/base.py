import os

import click
from click import Choice, Context, pass_context

from vercajk.ansible import AnsibleObj
from vercajk.cli.ansible.dotfiles import dotfiles
from vercajk.cli.ansible.system import system
from vercajk.cli.ansible.update import update
from vercajk.cli.ansible.user import user


def _get_user_host_d(targets: tuple[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for target in targets:
        split_target = [item.strip() for item in target.split(",")]
        host, user = split_target[0], split_target[1]
        if result.get(user):
            result[user].append(host)
        else:
            result[user] = [host]

    return result


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
    "-r",
    "--target",
    type=str,
    required=False,
    multiple=True,
    help=(
        "Specify host and user for which this has to be run separated"
        " by colon, e.g. localhost,nikromen."
    ),
)
@click.option(
    "-t",
    "--tag",
    type=Choice([]),
    multiple=True,
    help="Select tags to be passed to ansible playbook.",
)
@pass_context
def ansible(ctx: Context, verbose: int, target: tuple[str], tag: tuple[str]):
    """
    Run different ansible playbooks to the host to configure the system.
    """
    verbose_str = ""
    if verbose != 0:
        verbose_str = "-" + (verbose * "v")

    if target:
        user_host_d = _get_user_host_d(target)
    else:
        user_host_d = {os.getlogin(): ["localhost"]}

    tags = ""
    if tag:
        tags = ",".join(tag)

    ctx.obj = AnsibleObj(verbose_str, user_host_d, tags)


ansible.add_command(dotfiles)
ansible.add_command(system)
ansible.add_command(update)
ansible.add_command(user)
