#!/bin/bash

# close all client windows
HYPRCMDS=$(hyprctl -j clients | jq -j '.[] | "dispatch closewindow address:\(.address); "')
hyprctl --batch "$HYPRCMDS" >> /tmp/hypr/hyprexitwithgrace.log 2>&1

# exit hyprland
hyprctl dispatch exit >> /tmp/hypr/hyprexitwithgrace.log 2>&1
