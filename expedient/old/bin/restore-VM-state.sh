#!/bin/bash
#
# restore the OM, CH, and FV databases and settings
#
# Author: Jad Naous <jnaous@stanford.edu>
#

tar -zxf $1 --wildcard --no-anchored "$2"
