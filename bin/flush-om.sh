#!/bin/bash

source expedient-settings
 
cd $EXPEDIENT/src/python
python $OM/manage.py syncdb --noinput
python $OM/manage.py flush --noinput
python $OM/manage.py runscript create-superuser

