#!/bin/bash

FILES=`find . -name "*.py" `
tmp=tmp_file
for file in $FILES
do
	#sed $file 's/from\ openflow\.optin_manager/from\ openflow\.vt_manager'
	#cat $file > $tmp	
	#cat $tmp | sed 's/from\ openflow\.vt_manager/from\ vt_manager/' > $file
	#cat $file > $tmp	
        #cat $tmp | sed 's/openflow\.vt_manager/vt_manager/' > $file
	#cat $file > $tmp	
        #cat $tmp | sed 's/openflow\/vt_manager/vt_manager/' > $file
	cat $file > $tmp
        cat $tmp | sed 's/expedient\.common/common/' > $file

done
rm $tmp
