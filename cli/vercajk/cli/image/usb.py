from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click


def _list_block_devices() -> list[dict[str, str]]:
    """List removable block devices suitable for USB writing."""
    result = subprocess.run(
        ["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL,TRAN,RM", "--json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    import json

    data = json.loads(result.stdout)
    devices = []
    for dev in data.get("blockdevices", []):
        if dev.get("rm") == "1" or dev.get("tran") == "usb":
            devices.append(
                {
                    "name": f"/dev/{dev['name']}",
                    "size": dev.get("size", "?"),
                    "model": dev.get("model", "Unknown").strip() if dev.get("model") else "Unknown",
                }
            )
    return devices


@click.command("usb")
@click.option(
    "--iso",
    "iso_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="ISO file to write to USB.",
)
@click.option(
    "--device",
    type=str,
    default=None,
    help="Target device (e.g. /dev/sdb). If not specified, shows available devices.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt.",
)
def usb(iso_path: Path, device: str | None, force: bool) -> None:
    """Write an ISO image to a USB drive.

    This uses dd to write the ISO directly to the device. The target device
    will be completely overwritten - ALL DATA WILL BE LOST.
    """
    if device is None:
        devices = _list_block_devices()
        if not devices:
            click.echo("No removable USB devices found.", err=True)
            sys.exit(1)

        click.echo("Available USB devices:")
        for dev in devices:
            click.echo(f"  {dev['name']}  {dev['size']}  {dev['model']}")
        click.echo()
        click.echo("Specify device with: vercajk image usb --iso <path> --device /dev/sdX")
        return

    dev_path = Path(device)
    if not dev_path.exists():
        click.echo(f"Error: Device {device} does not exist.", err=True)
        sys.exit(1)

    if dev_path.name.startswith(("sda", "nvme0n1", "vda")):
        click.echo(
            f"Error: {device} looks like a primary system disk. Refusing to proceed.",
            err=True,
        )
        sys.exit(1)

    if not force:
        click.echo(f"WARNING: This will DESTROY ALL DATA on {device}!")
        click.echo(f"  Writing: {iso_path}")
        click.echo(f"  Target:  {device}")
        if not click.confirm("Are you sure?"):
            click.echo("Aborted.")
            return

    click.echo(f"Writing {iso_path} to {device}...")

    # Unmount any mounted partitions on the device
    dev_name = Path(device).name
    for partition in sorted(Path("/dev/").glob(f"{dev_name}*")):
        subprocess.run(
            ["sudo", "umount", str(partition)],
            capture_output=True,
        )

    dd_cmd = [
        "sudo",
        "dd",
        f"if={iso_path}",
        f"of={device}",
        "bs=4M",
        "status=progress",
        "oflag=sync",
    ]

    try:
        subprocess.run(dd_cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: dd failed with exit code {e.returncode}", err=True)
        sys.exit(1)

    subprocess.run(["sync"], check=True)
    click.echo()
    click.echo(f"Done! USB drive {device} is ready to boot.")
