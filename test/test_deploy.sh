#!/bin/bash


set -e


fail() {
    podman rmi -f $img_name
    exit 1
}


img_name="vercajk-test:latest"
podman build -t $img_name -f Containerfile ..
podman run $img_name /bin/bash -ci "make; vercajk update" || fail
podman rmi -f $img_name
