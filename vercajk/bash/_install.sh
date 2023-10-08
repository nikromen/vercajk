#!/bin/bash


set -e

bash_dir=$HOME/.config/bash
mkdir -p $bash_dir
rsync * $bash_dir --exclude=_install.sh

# add new line to the end of file if not present
if ! [[ -s "$HOME/.bashrc" && -z "$(tail -c 1 "$HOME/.bashrc")" ]]; then
    echo "" >> "$HOME/.bashrc"
fi

if ! grep -q "\$HOME/.config/bash/custom_bash_profile_merged" $HOME/.bashrc; then
    echo "
if [ -e \$HOME/.config/bash/custom_bash_profile_merged ]; then
    source \$HOME/.config/bash/custom_bash_profile_merged
fi" >> $HOME/.bashrc
fi

install -p -m 0755 ./scripts/* $HOME/.local/bin
