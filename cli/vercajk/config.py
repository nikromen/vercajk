from dataclasses import dataclass
from pathlib import Path

import yaml

from vercajk.constants import SYSTEM_CONFIG_PATH, USER_CONFIG_PATH


@dataclass
class Config:
    repo_path: Path


class ConfigManager:
    @classmethod
    def get_config(cls) -> Config:
        for config_path in [USER_CONFIG_PATH, SYSTEM_CONFIG_PATH]:
            if not config_path.exists():
                continue

            with open(config_path) as f:
                data = yaml.safe_load(f)
                return Config(**data)

        raise FileNotFoundError(
            "No configuration file found in user or system paths. Please set up the configuration.",
        )
