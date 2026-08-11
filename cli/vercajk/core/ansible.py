from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from vercajk.core.exceptions import VercajkAnsibleException

if TYPE_CHECKING:
    from vercajk.core.config import Config


@dataclass
class AnsibleObj:
    verbose: str = ""
    tags: list[str] = field(default_factory=list)
    skip_tags: list[str] = field(default_factory=list)
    users: list[str] = field(default_factory=list)
    check: bool = False
    extra_vars: dict[str, list[str] | str] = field(default_factory=dict)


def apply_config_defaults(ansible_ctx: AnsibleObj, config: Config) -> None:
    """Fall back to machine-local Config defaults for anything not passed on the
    CLI. Explicit CLI flags (-t/-s/-u) always take precedence over the config."""
    if not ansible_ctx.tags:
        ansible_ctx.tags = list(config.tags)
    if not ansible_ctx.skip_tags:
        ansible_ctx.skip_tags = list(config.skip_tags)
    target_users = ansible_ctx.users or config.target_users
    ansible_ctx.extra_vars["target_users"] = list(target_users)


def resolve_inventory(repo_path: Path) -> Path:
    return repo_path / "inventory"


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

    for key, value in obj.extra_vars.items():
        value_str = json.dumps(value) if isinstance(value, list) else value
        base_cmd.extend(["-e", f"{key}={value_str}"])

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
