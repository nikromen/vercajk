#!/bin/sh


__fail() {
    mv ../del.sh ./
    exit 1
}


remove_mock_logs() {
    preserve_rpm=false
    preserve_srpm=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --preserve_rpm | -r)
                preserve_rpm=true
                ;;
            --preserve_srpm | -s)
                preserve_srpm=true
                ;;
            *)
                exit 1
                ;;
        esac
        shift
    done

    if [ "$preserve_rpm" = true ]; then
        find . ! -name "*.rpm" -type f -exec rm -r {} +
        exit 0
    fi

    if [ "$preserve_srpm" = true ]; then
        find . ! -name "*.srpm" -type f -exec -r {} +
        exit 0
    fi

    rm -r *
}

[ "$PWD" == "$HOME/Documents/mock_results/" ] || __fail "Not currencly in mock resultdir, aborting"

mv ./del.sh ..
remove_mock_logs "$@" || __fail
mv ../del.sh ./
