#!/bin/bash

source expedient-settings

echo ------------------------------------------
echo -         Running GAPI Tests             -
echo ------------------------------------------
python $EXPEDIENT/src/python/openflow/tests/gapi/gapi.py

echo ------------------------------------------
echo -          Running OM Tests              -
echo ------------------------------------------
python $EXPEDIENT/src/python/openflow/tests/om/om.py

echo ------------------------------------------
echo -     Running Integration Tests          -
echo ------------------------------------------
python $EXPEDIENT/src/python/openflow/tests/full/fulltests.py
