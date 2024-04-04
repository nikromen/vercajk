#!/bin/bash


set -e


usage() {
    echo "Usage: $0 [OPTIONS] [ARGS]
    
    Options:
        -h, --help      Display this message.
        -n, --new       Create a new workspace.
        -m, --move      Move to an existing workspace.
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
ACTIVE_WORKSPACE=$(hyprctl -j activeworkspace | jq -r '.name')
MONITOR_LETTER=$(echo $ACTIVE_WORKSPACE | sed 's/.*\([a-z]\)$/\1/')
NEW_WORKSPACE_NAME="${WORKSPACE_NUMBER}${MONITOR_LETTER}"
WORKSPACE_EXISTS=$(hyprctl -j workspaces | jq -r ".[] | select(.name == \"$NEW_WORKSPACE_NAME\") | .name")

new() {
    if [ -n "$WORKSPACE_EXISTS" ]; then
        hyprctl dispatch workspace $NEW_WORKSPACE_NAME
        exit 0
    fi

    hyprctl dispatch workspace empty
    local id=$(hyprctl -j activeworkspace | jq -r '.id')
    hyprctl dispatch renameworkspace $id $NEW_WORKSPACE_NAME
}

move() {
    if [ -z "$WORKSPACE_EXISTS" ]; then
        echo dva
        new
    fi

    hyprctl dispatch workspace $ACTIVE_WORKSPACE
    hyprctl dispatch movetoworkspace $NEW_WORKSPACE_NAME
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
    *)
        usage
        exit 1
        ;;
esac
