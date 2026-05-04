from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def get_temporary_dir(permissions: int | None = None) -> Iterator[Path]:
    temp_dir = Path(tempfile.mkdtemp())
    if permissions:
        os.chmod(temp_dir, permissions)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def find_fst_number_in_str(string: str) -> int | None:
    match = re.search(r"\d+", string)
    if match:
        return int(match[0])
    return None


def get_mime(path: Path) -> str:
    process = subprocess.run(
        ["file", "-b", "--mime-type", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout.strip()


def streaming_copy(src: Path, dest: Path, chunk_size: int = 8 * 1024 * 1024) -> None:
    """Copy a file using streaming to avoid loading entire file into memory."""
    with open(src, "rb") as fsrc, open(dest, "wb") as fdst:
        while chunk := fsrc.read(chunk_size):
            fdst.write(chunk)


def require_tool(name: str, install_hint: str) -> Path:
    """Ensure a CLI tool is available on PATH, or exit with install instructions."""
    import sys

    path = shutil.which(name)
    if not path:
        import click

        click.echo(f"Error: {name} not found. Install it with: {install_hint}", err=True)
        sys.exit(1)
    return Path(path)


def render_kickstart(template_path: Path, tags: list[str], fedora_version: int) -> str:
    """Render a kickstart Jinja2 template and return the rendered content."""
    import sys

    import jinja2

    if not template_path.exists():
        import click

        click.echo(f"Error: Kickstart template not found at {template_path}", err=True)
        sys.exit(1)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_path.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    return template.render(tags=tags, fedora_version=fedora_version)
