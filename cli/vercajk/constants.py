from pathlib import Path

USER_CONFIG_PATH = Path("~/.config/vercajk.yaml").expanduser()
SYSTEM_CONFIG_PATH = Path("/etc/vercajk.yaml")

ISO_MIME = "application/x-iso9660-image"
QCOW2_MIME = "application/x-qemu-disk"


# ==================================================================================== #


# Type aliases

Pathlike = Path | str


# ==================================================================================== #


# Ansible tags

# dotfiles

DOTFILES_TAGS = [""]
