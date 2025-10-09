import click


@click.command("update")
def update():
    """
    Run every playbook to update the system globally and also for user.
    """
    # TODO: also pull from git, check if vercajk is up to date, check if something needs to be pushed etc
