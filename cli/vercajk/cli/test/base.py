"""Automated VM testing for vercajk provisioning."""

from __future__ import annotations

import subprocess
from pathlib import Path

import click
import requests

from vercajk.core.constants import KICKSTART_TAGS
from vercajk.core.exceptions import VercajkImageException
from vercajk.core.image import Image, _get_libvirt
from vercajk.core.utils import render_kickstart, require_tool

_VM_NAME = "vercajk-test"
_ISO_CACHE_DIR = Path("~/.cache/vercajk/iso").expanduser()
_LIBVIRT_DIR = Path("/var/lib/libvirt/images/vercajk")

_FEDORA_ISO_DIR = (
    "https://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Everything/x86_64/iso/"
)
_FEDORA_ISO_PATTERN = "Fedora-Everything-netinst-x86_64-{version}-"


def _resolve_fedora_iso_url(version: int) -> tuple[str, str]:
    """Discover the actual ISO filename from the Fedora mirror directory listing."""
    import re

    dir_url = _FEDORA_ISO_DIR.format(version=version)
    resp = requests.get(dir_url)
    resp.raise_for_status()

    prefix = _FEDORA_ISO_PATTERN.format(version=version)
    pattern = re.escape(prefix) + r"[\d.]+\.iso"
    match = re.search(pattern, resp.text)
    if not match:
        raise click.ClickException(f"Could not find ISO filename for Fedora {version} at {dir_url}")
    filename = match.group(0)
    return dir_url + filename, filename


def _get_fedora_iso(version: int) -> Path:
    """Download Fedora Everything netinst ISO if not cached."""
    _ISO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cached = list(_ISO_CACHE_DIR.glob(f"Fedora-Everything-netinst-x86_64-{version}-*.iso"))
    if cached:
        click.echo(f"Using cached ISO: {cached[0]}")
        return cached[0]

    url, filename = _resolve_fedora_iso_url(version)
    iso_path = _ISO_CACHE_DIR / filename

    click.echo(f"Downloading Fedora {version} Everything netinst ISO...")
    click.echo(f"  URL: {url}")

    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(iso_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8 * 1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = (downloaded / total) * 100
                click.echo(
                    f"\r  {downloaded // (1024 * 1024)} MB / {total // (1024 * 1024)} MB ({pct:.0f}%)",
                    nl=False,
                )
    click.echo()
    click.echo(f"  Saved to: {iso_path}")
    return iso_path


def _cache_iso(iso_path: Path) -> None:
    """Symlink a user-provided ISO into the cache dir for future reuse."""
    _ISO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = _ISO_CACHE_DIR / iso_path.name
    if not cached.exists():
        cached.symlink_to(iso_path.resolve())
        click.echo(f"  Cached (symlink): {cached}")


def _generate_test_kickstart(config_repo: Path, tags: list[str], fedora_version: int) -> Path:
    """Generate a fully automated kickstart for testing."""
    output_dir = Path("~/.cache/vercajk").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    ks_path = output_dir / "test.ks"

    template_path = config_repo / "files" / "image_template.ks.j2"
    rendered = render_kickstart(template_path, tags, fedora_version)

    test_additions = """
# === VERCAJK TEST MODE ===
# Fully automated install for testing
text
user --name=testuser --password=testpassword --plaintext --groups=wheel
rootpw --plaintext testroot
autopart --type=plain
clearpart --all --initlabel
zerombr
"""
    lines = rendered.split("\n")
    insert_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("reboot")),
        len(lines),
    )
    lines.insert(insert_idx, test_additions)
    rendered = "\n".join(lines)

    ks_path.write_text(rendered)
    click.echo(f"Generated test kickstart: {ks_path}")
    return ks_path


def _create_custom_iso(ks_path: Path, base_iso: Path) -> Path:
    """Embed kickstart into ISO using mkksiso."""
    require_tool("mkksiso", "sudo dnf install lorax")

    subprocess.run(
        ["sudo", "mkdir", "-p", str(_LIBVIRT_DIR)],
        check=True,
    )
    output = _LIBVIRT_DIR / "vercajk-test.iso"
    click.echo("Creating custom ISO with embedded kickstart...")
    cmd = ["sudo", "mkksiso", "--ks", str(ks_path), str(base_iso), str(output)]
    subprocess.run(cmd, check=True)
    click.echo(f"  Custom ISO: {output}")
    return output


@click.group("test")
def test():
    """Automated VM testing for provisioning changes."""


