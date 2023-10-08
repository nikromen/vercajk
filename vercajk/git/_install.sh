#!/bin/bash


set -e

cp -f .gitconfig $HOME
mkdir -p $HOME/.config/git
cp -f .gitignore $HOME/.config/git
