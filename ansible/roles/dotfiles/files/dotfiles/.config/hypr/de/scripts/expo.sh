#!/bin/bash


set -e

active_monitor_id=$(hyprctl -j monitors | jq -r ".[] | select(.focused == true) | .id")
first_workspace_id=$(hyprctl -j workspaces | jq -r ".[] | select(.monitorID == $active_monitor_id and (.name | startswith(\"special:\") | not)) | .id" | sort -r -t _ -g | tail -n 1)
hyprctl --batch "dispatch workspace $first_workspace_id; dispatch hyprexpo:expo toggle"
