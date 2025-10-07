# Plymouth Integration in vercajk

vercajk now includes Plymouth integration for providing visual feedback during the installation process. This helps users understand what's happening during the post-installation setup.

## Features

- Visual progress indication during system configuration tasks
- Status messages for key installation steps
- Custom Ansible callback plugin to show playbook progress
- Clean system boot experience with appropriate feedback

## How It Works

1. Plymouth is used to display messages during the boot process
2. Custom systemd unit files display progress messages
3. A custom Ansible callback plugin sends task progress to Plymouth
4. Plymouth spinner is shown during long-running operations

## Implementation Details

### Temporary Installation

All installation components are now stored in temporary directories:
- Ansible playbooks and modules are in `/tmp/vercajk-install`
- Status flags are in `/tmp/vercajk-status`
- Everything is cleaned up after installation completes

### Plymouth Messages

During the post-installation phase, Plymouth will display the following types of messages:

- Start of each service execution
- Task names from Ansible playbooks
- Results of key operations
- Completion of installation steps

### Custom Callback Plugin

The system includes a custom Ansible callback plugin that:

- Integrates with Plymouth messaging system
- Shows playbook progress in real-time
- Provides task execution status
- Summarizes playbook results
- Is installed to the temporary directory at `/tmp/vercajk-install/callback_plugins/`

### Commands Used

The following Plymouth commands are used:

- `plymouth display-message --text="message"` - Displays text on the splash screen
- `plymouth change-mode --updates` - Changes Plymouth to progress mode for long operations
- `plymouth change-mode --system-boot` - Returns Plymouth to normal boot mode

## Troubleshooting

If Plymouth messages are not displayed:

1. Check if Plymouth is running (`plymouth --ping`)
2. Verify the Plymouth theme supports messages (`plymouth show-splash`)
3. Ensure the services are executing with appropriate permissions

For more information on Plymouth, see `man plymouth` or visit the [Plymouth documentation](https://www.freedesktop.org/wiki/Software/Plymouth/).