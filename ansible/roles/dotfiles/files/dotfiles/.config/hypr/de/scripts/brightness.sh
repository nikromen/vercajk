#!/bin/bash


set -e

usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]
    Options:
        -h | --help     Show this message.
        -n | --notify   Send a notification after changing the brightness.

    Commands:
        up      Increase the brightness.
        down    Decrease the brightness.
        get     Get the current brightness."
}

if [ -z "$1" ]; then
    usage
    exit 1
fi

get() {
    echo $(brightnessctl -m | cut -d, -f4 | sed 's/%$//')
}

_icon() {
    local brightness=$1
    local icon_path="$WM_ICONS/brightness"
    if [ $brightness -lt 20 ]; then
        echo "$icon_path/20.png"
    elif [ $brightness -lt 40 ]; then
        echo "$icon_path/40.png"
    elif [ $brightness -lt 60 ]; then
        echo "$icon_path/60.png"
    elif [ $brightness -lt 80 ]; then
        echo "$icon_path/80.png"
    else
        echo "$icon_path/100.png"
    fi
}

_notify() {
    local brightness=$(get)
    notify-send -e -h string:x-canonical-private-synchronous:brightness_notify -h int:value:$brightness -u low -i "$(_icon $brightness)" "$brightness%"
}

notify=false
while [ "$1" != "" ]; do
    case $1 in
        -h | --help)
            usage
            exit 0
            ;;
        -n | --notify)
            notify=true
            ;;
        *)
            break
            ;;
    esac
    shift
done

case $1 in
    up)
        brightnessctl set +5%
        ;;
    down)
        brightnessctl set 5%-
        ;;
    get)
        get
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    -n | --notify)
        notify=true
        shift
        ;;
    *)
        usage
        exit 1
        ;;
esac

if [ "$notify" = true ]; then
    _notify
fi
