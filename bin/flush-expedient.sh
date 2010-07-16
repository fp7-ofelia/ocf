#!/bin/bash

source expedient-settings
 
cd $EXPEDIENT/src/python
rm -f $EXPEDIENT/db/$CH/clearinghouse.db
python $CH/manage.py syncdb --noinput
python $CH/manage.py runscript create-superuser

