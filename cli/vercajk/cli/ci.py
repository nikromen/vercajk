from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Optional
from urllib.parse import urlparse

import click
import requests
from click import Context, pass_context
from libvirt import virDomain

from vercajk.ansible import AnsibleObj, run_ansible_playbook, setup_ansible_cmd
from vercajk.constants import ISO_MIME, QCOW2_MIME
from vercajk.exceptions import VercajkImageException
from vercajk.img import Image
from vercajk.path import vercajk_path
from vercajk.spells import get_mime, get_temporary_dir


@dataclass
class Obj:
    image_path: str


@click.group("ci")
@click.argument(
    "image_path",
    type=str,
)
@pass_context
def ci(ctx: Context, image_path: str):
    """
    Tool for testing the configuration.
    """
    ctx.obj = Obj(image_path=image_path)


def img_prep_or_fork(
    image_src: Path,
    memory: int,
    vcpus: int,
    os_variant: str,
    network: str,
    graphics: str,
    console: str,
    fork: bool,
    dest: Path,
    virt_name: Optional[str],
):
    image = Image(
        image_src,
        memory=memory,
        vcpus=vcpus,
        os_variant=os_variant,
        network=network,
        graphics=graphics,
        console=console,
        virt_name=virt_name,
    )

    if fork:
        print(image.fork_qcow2(Path(dest)))
        return

    image.prepare(dest)


def download_file_from_net(url: str, dest: Path) -> Path:
    resp = requests.get(url)
    resp.raise_for_status()
    unknown_file = dest / "image.unknown"
    with open(unknown_file, "wb") as f:
        f.write(resp.content)

    mimetype = get_mime(unknown_file)
    if mimetype == ISO_MIME:
        img_name = dest / "image.iso"
        unknown_file.rename(img_name)
    elif mimetype == QCOW2_MIME:
        img_name = dest / "image.qcow2"
        unknown_file.rename(img_name)
    else:
        raise VercajkImageException(f"Unknown image type: {mimetype}")

    return img_name


@ci.command("img")
@click.option(
    "-f",
    "--fork",
    is_flag=True,
    help="Fork the image from the source and create new domain.",
)
@click.option(
    "-p",
    "--prepare",
    is_flag=True,
    help="Prepare the image and log into the console of new VM.",
)
@click.option(
    "-m",
    "--memory",
    default=2048,
    help="Memory for the VM.",
)
@click.option(
    "-v",
    "--vcpus",
    default=2,
    help="Number of virtual CPUs.",
)
@click.option(
    "-o",
    "--os-variant",
    default="auto",
    help="OS variant for virt-install.",
)
@click.option(
    "-n",
    "--network",
    default="bridge=virbr0",
    help="Network for the VM.",
)
@click.option(
    "-g",
    "--graphics",
    default="spice",
    help="Graphics for the VM.",
)
@click.option(
    "-c",
    "--console",
    default="pty,target_type=serial",
    help="Console for the VM.",
)
@click.option(
    "-v",
    "--virt-name",
    default=None,
    help="Name of the VM.",
)
@click.argument(
    "dest",
    type=click.Path(exists=True, resolve_path=True, dir_okay=True, file_okay=False),
)
@pass_context
def img(
    ctx: Context,
    fork: bool,
    prepare: bool,
    memory: int,
    vcpus: int,
    os_variant: str,
    network: str,
    graphics: str,
    console: str,
    dest: str,
    virt_name: Optional[str],
):
    """
    Fork or prepare the image for testing purposes.
    Specify destination where the image will be stored.
    """
    if fork and prepare:
        raise click.UsageError("You can't use both --fork and --prepare.")

    if not fork and not prepare:
        raise click.UsageError("You have to use either --fork or --prepare.")

    dest = Path(dest)
    if not urlparse(ctx.obj.image_path).scheme:
        img_prep_or_fork(
            image_src=Path(ctx.obj.image_path),
            memory=memory,
            vcpus=vcpus,
            os_variant=os_variant,
            network=network,
            graphics=graphics,
            console=console,
            fork=fork,
            dest=dest,
            virt_name=virt_name,
        )
        return

    with get_temporary_dir() as tmp_dir:
        img_path = download_file_from_net(ctx.obj.image_path, tmp_dir)
        img_prep_or_fork(
            image_src=img_path,
            memory=memory,
            vcpus=vcpus,
            os_variant=os_variant,
            network=network,
            graphics=graphics,
            console=console,
            fork=fork,
            dest=dest,
            virt_name=virt_name,
        )


def _test_ansible_playbook_on_vm(image: Image, domain: virDomain) -> None:
    domain.create()
    print("60 sleep bo potrebuje naskocit")
    sleep(1)

    obj = AnsibleObj(
        verbose="",
        user_host_dict={"root": [image.ip(domain)]},
        tags="",
    )
    cmd = setup_ansible_cmd(obj)
    playbook_path = vercajk_path() / "ansible" / "play_system.yml"
    run_ansible_playbook(cmd, playbook_path, obj.user_host_dict)

    input("Press Enter to continue...")


@ci.command("test")
@pass_context
def test(ctx: Context):
    """
    Run the ansible scripts on the VM image.
    """
    if not urlparse(ctx.obj.image_path).scheme:
        path = Path(ctx.obj.image_path)
        image = Image(path, virt_name="fedora-minimal-86", os_variant="fedora39")
        with image.fork_qcow2_tmp() as (domain, tmp_dest_path):
            _test_ansible_playbook_on_vm(image, domain)
