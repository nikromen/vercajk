#!/bin/bash


set -e

conky_dir=$HOME/.config/conky
mkdir -p $conky_dir
cp -f * $conky_dir
