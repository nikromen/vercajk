from pathlib import Path

VERCAJK_DIR = Path("~/.local/share/vercajk").expanduser()
VERCAJK_PATH = VERCAJK_DIR / "vercajk_path"
ISO_MIME = "application/x-iso9660-image"
QCOW2_MIME = "application/x-qemu-disk"


# ==================================================================================== #


# Type aliases

Pathlike = Path | str


# ==================================================================================== #


# Ansible tags

# dotfiles

DOTFILES_TAGS = [""]
