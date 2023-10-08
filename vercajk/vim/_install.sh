#!/bin/bash


set -e

cp -f .vimrc $HOME
vim $HOME/.vimrc -c PlugInstall -c wqa
