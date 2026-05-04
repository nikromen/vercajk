import click

from vercajk.cli.image.burn import burn
from vercajk.cli.image.iso import iso
from vercajk.cli.image.kickstart import kickstart
from vercajk.cli.image.usb import usb
from vercajk.cli.image.vm import vm


@click.group("image")
def image():
    """Manage system images - kickstart, ISO, USB, and VM operations."""


image.add_command(burn)
image.add_command(kickstart)
image.add_command(iso)
image.add_command(usb)
image.add_command(vm)
