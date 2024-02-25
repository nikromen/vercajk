#!/bin/bash


set -e

usage() {
    echo "Usage: $0 [COMMAND]

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
    local icon_path="$HOME/.config/swaync/icons/brightness"
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

case $1 in
    up)
        brightnessctl set +5%
        _notify
        ;;
    down)
        brightnessctl set 5%-
        _notify
        ;;
    get)
        get
        ;;
    *)
        usage
        exit 1
        ;;
esac
