#!/bin/bash

TMP=`mktemp /tmp/build_prdictapi.XXXXXXXX`
trap "rm -f $TMP; exit 1" 2 3 15
git log | head -1 | awk '{print $2}' > $TMP
if [ ! -f $1 ]; then
  mv $TMP $1
else
  if ! diff $TMP $1 > /dev/null; then
    mv $TMP $1
  fi
fi
rm -f $TMP
