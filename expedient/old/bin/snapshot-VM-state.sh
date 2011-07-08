#!/bin/bash
#
# Store the OM, CH, and FV databases and settings
#
# Author: Jad Naous <jnaous@stanford.edu>
#
source expedient-settings

FILES="$EXPEDIENT/bin/expedient-settings \
$EXPEDIENT/db/$CH/clearinghouse.db \
$EXPEDIENT/db/$OM/om.db \
$FLOWVISOR/$FV_CONFIG \
$FLOWVISOR/mySSLKeyStore \
"

ver=`date +%F-%T`

mkdir -p $SNAPSHOT_DIR
tar -Pzcf $SNAPSHOT_DIR/$1-expedient-snapshot-$ver.tar.gz $FILES

echo "Created archive: $SNAPSHOT_DIR/expedient-snapshot-$ver.tar.gz"
