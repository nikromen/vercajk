#!/bin/bash


set -e


usage() {
    echo "Usage: $0 [OPTIONS] [ARGS]
    
    Options:
        -h, --help      Display this message.
        -n, --new       Create a new workspace.
        -m, --move      Move to an existing workspace.
        -r, --refresh   Refresh the workspaces with monitors.
    "
}

if [ -z "$1" ]; then
    usage
    exit 1
fi


refresh() {
    local workspaces=$(hyprctl -j workspaces)
    local monitors=$(hyprctl -j monitors | jq -r ".[].id")

    local is_zero_monitor=false
    if [[ $monitors == *"0"* ]]; then
        is_zero_monitor=true
    fi

    for monitorID in $monitors; do
        local monitor_workspacesID=$(echo $workspaces | jq -r ".[] | select(.monitorID == $monitorID and (.name | startswith(\"special:\") | not)) | .id" | sort)
        local i=1

        if ! $is_zero_monitor; then
            monitorID=$((monitorID - 1))
        fi

        for workspace_id in $monitor_workspacesID; do
            if [[ $monitorID -eq 0 ]]; then
                monitorID=""
            fi

            hyprctl dispatch renameworkspace $workspace_id ${monitorID}${i}
            i=$((i + 1))
        done
    done
}

_prep() {
    local monitors=$(hyprctl -j monitors)
    ACTIVE_MONITOR_ID=$(echo $monitors | jq -r ".[] | select(.focused == true) | .id")
    local monitors_ids=$(echo $monitors | jq -r ".[].id")
    local shifted_monitor_id=$ACTIVE_MONITOR_ID
    if [[ $monitors_ids != *"0"* ]]; then
        shifted_monitor_id=$((ACTIVE_MONITOR_ID - 1))
    fi

    if [[ $shifted_monitor_id -eq 0 ]]; then
        shifted_monitor_id=""
    fi

    local workspace_number=$2
    NEW_WORKSPACE_NAME="${shifted_monitor_id}${workspace_number}"
    WORKSPACES=$(hyprctl -j workspaces)
    WORKSPACE_ID=$(echo "$WORKSPACES" | jq -r ".[] | select(.name == \"$NEW_WORKSPACE_NAME\" and .monitorID == $ACTIVE_MONITOR_ID) | .id")
}

_properly_rename_new_workspace() {
    local new_workspace_id=$(hyprctl -j activeworkspace | jq -r ".id")
    hyprctl dispatch renameworkspace $new_workspace_id $NEW_WORKSPACE_NAME
}

_calculate_r_to_empty_worspace() {
    local last_workspace_id=$(echo $WORKSPACES | jq -r ".[] | select(.id >= 0 and .monitorID == $ACTIVE_MONITOR_ID) | .id" | sort -n | tail -n 1)
    local active_workspace_id=$(hyprctl -j activeworkspace | jq -r ".id")
    if [ $last_workspace_id -ge $active_workspace_id ]; then
        echo $(($last_workspace_id - $active_workspace_id + 1))
    else
        echo $(($active_workspace_id + $last_workspace_id + 1))
    fi
}

new() {
    _prep $@
    # go to existing workspace
    if [ -n "$WORKSPACE_ID" ]; then
        hyprctl dispatch workspace $WORKSPACE_ID
        exit 0
    fi

    echo "dispatch workspace r+$(_calculate_r_to_empty_worspace)"
    hyprctl dispatch workspace r+$(_calculate_r_to_empty_worspace)
    _properly_rename_new_workspace
}

move() {
    _prep $@

    if [ -z "$WORKSPACE_ID" ]; then
        hyprctl dispatch movetoworkspace r+$(_calculate_r_to_empty_worspace)
        _properly_rename_new_workspace
    else
        hyprctl dispatch movetoworkspace $WORKSPACE_ID
    fi
}


check() {
    if [ -z "$2" ]; then
        echo "Error: Missing workspace number."
        exit 1
    fi
}


case $1 in
    -h|--help)
        usage
        exit 0
        ;;
    -n|--new)
        check $@
        new $@
        ;;
    -m|--move)
        check $@
        move $@
        ;;
    -r|--refresh)
        refresh
        ;;
    *)
        usage
        exit 1
        ;;
esac
