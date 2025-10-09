import subprocess
from dataclasses import dataclass
from pathlib import Path


# TODO: inventory, users, hosts.... create file from it
@dataclass
class AnsibleObj:
    verbose: str
    tags: list[str]
    skip_tags: list[str]


def run_ansible_playbook(
    base_cmd: list[str],
    playbook_path: Path,
) -> None:
    cmd = base_cmd + [str(playbook_path)]
    subprocess.run(cmd, check=True)


def setup_ansible_cmd(obj: AnsibleObj) -> list[str]:
    base_cmd = ["ansible-playbook"]
    if obj.verbose:
        base_cmd.append(obj.verbose)

    if obj.tags:
        base_cmd.append(obj.tags)

    if obj.skip_tags:
        base_cmd.append(f"--skip-tags={','.join(obj.skip_tags)}")

    return base_cmd
