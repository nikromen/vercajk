#!/bin/bash

# deal with stupid workspaces

hyprlock

# worskpaces may be confused
$WM_SCRIPTS/workspaces.sh --refresh

if pgrep -x waybar > /dev/null; then
    killall waybar
    waybar
fi
