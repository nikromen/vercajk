#!/bin/bash


# Change the wallpaper every X seconds, each iteration order is random

if [[ $# -lt 2 ]]; then
	echo "Usage:
    $0 DIRECTORY TIME
    DIRECTORY Directory with the wallpapers
    TIME      Time in seconds to change the wallpaper
    Optional:
    FPS       Transition FPS (default 60)
    "
    exit 1
fi

DIRECTORY=$1
INTERVAL=$2
FPS=${3:-60}

if [[ ! -d $DIRECTORY ]]; then
    echo "Directory not found: $DIRECTORY"
    exit 1
fi

if [[ ! $INTERVAL =~ ^[0-9]+$ ]]; then
    echo "Invalid interval: $INTERVAL"
    exit 1
fi

if [[ ! $FPS =~ ^[0-9]+$ ]]; then
    echo "Invalid FPS: $FPS"
    exit 1
fi

export SWWW_TRANSITION_FPS=$FPS
export SWWW_TRANSITION_STEP=2

while true; do
    images=($DIRECTORY/*)
    shuffled=($(shuf -e "${images[@]}"))
    for image in "${shuffled[@]}"; do
        swww img "$image"
        sleep $INTERVAL
    done
done
