#!/bin/bash

source expedient-settings
 
cd $EXPEDIENT/src/python
python $CH/manage.py syncdb --noinput
python $CH/manage.py flush --noinput
python $CH/manage.py runscript create-superuser

