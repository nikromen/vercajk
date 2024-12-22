#!/bin/bash


set -e

usage() {
    echo "Usage: $0 [OPTIONS]
    -h, --help      Display this help and exit
    -j, --json      Output in JSON format"
}


main() {
    output=$(sensors | grep fan | awk '{print $2}')
    for number in $output; do
        total=$((total + number))
        count=$((count + 1))
    done

    avg=$((total / count))
    echo "${avg}"
}


json=false
case "$1" in
    -h|--help)
        usage
        exit 0
        ;;
    -j|--json)
        json=true
        ;;
    *)
        usage
        exit 1
        ;;
esac

result=$(main)

if [ "$json" = true ]; then
    echo "{\"text\": \"${result}\"}"
else
    echo "${result}"
fi
