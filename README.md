## Vercajk

This is my personal vercajk [read user-specific scripts] (from German werkzeug). Most of the tools are meant to be
user-specific, but it's possible to install them for root (e.g. in container).

#### I do not recommend to install this tool since it is designed for my personal needs. But you can still copy some scripts if you like them :D

Also note that these scripts has hardcoded paths, and it is currently meant only for Fedora and Rocky Linux.

## Features

### Kickstart Installation

Vercajk now includes a customizable kickstart file for Fedora installations. You can generate a kickstart file with specific tags to include only the features you need.

```bash
vercajk-cli kickstart --tag desktop --tag development-tools -o my_kickstart.ks
```

Available tags:
- `desktop` - Desktop environment setup
- `development-tools` - Development tools and IDEs
- `kde` - KDE Plasma desktop environment
- `multi-user` - Multi-user setup with shared documents
- `vercajk` - Install vercajk tools
- `communication` - Communication tools (Discord, Signal, etc.)
- `multimedia` - Multimedia applications
- `games` - Gaming applications
- `productivity` - Office and productivity tools

See [FLATPAK.md](FLATPAK.md) for information about the Flatpak installation process.

See [PLYMOUTH.md](PLYMOUTH.md) for information about the Plymouth integration providing visual feedback during installation.
