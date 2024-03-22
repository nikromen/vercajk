#!/bin/bash

song_name=$(playerctl metadata --format "{{title}} | {{artist}}")
if [ -n "$song_name" ]; then
    echo "    $song_name"
fi
