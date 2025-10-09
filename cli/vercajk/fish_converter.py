"""
Generate scripts, etc. for fish from bash config dir.
"""

import subprocess
from os import getcwd
from pathlib import Path
from typing import Optional

from vercajk.config import ConfigManager


class FishToBashConverter(Exception):
    pass


class Converterator3000:
    def __init__(self, store_to: Optional[str]) -> None:
        self.store_to = Path(store_to or getcwd())
        vercajk_path = ConfigManager.get_config().repo_path
        self.bash_dir = vercajk_path / "dotfiles" / ".config" / "bash"

    def get_variables(self) -> None:
        var_file_path = self.bash_dir / "variables"
        if not var_file_path.exists():
            return

        lines_for_fish_variables = []
        with open(var_file_path) as var_file:
            for line in var_file:
                if line == "\n":
                    continue

                line_to_parse = line.strip().split("=", 1)
                lines_for_fish_variables.append(
                    f"set {line_to_parse[0]} {line_to_parse[1]}",
                )

        with open(self.store_to / "variables", "w") as fish_vars:
            for line in lines_for_fish_variables:
                fish_vars.write(line + "\n")

    def get_scripts(self) -> None:
        scripts_file_path = self.bash_dir / "custom_scripts"
        if not scripts_file_path.exists():
            return

        process = subprocess.run(
            ["bash", "-c", f". {scripts_file_path!s}; compgen -A function"],
            stdout=subprocess.PIPE,
        )
        functions_to_call_in_bash = []
        for fn in process.stdout.decode().split():
            candidate = fn.strip()
            if not candidate.startswith("_"):
                functions_to_call_in_bash.append(candidate)

        fish_fn_template = "function {fn_name}\n    call_in_bash {fn_name} $argv\nend\n\n"
        lines = []
        for fn in functions_to_call_in_bash:
            lines.append(fish_fn_template.format(fn_name=fn))

        if lines:
            lines[-1] = lines[-1][:-1]

        with open(self.store_to / "call_in_bash_scripts.fish", "w") as cib_scripts_f:
            for line in lines:
                cib_scripts_f.write(line)
