#!/bin/bash


set -e

fish_dir=$HOME/.config/fish
mkdir -p $fish_dir/functions
mkdir -p $fish_dir/conf.d
cp -f config.fish $fish_dir
cp -f custom_functions.fish $fish_dir/functions
cp -f custom_interactive_functions.fish $fish_dir/functions
cp -f aliases $fish_dir/conf.d

python3 generate_from_bash.py variables
cp -f variables $fish_dir/conf.d
rm variables

python3 generate_from_bash.py scripts
cp -f call_in_bash_scripts.fish $fish_dir/functions
rm call_in_bash_scripts.fish
