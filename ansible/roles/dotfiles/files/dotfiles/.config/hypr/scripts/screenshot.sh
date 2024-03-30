#!/bin/bash


# TODO: this will hopefully be deprecated by flameshot


set -e

usage() {
    echo "Usage: $0 [OPTIONS] MODE
    Options:
        -h, --help         Show this help message and exit
        -f, --folder       Folder to save screenshots
        -c, --clipboard    Copy screenshot to clipboard
    
    Modes:
        full              Take a screenshot of the entire screen
        area              Take a screenshot of an area
        window            Take a screenshot of window you select
        workspace         Take a screenshot of active workspace
    "
}


__fail() {
    echo "$*" >&2
    exit 1
}


notify() {
    msg="Screenshot saved to $1"
    if [ "$CLIPBOARD" = true ]; then
        msg="$msg and copied to clipboard"
    fi
    notify-send -t 5000 "$msg"
}


parse_args() {
    while [ "$1" != "" ]; do
        case $1 in
            -h | --help)
                usage
                exit 0
                ;;
            -f | --folder)
                FOLDER=$1
                ;;
            -c | --clipboard)
                CLIPBOARD="true"
                ;;
            full | area | window | workspace)
                MODE=$1
                ;;
            *)
                __fail "Invalid argument: $1"
                ;;
        esac
        shift
    done
}


get_active_workspace_pos() {
    local active_workspace=$(hyprctl -j activeworkspace)
    local monitors=$(hyprctl -j monitors)
    local current_monitor="$(echo $monitors | jq -r 'first(.[] | select(.activeWorkspace.id == '$(echo $active_workspace | jq -r '.id')'))')"
    echo $current_monitor | jq -r '"\(.x),\(.y) \(.width/.scale|round)x\(.height/.scale|round)"'
}


get_windows_pos() {
    local monitors=`hyprctl -j monitors`
    local clients=`hyprctl -j clients | jq -r '[.[] | select(.workspace.id | contains('$(echo $monitors | jq -r 'map(.activeWorkspace.id) | join(",")')'))]'`
    local boxes="$(echo $clients | jq -r '.[] | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1]) \(.title)"')"
    slurp -r <<< "$boxes"
}


screenshot() {
    local filename="$(date +%Y-%m-%d-%H-%M-%S)_screenshot.png"
    local filepath="$FOLDER/$filename"
    case $MODE in
        full)
            grim $filepath
            ;;
        area)
            grim -g "$(slurp -d)" $filepath
            ;;
        workspace)
            grim -g "$(get_active_workspace_pos)" $filepath
            ;;
        window)
            grim -g "$(get_windows_pos)" $filepath
            ;;
        *)
            __fail "Invalid mode: $MODE"
            ;;
    esac

    if [ "$CLIPBOARD" = true ] && [ -f "$filepath" ]; then
        wl-copy < $filepath
    fi
    notify $filepath
}


FOLDER="$HOME/Pictures/Screenshots"
MODE="full"
CLIPBOARD="false"

parse_args "$@"
screenshot
