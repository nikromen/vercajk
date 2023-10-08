#!/bin/bash


set -e

profile_name="the-best-kde-profile"
konsave -r $profile_name
konsave -i ./$profile_name.knsv
konsave -a $profile_name
