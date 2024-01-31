#!/usr/bin/env python3


import subprocess
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Iterable

import click
from yaml import safe_load


class VercajkException(Exception):
    pass


def _get_vercajk_path() -> Path:
    vercajk_path_file = Path("~/.local/share/vercajk/vercajk_path").expanduser()
    if not vercajk_path_file.exists():
        raise VercajkException(
            "You have to first define the vercajk repo path to use this tool"
        )

    with open(vercajk_path_file, "r") as vercajk_path_f:
        return Path(vercajk_path_f.readline().strip())


def _get_user_specified_tools(what: tuple[str], tools: Iterable[Path]) -> list[Path]:
    result = []
    for tool in tools:
        if tool.name in what:
            result.append(tool)

    return result


@click.group()
def entry_point() -> None:
    pass


def _run_these_tools(vercajk_path: Path, excluded_tools: list[Path]) -> list[Path]:
    with open(vercajk_path / "vercajk" / "dependencies.yaml", "r") as deps_file:
        dependencies_yaml = safe_load(deps_file)

    graph = {tool["tool"]: set(tool["deps"]) for tool in dependencies_yaml}
    sorter = TopologicalSorter(graph)
    ordered_deps = [vercajk_path / "vercajk" / dep for dep in sorter.static_order()]
    run_these_tools = []
    for tool in ordered_deps:
        if tool in excluded_tools:
            run_these_tools.append(tool)
            excluded_tools.remove(tool)

    run_these_tools += excluded_tools
    return run_these_tools


@entry_point.command("update")
@click.option(
    "-e",
    "--exclude",
    type=str,
    required=False,
    multiple=True,
    help="Exclude these tools from update.",
)
@click.argument(
    "what",
    type=str,
    required=False,
    nargs=-1,
)
def update(exclude: tuple[str], what: tuple[str]) -> None:
    """
    Update vercajk from this repo to your Linux machine.

    Args:
        what: Specify what to update. Can be multiple.
    """
    vercajk_path = _get_vercajk_path()
    available_tools = list((Path(vercajk_path) / "vercajk").iterdir())
    available_tools.remove(Path(vercajk_path) / "vercajk" / "dependencies.yaml")
    if what:
        tools = _get_user_specified_tools(what, available_tools)
    else:
        tools = available_tools

    excluded_tools = []
    for tool in tools:
        if tool.name not in exclude:
            excluded_tools.append(tool)

    for tool in _run_these_tools(vercajk_path, excluded_tools):
        process = subprocess.run(["bash", tool / "_install.sh"], cwd=tool)
        if process.returncode != 0:
            exit(process.returncode)


@entry_point.command("test")
def test() -> None:
    """
    Test whether new changes will install in fresh Linux (fedora for now) installation

    Returns:
        Exits with failure if tests won't pass
    """
    process = subprocess.run(
        ["bash", "./test_deploy.sh"], cwd=_get_vercajk_path() / "test"
    )
    exit(process.returncode)


@entry_point.command("dir")
def vercajk_working_directory() -> None:
    """
    Print vercajk's directory
    """
    print(str(_get_vercajk_path()))


if __name__ == "__main__":
    entry_point()