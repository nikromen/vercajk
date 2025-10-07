# Vercajk Kickstart

A kickstart file for automating Fedora installations with Vercajk configurations.

## Usage

Generate a customized kickstart file using the vercajk CLI tool:

```bash
# Generate a complete kickstart file with all configurations
vercajk kickstart -o my_kickstart.ks

# Generate a kickstart file with specific system tags
vercajk kickstart -t desktop -t development_tools -o custom.ks

# Generate a kickstart file with specific flatpak categories
vercajk kickstart -t desktop -t flatpak_browsers -t flatpak_productivity -o work_station.ks

# Generate a gaming setup
vercajk kickstart -t desktop -t flatpak_games -t flatpak_multimedia -o gaming_station.ks
```

## Available Tags

### System Tags
- `desktop`: Desktop environment packages including Hyprland
- `development_tools`: Programming languages, development tools, IDEs
- `kde`: KDE Plasma desktop environment
- `office`: LibreOffice suite
- `vercajk`: Vercajk CLI tool itself

### Flatpak Tags
- `flatpak_core`: Core flatpak applications (password managers, utilities)
- `flatpak_communication`: Communication apps (Discord, Signal, Telegram)
- `flatpak_multimedia`: Media players and image editors
- `flatpak_multimedia_extra`: Additional multimedia tools like Kdenlive
- `flatpak_dev_tools`: Development tools (Insomnia, Filezilla, Qt Designer)
- `flatpak_games`: Gaming applications (Steam, PrismLauncher, Lutris)
- `flatpak_productivity`: Office and productivity apps
- `flatpak_browsers`: Web browsers

## Using the Kickstart File

1. Copy the kickstart file to a USB drive or make it accessible to the installer
2. Boot from the Fedora installation media
3. At the boot menu, press 'e' to edit the boot options
4. Add `inst.ks=file:/path/to/kickstart.ks` to the kernel parameters
5. Press Ctrl+X to boot with these options

The installer will automatically proceed with the installation according to the configurations in the kickstart file.
