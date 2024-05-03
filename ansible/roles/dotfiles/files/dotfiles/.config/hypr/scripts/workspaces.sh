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
    echo "New workspace name: $NEW_WORKSPACE_NAME"
    WORKSPACES=$(hyprctl -j workspaces)
    WORKSPACE_ID=$(echo "$WORKSPACES" | jq -r ".[] | select(.name == \"$NEW_WORKSPACE_NAME\" and .monitorID == $ACTIVE_MONITOR_ID) | .id")
}

new() {
    _prep $@

    # go to existing workspace
    if [ -n "$WORKSPACE_ID" ]; then
        hyprctl dispatch workspace $WORKSPACE_ID
        exit 0
    fi

    hyprctl dispatch workspace empty
    local new_workspace_id=$(hyprctl -j activeworkspace | jq -r '.id')
    hyprctl dispatch renameworkspace $new_workspace_id $NEW_WORKSPACE_NAME
}

move() {
    _prep $@

    if [ -z "$WORKSPACE_ID" ]; then
        # move to new workspace
        local last_workspace_id=$(echo $WORKSPACES | jq -r ".[] | select(.monitorID == $ACTIVE_MONITOR_ID) | .id" | sort -r -t _ -g | head -n 1)
        id=$((last_workspace_id + 1))
    else
        id=$WORKSPACE_ID
    fi

    hyprctl dispatch movetoworkspace $id
    if [ -z "$WORKSPACE_ID" ]; then
        hyprctl dispatch renameworkspace $id $NEW_WORKSPACE_NAME
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
