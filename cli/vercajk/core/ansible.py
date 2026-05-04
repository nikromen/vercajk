from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from vercajk.core.exceptions import VercajkAnsibleException


@dataclass
class AnsibleObj:
    verbose: str = ""
    tags: list[str] = field(default_factory=list)
    skip_tags: list[str] = field(default_factory=list)
    check: bool = False


def setup_ansible_cmd(obj: AnsibleObj, inventory: Path | None = None) -> list[str]:
    base_cmd = ["ansible-playbook"]

    if inventory and inventory.exists():
        base_cmd.extend(["-i", str(inventory)])
    else:
        base_cmd.extend(["-i", "localhost,", "-c", "local"])

    if obj.verbose:
        base_cmd.append(obj.verbose)

    if obj.tags:
        base_cmd.append(f"--tags={','.join(obj.tags)}")

    if obj.skip_tags:
        base_cmd.append(f"--skip-tags={','.join(obj.skip_tags)}")

    if obj.check:
        base_cmd.extend(["--check", "--diff"])

    return base_cmd


def run_ansible_playbook(base_cmd: list[str], playbook_path: Path) -> None:
    if not playbook_path.exists():
        raise VercajkAnsibleException(f"Playbook not found: {playbook_path}")

    cmd = base_cmd + [str(playbook_path)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise VercajkAnsibleException(f"Ansible playbook failed: {e}") from e
