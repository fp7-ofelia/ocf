#!/bin/bash

#----------------------------------------------------------------------
# Copyright (c) 2012 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------


if [ $# != 2 ] 
then
    echo "Usage: deletesliver pathToHomeDir pathToSliceSpecificScriptsDir"
    exit 1
fi

# Stop the PCs
echo "Stopping running containers..."
vzctl stop 101
vzctl stop 102
vzctl stop 103
vzctl stop 104
vzctl stop 105
vzctl stop 106

# Destroy containers
echo "Destroying containers..."
vzctl destroy 101
vzctl destroy 102
vzctl destroy 103
vzctl destroy 104
vzctl destroy 105
vzctl destroy 106

# Disable and delete bridges 
echo "Disabling and deleting bridges..."
for i in $(brctl show | awk '{print $1}')
    do
    if  [ $i != "bridge" ]
    then
        echo "Disabling and deleting bridge $i..."
        /sbin/ifconfig $i down
        /usr/sbin/brctl delbr $i
    fi
done

echo "Cleaning up files created for sliver"
rm -f $1/.ssh/known_hosts

# Delete the files that hold the sliver status
rm -f $2/*.status

exit 0
