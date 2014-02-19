#!/bin/bash

omni_path="/opt/gcf-2.0/src/omni.py"

python $omni_path -o -a https://localhost:8003 -V 3 --debug allocate "some-slice" request.xml
