#!/bin/bash
# This script is used to print the custom addons path.
# Copyright (C) 2021 Mihran Thalhath (https://github.com/mihranthalhath)

addons=""
flag=0
for dir in *; do
    if [ -d "$dir" ]; then
        cd $dir
        present=$(pwd)
        if [ "$flag" = 0 ]; then
            flag=1
            addons="${present}"
        else
            addons="${addons},\n${present}"
        fi
        cd ..
    fi
done
echo "$addons"
