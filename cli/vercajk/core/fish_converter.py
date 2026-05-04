"""Generate fish shell config from bash config directory."""

from __future__ import annotations

import subprocess
from pathlib import Path


class FishConverterError(Exception):
    pass


def convert_variables(bash_dir: Path, store_to: Path) -> None:
    """Convert bash variable definitions to fish `set -gx` format."""
    var_file_path = bash_dir / "variables"
    if not var_file_path.exists():
        return

    lines_for_fish_variables = []
    with open(var_file_path) as var_file:
        for line in var_file:
            if line.strip() == "" or line.startswith("#"):
                continue

            parts = line.strip().split("=", 1)
            if len(parts) != 2:
                continue

            name, value = parts
            value = value.strip('"').strip("'")
            lines_for_fish_variables.append(f"set -gx {name} {value}")

    output_dir = store_to / "variables"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "variables", "w") as fish_vars:
        for line in lines_for_fish_variables:
            fish_vars.write(line + "\n")


def convert_scripts(bash_dir: Path, store_to: Path) -> None:
    """Generate fish function wrappers that delegate to bash functions."""
    scripts_file_path = bash_dir / "custom_scripts"
    if not scripts_file_path.exists():
        return

    process = subprocess.run(
        ["bash", "-c", f". {scripts_file_path!s}; compgen -A function"],
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise FishConverterError(f"Failed to extract bash functions: {process.stderr}")

    functions_to_call_in_bash = [
        fn.strip() for fn in process.stdout.split() if fn.strip() and not fn.strip().startswith("_")
    ]

    fish_fn_template = "function {fn_name}\n    call_in_bash {fn_name} $argv\nend\n\n"
    lines = [fish_fn_template.format(fn_name=fn) for fn in functions_to_call_in_bash]

    if lines:
        lines[-1] = lines[-1].rstrip("\n") + "\n"

    with open(store_to / "call_in_bash_scripts.fish", "w") as f:
        f.writelines(lines)
