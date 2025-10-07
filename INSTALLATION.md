# Vercajk Installation Process

## Overview

The vercajk system now handles the installation in three phases:

1. **Kickstart Installation**: The base system is installed using the vercajk.ks kickstart file
2. **One-Time Setup**: System-wide configurations and application installations (including flatpaks) are performed by systemd services on first boot
3. **User-Specific Setup**: Dotfiles configuration for user "nikromen" is applied

## How It Works

### Kickstart Installation Phase

During the installation, the kickstart file:
- Installs the base system
- Sets up partitioning, users, and basic packages
- Creates systemd services for post-installation tasks

### First Boot Phase

On first boot, three systemd one-shot services run in sequence:

1. **vercajk-one-timers.service**:
   - Runs the `play_one_timers.yml` Ansible playbook
   - Configures system settings and installs applications
   - Installs flatpak applications system-wide for all users
   - Creates a completion flag at `/var/lib/vercajk/one-timers-completed`

2. **vercajk-dotfiles.service**:
   - Runs after one-timers completes
   - Runs the `play_dotfiles.yml` Ansible playbook specifically for user "nikromen"
   - Sets up all dotfiles and user-specific configurations
   - Creates a completion flag at `/var/lib/vercajk/dotfiles-completed`

3. **vercajk-cleanup.service**:
   - Runs after dotfiles completes
   - Removes all vercajk-related systemd service files
   - Reloads the systemd daemon to apply changes
   - Ensures no service artifacts remain after installation

## Manual Installation

If you need to trigger these processes manually after installation:

```bash
# Run the one-timers setup
sudo ansible-playbook /etc/vercajk/ansible/play_one_timers.yml

# Run the dotfiles setup for user nikromen
sudo -u nikromen ansible-playbook -e "hosts=localhost ansible_user=nikromen" /etc/vercajk/ansible/play_dotfiles.yml
```

## Notes

- Flatpak applications are now installed system-wide using the `system` method
- The ansible playbooks and configuration files are stored in `/etc/vercajk/ansible/`
- Status flags are stored in `/var/lib/vercajk/` to prevent re-running of completed tasks