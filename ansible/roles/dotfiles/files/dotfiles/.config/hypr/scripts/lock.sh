#!/bin/bash

# deal with stupid workspaces

pidof hyprlock || hyprlock  # so hyprlock is called only once
$HOME/.config/hypr/scripts/workspaces.sh --refresh
killall waybar && waybar & disown
