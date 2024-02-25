#!/bin/bash


set -e


# TODO: won;t switch for every keyboard
active_kb=$(hyprctl --instance "$HYPRLAND_INSTANCE" devices -j | jq -r ".keyboards | map(select(.main)) | .[0] | .name")
if [ -z "$active_kb" ]; then
    echo "No main keyboard found."
    exit 1
fi

hyprctl switchxkblayout "$active_kb" next

current_layout=$(hyprctl --instance "$HYPRLAND_INSTANCE" devices -j | jq -r ".keyboards | map(select(.main)) | .[0] | .active_keymap")
notify-send -e -u low -t 1500 -h string:x-canonical-private-synchronous:keyboard_notify -i "$HOME/.config/swaync/icons/keyboard.png" "$current_layout"
