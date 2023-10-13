#!/bin/bash


killall conky >> /dev/null 2>&1
conky -d -p 10 -c "$HOME/.config/conky/default.conkyrc" >> /dev/null 2>&1
