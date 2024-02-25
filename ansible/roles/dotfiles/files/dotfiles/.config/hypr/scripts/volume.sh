#!/bin/bash


set -e

usage() {
    echo "Usage: $0 [COMMAND]

    Commands:
        up      Increase the volume.
        down    Decrease the volume.
        get     Get the current volume.
        mute    Mute the volume."
}

if [ -z "$1" ]; then
    usage
    exit 1
fi

get() {
    local volume=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | cut -d " " -f2)
    local result=$(echo "scale=0; $volume * 100 / 1" | bc)
    echo $result
}

_icon() {
    local volume=$1
    local icon_path="$HOME/.config/swaync/icons/volume"
    if [ $volume == 0 ]; then
        echo "$icon_path/mute.png"
    elif [ $volume -lt 30 ]; then
        echo "$icon_path/low.png"
    elif [ $volume -lt 60 ]; then
        echo "$icon_path/mid.png"
    else
        echo "$icon_path/high.png"
    fi
}

_notify() {
    local volume=$(get)
    notify-send -e -h string:x-canonical-private-synchronous:volume_notify -h int:value:$volume -u low -i "$(_icon $volume)" "$volume%"

    if [ $volume != 0 ]; then
        pw-cat --playback $HOME/.config/hypr/stereo/bell.oga
    fi
}

_ummute_if_needed() {
    if [ "$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -o "MUTED")" ]; then
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
    fi
}

case $1 in
    up)
        _ummute_if_needed
        wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ 5%+
        _notify
        ;;
    down)
        _ummute_if_needed
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
        _notify
        ;;
    get)
        get
        ;;
    mute)
        if [ "$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -o "MUTED")" ]; then
            _notify
        else
            notify-send -e -h string:x-canonical-private-synchronous:volume_notify -u low -i "$(_icon 0)" "Muted"
        fi
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        ;;
    *)
        usage
        exit 1
        ;;
esac
