#!/bin/bash


set -e

startup_dir=$HOME/.config/startup-scripts
mkdir -p $startup_dir
rsync * $startup_dir --exclude=_install.sh
