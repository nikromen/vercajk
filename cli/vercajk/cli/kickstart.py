import os
import shutil
import sys
from pathlib import Path

import click
import jinja2

from vercajk.path import vercajk_path


def _get_kickstart_template_path() -> Path:
    """Get the path to the kickstart template file."""
    return Path(vercajk_path()) / "vercajk.ks"


def _render_kickstart_template(tags: list[str], output_file: str) -> None:
    """Render the kickstart template with the specified tags."""
    template_path = _get_kickstart_template_path()
    
    if not template_path.exists():
        print(f"Error: Kickstart template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create Jinja2 environment and load template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    
    # Render template with provided tags
    rendered_content = template.render(tags=tags)
    
    # Write to output file
    output_path = Path(output_file).resolve()
    with open(output_path, "w") as f:
        f.write(rendered_content)
    
    print(f"Kickstart file generated at: {output_path}")


@click.command("kickstart")
@click.option(
    "-t",
    "--tag",
    multiple=True,
    help="Tags to include in kickstart file (desktop, development-tools, kde, multi-user, vercajk, "
         "communication, multimedia, games, productivity)",
)
@click.option(
    "-o",
    "--output",
    default="./output.ks",
    help="Output kickstart file path",
)
def kickstart(tag: tuple[str], output: str):
    """
    Generate a kickstart file for Fedora installation based on vercajk configuration.
    
    This command creates a kickstart file that incorporates configurations from
    vercajk Ansible roles, allowing for a streamlined installation process.
    """
    tags = list(tag)
    _render_kickstart_template(tags, output)
    
    print("\nTo use this kickstart file for Fedora installation:")
    print("1. Copy it to a USB drive or make it accessible to the installer")
    print("2. At boot, press 'e' to edit the boot options")
    print(f"3. Add 'inst.ks=file:/path/to/{os.path.basename(output)}' to the kernel parameters")
    print("4. Press Ctrl+X to boot with these options")


if __name__ == "__main__":
    kickstart()