#!/bin/bash

usage() {
    echo "Usage: $0 [OPTIONS]
    -h | --help:  Display this help message
    -r | --right: Move current workspace to the monitor on the right
    -l | --left:  Move current workspace to the monitor on the left
    "
}

move() {
    local direction=$1
    local monitors=$(hyprctl -j monitors)
    local sorted_monitors=$(echo "$monitors" | jq -r '. | sort_by(.x)[] | .id')
    local current_monitor_id=$(echo "$monitors" | jq -r '.[] | select(.focused) | .id')

    local next_monitor_id
    if [ "$direction" == "right" ]; then
        next_monitor_id=$(echo "$sorted_monitors" | grep -A1 "$current_monitor_id" | tail -n1)
    else
        next_monitor_id=$(echo "$sorted_monitors" | grep -B1 "$current_monitor_id" | head -n1)
    fi

    if [ "$next_monitor_id" == "$current_monitor_id" ]; then
        notify-send -a "Hyprland" -i "error" -c "error" "No monitor to move to."
        exit 1
    fi

    local current_worspace=$(echo "$monitors" | jq -r ".[] | select(.id == $current_monitor_id) | .activeWorkspace")
    local current_workspace_id=$(echo "$current_worspace" | jq -r ".id")
    local current_workspace_name_position=$(echo "$current_worspace" | jq -r ".name" | cut -d ":" -f2)

    local next_workspace=$(echo "$monitors" | jq -r ".[] | select(.id == $next_monitor_id) | .activeWorkspace")
    local next_workspace_id=$(echo "$next_workspace" | jq -r ".id")
    local next_workspace_name_position=$(echo "$next_workspace" | jq -r ".name" | cut -d ":" -f2)

    local active_window_address=$(hyprctl -j activewindow | jq -r ".address")

    # do not touch, this is efficient
    hyprctl --batch "dispatch renameworkspace $current_workspace_id $next_monitor_id:$next_workspace_name_position; dispatch renameworkspace $next_workspace_id $current_monitor_id:$current_workspace_name_position; dispatch focusworkspaceoncurrentmonitor $next_workspace_id"
}

main() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -r|--right)
                move "right"
                ;;
            -l|--left)
                move "left"
                ;;
            *)
                usage
                exit 1
                ;;
        esac
        shift
    done
}

main "$@"
