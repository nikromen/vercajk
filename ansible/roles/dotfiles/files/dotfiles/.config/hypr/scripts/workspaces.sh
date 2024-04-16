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

if [ -z "$2" ]; then
    echo "Error: Missing workspace number."
    exit 1
fi

WORKSPACE_NUMBER=$2
ACTIVE_MONITOR_NAME=$(hyprctl -j monitors | jq -r ".[] | select(.focused == true) | .name")
EXISTING_WORKSPACE_ID=$(hyprctl -j workspaces | jq -r ".[] | select(.monitor == \"$ACTIVE_MONITOR_NAME\" and .name == \"$WORKSPACE_NUMBER\") | .id")


new() {
    if [ -n "$EXISTING_WORKSPACE_ID" ]; then
        hyprctl dispatch workspace $EXISTING_WORKSPACE_ID
        exit 0
    fi

    hyprctl dispatch workspace empty
    local id=$(hyprctl -j activeworkspace | jq -r '.id')
    hyprctl dispatch renameworkspace $id $WORKSPACE_NUMBER
    echo $id
}

move() {
    local id=
    local active_window=
    local active_workspace=$(hyprctl -j activeworkspace | jq -r ".id")
    if [ -z "$EXISTING_WORKSPACE_ID" ]; then
        active_window=$(hyprctl -j activewindow | jq -r ".address")
        id=$(new)
    else
        id=$EXISTING_WORKSPACE_ID
    fi

    if [ -n "$active_window" ]; then
        hyprctl dispatch movetoworkspace $active_workspace,$active_window
    else
        hyprctl dispatch workspace $active_workspace
        hyprctl dispatch movetoworkspace $id
    fi
}


case $1 in
    -h|--help)
        usage
        exit 0
        ;;
    -n|--new)
        new
        ;;
    -m|--move)
        move
        ;;
    -r|--refresh)
        refresh
        ;;
    *)
        usage
        exit 1
        ;;
esac
