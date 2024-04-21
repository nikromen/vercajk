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


MONITOR_LETTERS=("a" "b" "c" "d" "e" "f")


refresh() {
    local workspaces=$(hyprctl -j workspaces)
    local monitors=$(hyprctl -j monitors | jq -r '.[].name')
    local monitor_count=0
    for monitor in $monitors; do
        local monitor_workspaces=$(echo $workspaces | jq -r ".[] | select(.monitor == \"$monitor\") | .id" | sort)
        local i=1
        for workspace_id in $monitor_workspaces; do
            hyprctl dispatch renameworkspace $workspace_id $i${MONITOR_LETTERS[$monitor_count]}
            i=$((i + 1))
        done
        monitor_count=$((monitor_count + 1))
    done
}

_prep() {
    WORKSPACE_NUMBER=$2
    ACTIVE_MONITOR_NAME=$(hyprctl -j monitors | jq -r ".[] | select(.focused == true) | .name")
    ACTIVE_WORKSPACE=$(hyprctl -j activeworkspace | jq -r '.name')
    MONITOR_LETTER=$(echo $ACTIVE_WORKSPACE | sed 's/.*\([a-z]\)$/\1/')
    NEW_WORKSPACE_NAME=$WORKSPACE_NUMBER$MONITOR_LETTER
    WORKSPACE_ID=$(hyprctl -j workspaces | jq -r ".[] | select(.monitor == \"$ACTIVE_MONITOR_NAME\" and .name == \"$NEW_WORKSPACE_NAME\") | .id")
}

new() {
    _prep $@

    if [ -n "$WORKSPACE_ID" ]; then
        hyprctl dispatch workspace $WORKSPACE_ID
        echo "ahoj"
        exit 0
    fi

    hyprctl dispatch workspace empty
    local new_workspace_id=$(hyprctl -j activeworkspace | jq -r '.id')
    hyprctl dispatch renameworkspace $new_workspace_id $NEW_WORKSPACE_NAME
    echo $new_workspace_id
}

move() {
    _prep $@
    if [ -z "$WORKSPACE_ID" ]; then
        local last_workspace_id=$(hyprctl -j workspaces | jq -r ".[] | select(.monitor == \"$ACTIVE_MONITOR_NAME\") | .id" | sort | tail -n 1)
        id=$((last_workspace_id + 1))
    else
        id=$WORKSPACE_ID
    fi

    hyprctl dispatch movetoworkspace $id
    if [ -z "$WORKSPACE_ID" ]; then
        $HOME/.config/hypr/scripts/workspaces.sh -r
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
