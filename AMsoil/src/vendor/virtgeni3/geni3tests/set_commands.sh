#!/bin/bash

slicename="slice-name"
omni_path="/opt/gcf-2.0/src/omni.py"

python $omni_path -o -a https://localhost:8003 -V 3 --debug getversion
python $omni_path -o -a https://localhost:8003 -V 3 --debug --no-compress listresources
python $omni_path -o -a https://localhost:8003 -V 3 --debug describe $slicename
python $omni_path -o -a https://localhost:8003 -V 3 --debug allocate $slicename request.xml 
# OR python $omni_path -o -a https://localhost:8003 -V 3 --debug --end-time=2014-04-12T23:20:50.52Z allocate $slicename rspec-req.xml
python $omni_path -o -a https://localhost:8003 -V 3 --debug renew $slicename 2013-02-07T15:00:50.52Z
python $omni_path -o -a https://localhost:8003 -V 3 --debug provision $slicename
# OR python $omni_path -o -a https://localhost:8003 -V 3 --debug --end-time=2014-04-12T23:20:50.52Z provision $slicename
python $omni_path -o -a https://localhost:8003 -V 3 --debug status $slicename
python $omni_path -o -a https://localhost:8003 -V 3 --debug performoperationalaction $slicename geni_start
# OR python $omni_path -o -a https://localhost:8003 -V 3 --debug performoperationalaction $slicename geni_stop
# OR python $omni_path -o -a https://localhost:8003 -V 3 --debug performoperationalaction $slicename geni_restart
python $omni_path -o -a https://localhost:8003 -V 3 --debug delete $slicename
python $omni_path -o -a https://localhost:8003 -V 3 --debug shutdown $slicename
