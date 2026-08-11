from __future__ import annotations

import os
from pathlib import Path

import click

_SNIPPETS = {
    "bash": 'eval "$(_VERCAJK_COMPLETE=bash_source vercajk)"',
    "zsh": 'eval "$(_VERCAJK_COMPLETE=zsh_source vercajk)"',
    "fish": "_VERCAJK_COMPLETE=fish_source vercajk | source",
}


def _detect_shell() -> str:
    shell_path = os.environ.get("SHELL", "")
    shell = Path(shell_path).name if shell_path else ""
    return shell if shell in _SNIPPETS else "bash"


@click.command("completion")
@click.option(
    "--shell",
    type=click.Choice(list(_SNIPPETS)),
    default=None,
    help="Shell to generate the completion snippet for (auto-detected from $SHELL if omitted).",
)
def completion(shell: str | None) -> None:
    """Print the shell snippet that enables tab-completion for vercajk.

    Add the output to your shell config, e.g.:

      vercajk completion --shell fish >> ~/.config/fish/config.fish

      vercajk completion --shell bash >> ~/.bashrc
    """
    click.echo(_SNIPPETS[shell or _detect_shell()])
