from __future__ import annotations

import getpass
import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

from vercajk.core.exceptions import VercajkConfigException

_USER_CONFIG_PATH = Path("~/.config/vercajk.yaml").expanduser()
_SYSTEM_CONFIG_PATH = Path("/etc/vercajk.yaml")
_ENV_REPO_PATH = "VERCAJK_REPO_PATH"


class Config(BaseModel):
    repo_path: Path
    target_users: list[str] = Field(default_factory=lambda: [getpass.getuser()])
    tags: list[str] = Field(default_factory=list)
    skip_tags: list[str] = Field(default_factory=list)
    vm_presets: dict[str, dict[str, int | str]] = Field(default_factory=dict)

    @field_validator("repo_path", mode="before")
    @classmethod
    def _resolve_repo_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser().resolve()

    @property
    def ansible_dir(self) -> Path:
        return self.repo_path / "ansible"

    @property
    def kickstart_template(self) -> Path:
        return self.repo_path / "files" / "image_template.ks.j2"

    @property
    def dotfiles_dir(self) -> Path:
        # Uses the repo-root convenience symlink (-> ansible/roles/dotfiles/files/dotfiles)
        # rather than the deep submodule path, so this stays valid if the role is reorganized.
        return self.repo_path / "dotfiles"


def get_config(repo_path_override: Path | None = None) -> Config:
    """Load config from env var, CLI override, or YAML files (in priority order)."""
    if repo_path_override:
        return Config(repo_path=repo_path_override)

    env_path = os.environ.get(_ENV_REPO_PATH)
    if env_path:
        return Config(repo_path=env_path)

    for config_path in (_USER_CONFIG_PATH, _SYSTEM_CONFIG_PATH):
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                raise VercajkConfigException(
                    f"Config file {config_path} is empty or invalid. "
                    f"Expected YAML with 'repo_path' key."
                )
            return Config(**data)

    raise FileNotFoundError(
        f"No configuration found. Set {_ENV_REPO_PATH} env var, "
        f"pass --repo-path, or create {_USER_CONFIG_PATH} or {_SYSTEM_CONFIG_PATH}."
    )
