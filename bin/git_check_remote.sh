#!/bin/bash

git pull | grep "Already up-to-date"
if [ $? == 0 ]; then
    exit 0
fi
echo "There are remote changes which need to get merged and tested!"
exit 1