@test.command("run")
@click.option(
    "-t",
    "--tag",
    type=click.Choice(KICKSTART_TAGS),
    multiple=True,
    help="Tags to include in kickstart.",
)
@click.option("--fedora-version", default=43, help="Fedora version to test with.")
@click.option(
    "--iso",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to an existing Fedora netinst ISO (skips download).",
)
@click.option("-m", "--memory", default=4096, help="VM memory in MB.")
@click.option("--vcpus", default=4, help="Number of virtual CPUs.")
@click.pass_context
def run_test(
    ctx: click.Context,
    tag: tuple[str, ...],
    fedora_version: int,
    iso: str | None,
    memory: int,
    vcpus: int,
) -> None:
    """Run a full automated VM test.

    Generates kickstart, downloads Fedora ISO, creates custom ISO,
    boots VM, and reports status.
    """
    config = ctx.obj.config
    tags = list(tag)

    click.echo("=== Vercajk VM Test ===")
    click.echo()

    if iso:
        base_iso = Path(iso)
        click.echo(f"Using provided ISO: {base_iso}")
        _cache_iso(base_iso)
    else:
        base_iso = _get_fedora_iso(fedora_version)
    ks_path = _generate_test_kickstart(config.repo_path, tags, fedora_version)
    custom_iso = _create_custom_iso(ks_path, base_iso)

    disk_path = _LIBVIRT_DIR / f"{_VM_NAME}.qcow2"

    if disk_path.exists():
        click.echo(f"Removing existing test disk: {disk_path}")
        subprocess.run(["sudo", "rm", "-f", str(disk_path)], check=True)

    click.echo("Creating VM disk...")
    subprocess.run(
        ["sudo", "qemu-img", "create", "-f", "qcow2", str(disk_path), "60G"],
        check=True,
    )

    click.echo(f"Starting VM installation (name={_VM_NAME})...")
    cmd = [
        "sudo",
        "virt-install",
        f"--name={_VM_NAME}",
        f"--memory={memory}",
        f"--vcpus={vcpus}",
        "--os-variant=auto",
        "--network=bridge=virbr0",
        "--graphics=spice",
        "--noautoconsole",
        f"--disk=path={disk_path},format=qcow2",
        f"--cdrom={custom_iso}",
    ]
    subprocess.run(cmd, check=True)

    click.echo()
    click.echo("VM installation started. The VM will:")
    click.echo("  1. Install Fedora from kickstart (fully automated)")
    click.echo("  2. Reboot after installation")
    click.echo("  3. Run first-boot provisioning service")
    click.echo()
    click.echo("Monitor with:")
    click.echo(f"  virt-viewer {_VM_NAME}")
    click.echo(f"  virsh console {_VM_NAME}")
    click.echo()
    click.echo("Check status with:")
    click.echo("  vercajk test status")
    click.echo()
    click.echo("When done:")
    click.echo("  vercajk test cleanup")


@test.command("status")
def status() -> None:
    """Show the status of the test VM."""
    libvirt = _get_libvirt()
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        click.echo(f"Cannot connect to libvirt: {e}", err=True)
        return

    try:
        domain = conn.lookupByName(_VM_NAME)
        state = "running" if domain.isActive() else "inactive"
        click.echo(f"VM: {_VM_NAME}")
        click.echo(f"State: {state}")

        if domain.isActive():
            ip = Image.get_ip(domain)
            if ip:
                click.echo(f"IP: {ip}")
                click.echo(f"SSH: ssh testuser@{ip}")
            else:
                click.echo("IP: not yet assigned (VM may still be installing)")
    except libvirt.libvirtError:
        click.echo(f"VM '{_VM_NAME}' not found. Run 'vercajk test run' first.")
    finally:
        conn.close()


@test.command("cleanup")
def cleanup() -> None:
    """Destroy the test VM and remove its disk."""
    try:
        Image.destroy_by_name(_VM_NAME)
        click.echo(f"VM '{_VM_NAME}' destroyed.")
    except VercajkImageException:
        click.echo(f"VM '{_VM_NAME}' not found (already cleaned up?).")

    disk_path = _LIBVIRT_DIR / f"{_VM_NAME}.qcow2"
    if disk_path.exists():
        subprocess.run(["sudo", "rm", "-f", str(disk_path)], check=True)
        click.echo(f"Disk removed: {disk_path}")

    custom_iso = _LIBVIRT_DIR / "vercajk-test.iso"
    if custom_iso.exists():
        subprocess.run(["sudo", "rm", "-f", str(custom_iso)], check=True)
        click.echo(f"Custom ISO removed: {custom_iso}")

    click.echo("Cleanup complete.")
