from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

if "libvirt" not in sys.modules:
    sys.modules["libvirt"] = MagicMock()

from vercajk.core.config import Config  # noqa: E402


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a minimal fake vercajk repo structure."""
    (tmp_path / "ansible").mkdir()
    (tmp_path / "ansible" / "play_dotfiles.yml").write_text("---\n")
    (tmp_path / "ansible" / "play_one_timers.yml").write_text("---\n")
    (tmp_path / "files").mkdir()
    (tmp_path / "files" / "image_template.ks.j2").write_text(
        "# kickstart\n{% if tags %}tags: {{ tags }}{% endif %}\n"
    )
    (tmp_path / "dotfiles").mkdir()
    (tmp_path / "dotfiles" / ".config").mkdir(parents=True)
    (tmp_path / "dotfiles" / ".config" / "bash").mkdir()
    (tmp_path / "inventory").write_text("[local]\nlocalhost ansible_connection=local\n")
    return tmp_path


@pytest.fixture
def mock_config(tmp_repo: Path) -> Config:
    return Config(repo_path=tmp_repo)


@pytest.fixture(autouse=True)
def patch_config(mock_config: Config):
    """Patch get_config to always return test config."""
    with patch("vercajk.core.config.get_config", return_value=mock_config):
        yield
