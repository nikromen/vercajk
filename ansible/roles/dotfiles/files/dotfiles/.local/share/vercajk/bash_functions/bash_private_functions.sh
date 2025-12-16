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
        "")
            echo ""
            ;;
        *)
            echo "$1"
            ;;
    esac
}


get_default_main_branch() {
    git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
}
