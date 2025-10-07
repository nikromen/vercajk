# Flatpak Installation Process

The vercajk system now handles Flatpak installations through a systemd oneshot service that runs after the first boot. This approach solves issues that were encountered when trying to install Flatpak applications directly in the kickstart %post section.

## How It Works

1. During system installation, the kickstart file sets up:
   - Flatpak package installation
   - Flathub repository configuration
   - A systemd oneshot service called `vercajk-flatpak.service`

2. On first boot, the systemd service:
   - Runs after network connectivity is established
   - Executes the Ansible playbook with the `flatpak` tag
   - Creates a marker file to prevent re-running on subsequent boots

3. The Ansible playbook installs all flatpak applications based on your configuration.

## Flatpak Categories

The following flatpak application categories are available:

- **Core** - Essential applications (password managers, file managers, etc.)
- **Communication** - Messaging and communication tools
- **Dev Tools** - Development applications
- **Multimedia** - Media players and creative applications
- **Multimedia Extra** - Additional media applications
- **Games** - Gaming applications
- **Productivity** - Office and productivity tools
- **Browsers** - Web browsers

## Configuration

You can modify the flatpak applications installed by:

1. Editing the `ansible/group_vars/user_flatpak` file to add/remove applications
2. Adding/removing flatpak categories in your tags when generating kickstart files

## Troubleshooting

If flatpak applications are not installed after a system installation:

1. Check if the `vercajk-flatpak.service` is enabled:
   ```
   systemctl status vercajk-flatpak.service
   ```

2. Check if the ansible playbook and supporting files were properly installed:
   ```
   ls -l /etc/vercajk/ansible/
   ```

3. Run the flatpak installation manually:
   ```
   sudo ansible-playbook -t flatpak /etc/vercajk/ansible/play_user.yml
   ```

4. Check if the marker file exists:
   ```
   ls -l /var/lib/vercajk/flatpak-installed
   ```
   If it exists, remove it to re-enable the service and reboot.