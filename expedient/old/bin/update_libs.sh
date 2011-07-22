#!/bin/bash

source expedient-settings

# Skip lines that begin with a #
lib_lines=`grep -e "^[^#]" $EXPEDIENT/dist/python-deps`
for line in $lib_lines; do
	libs="$libs $line"
done

easy_install -U -s $EXPEDIENT/bin -d $EXPEDIENT/lib/python $libs
