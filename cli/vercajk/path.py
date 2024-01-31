from pathlib import Path

from vercajk.constants import VERCAJK_PATH, Pathlike


def create_vercajk_path(vercajk_repo_path: Pathlike) -> None:
    if isinstance(vercajk_repo_path, Path):
        vercajk_repo_path = str(vercajk_repo_path)

    with open(VERCAJK_PATH, "w") as f:
        f.write(vercajk_repo_path)


def vercajk_path() -> Path:
    if not VERCAJK_PATH.exists():
        raise FileNotFoundError(f"Vercajk path not defined in {VERCAJK_PATH}")

    with open(VERCAJK_PATH, "r") as vercajk_path_f:
        return Path(vercajk_path_f.readline().strip())
