#!/bin/bash

# list all screen sessions and filter only those whose name starts with "build"
screens=$(screen -ls | grep "^\\s*[0-9]\\+.build" | awk '{print $1}')

# iterate over the list of screens and kill each one
for screen in $screens
do
    screen -X -S $screen quit
done