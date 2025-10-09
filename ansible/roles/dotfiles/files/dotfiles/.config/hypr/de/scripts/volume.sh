#!/bin/bash


set -e

usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]
    Options:
        -h | --help     Show this message.
        -n | --notify   Send a notification after changing the volume.

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
    local icon_path="$WM_ICONS/volume"
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
        pw-cat --playback $WM_AUDIO/bell.oga
    fi
}

_ummute_if_needed() {
    if [ "$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -o "MUTED")" ]; then
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
    fi
}


notify=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h | --help)
            usage
            exit 0
            ;;
        -n | --notify)
            notify=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

case $1 in
    up)
        _ummute_if_needed
        wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ 5%+
        if [ "$notify" = true ]; then
            _notify
        fi
        ;;
    down)
        _ummute_if_needed
        wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
        if [ "$notify" = true ]; then
            _notify
        fi
        ;;
    get)
        get
        ;;
    mute)
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        if [ "$notify" = true ]; then
            if [ "$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -o "MUTED")" ]; then
                _notify
            else
                notify-send -e -h string:x-canonical-private-synchronous:volume_notify -u low -i "$(_icon 0)" "Muted"
            fi
        fi
        ;;
    *)
        usage
        exit 1
        ;;
esac
