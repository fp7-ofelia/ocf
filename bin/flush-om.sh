#!/bin/bash

source expedient-settings
 
cd $EXPEDIENT/src/python
rm -f $EXPEDIENT/db/$OM/om.db
python $OM/manage.py syncdb --noinput
python $OM/manage.py runscript create-superuser

