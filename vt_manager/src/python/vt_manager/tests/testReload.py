#!/usr/bin/python
import sys,os
sys.path.append("/opt/ofelia/vt_manager/src/python/vt_manager")
import vt_manager.models

for i in range(0,100):
    for mod in sys.modules:
        if mod.startswith('vt_manager.models'):
            #print mod
            del mod

    import vt_manager.models 
