#!/bin/bash


set -e

get_remote() {
    case "$1" in
        "o")
            echo "origin"
            ;;
        "u")
            echo "upstream"
            ;;
        *)
            echo "$1"
            ;;
    esac
}
