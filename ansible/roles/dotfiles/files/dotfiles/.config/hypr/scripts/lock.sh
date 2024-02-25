#!/bin/bash

# deal with stupid workspaces

hyprlock
$HOME/.config/hypr/scripts/workspaces.sh --refresh
killall waybar && waybar
