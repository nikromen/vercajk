"""
Generate scripts, etc. for fish from bash config dir.
"""
import subprocess
import sys
from os import getcwd
from pathlib import Path


class Converterator3000:
    def __init__(self) -> None:
        self.cwd = Path(getcwd())
        self.bash_dir = self.cwd.parent / "bash"

    def get_variables(self) -> None:
        var_file_path = self.bash_dir / "variables"
        if not var_file_path.exists():
            return

        lines_for_fish_variables = []
        with open(var_file_path, "r") as var_file:
            for line in var_file:
                line_to_parse = line.strip().split("=", 1)
                lines_for_fish_variables.append(
                    f"set {line_to_parse[0]} {line_to_parse[1]}"
                )

        with open(self.cwd / "variables", "w") as fish_vars:
            for line in lines_for_fish_variables:
                fish_vars.write(line + "\n")

    def get_scripts(self) -> None:
        scripts_file_path = self.bash_dir / "custom_scripts"
        if not scripts_file_path.exists():
            return

        process = subprocess.run(
            ["bash", "-c", f". {str(scripts_file_path)}; compgen -A function"],
            stdout=subprocess.PIPE,
        )
        functions_to_call_in_bash = []
        for fn in process.stdout.decode().split():
            candidate = fn.strip()
            if not candidate.startswith("_"):
                functions_to_call_in_bash.append(candidate)

        fish_fn_template = (
            "function {fn_name}\n" "    call_in_bash {fn_name} $argv\n" "end\n\n"
        )
        lines = []
        for fn in functions_to_call_in_bash:
            lines.append(fish_fn_template.format(fn_name=fn))

        if lines:
            lines[-1] = lines[-1][:-1]

        with open(self.cwd / "call_in_bash_scripts.fish", "w") as cib_scripts_f:
            for line in lines:
                cib_scripts_f.write(line)


def _fail() -> None:
    print(f"Provide one of these args: {args}", file=sys.stderr)
    exit(1)


if __name__ == "__main__":
    args = ["variables", "scripts"]
    if len(sys.argv) < 1:
        _fail()

    converterator = Converterator3000()
    match sys.argv[1]:
        case "variables":
            converterator.get_variables()
        case "scripts":
            converterator.get_scripts()
        case _:
            _fail()
