import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnsibleObj:
    verbose: str
    user_host_dict: dict[str, list[str]]
    tags: str


def run_ansible_playbook(
    base_cmd: list[str], playbook_path: Path, user_host_dict: dict[str, list[str]]
) -> None:
    for user, hosts in user_host_dict.items():
        hosts_str = ",".join(hosts)
        cmd = base_cmd + [
            "-e",
            f"hosts={hosts_str} ansible_user={user}",
            str(playbook_path),
        ]
        print(cmd)
        subprocess.run(cmd, check=True)


def setup_ansible_cmd(obj: AnsibleObj) -> list[str]:
    base_cmd = ["ansible-playbook"]
    if obj.verbose:
        base_cmd.append(obj.verbose)

    if obj.tags:
        base_cmd.append(obj.tags)

    return base_cmd
