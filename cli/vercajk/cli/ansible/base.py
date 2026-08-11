import click
from click import Choice, Context, pass_context

from vercajk.core.ansible import AnsibleObj
from vercajk.core.constants import ANSIBLE_TAGS
from vercajk.cli.ansible.dotfiles import dotfiles
from vercajk.cli.ansible.one_timers import one_timers
from vercajk.cli.ansible.update import update


@click.group("ansible")
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase Ansible verbosity (up to -vvvvvv).",
)
@click.option(
    "-t",
    "--tag",
    type=Choice(ANSIBLE_TAGS),
    multiple=True,
    help="Tags to pass to ansible-playbook.",
)
@click.option(
    "-s",
    "--skip-tag",
    type=Choice(ANSIBLE_TAGS),
    multiple=True,
    help="Tags to skip in ansible-playbook.",
)
@click.option(
    "-u",
    "--user",
    "user",
    multiple=True,
    help="Target user(s) to provision (repeatable). Defaults to target_users from the config file.",
)
@click.option(
    "--check/--no-check",
    default=False,
    help="Dry-run mode: show what would change without applying.",
)
@click.option(
    "-K",
    "--ask-become-pass/--no-ask-become-pass",
    default=False,
    help="Prompt for the sudo/become password (needed unless passwordless sudo is configured).",
)
@pass_context
def ansible(
    ctx: Context,
    verbose: int,
    tag: tuple[str, ...],
    skip_tag: tuple[str, ...],
    user: tuple[str, ...],
    check: bool,
    ask_become_pass: bool,
):
    """Run Ansible playbooks on localhost."""
    verbose_str = ""
    if verbose > 0:
        verbose_str = "-" + ("v" * min(verbose, 6))

    # Tags/users are resolved against Config defaults later, in the leaf commands -
    # not here, so `vercajk ansible <subcommand> --help` keeps working without a config.
    ctx.obj.ansible_ctx = AnsibleObj(
        verbose=verbose_str,
        tags=list(tag),
        skip_tags=list(skip_tag),
        users=list(user),
        check=check,
        ask_become_pass=ask_become_pass,
    )


ansible.add_command(dotfiles)
ansible.add_command(one_timers)
ansible.add_command(update)
