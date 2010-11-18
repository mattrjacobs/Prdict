#!/bin/bash

git status | egrep "Untracked|modified|deleted|new file"
if [ $? == 0 ]; then
    echo "There are local changes which need to get committed!"
    exit 1
fi

git status | grep "Your branch is ahead"
if [ $? == 0 ]; then
    echo "There are local repo commits which need to get pushed!"
    exit 1
fi
exit 0