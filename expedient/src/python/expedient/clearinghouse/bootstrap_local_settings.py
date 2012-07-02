#!/usr/bin/python
'''Script to create a skeleton localsettings.py file.
Created on Sep 25, 2010

@author: jnaous
'''

import sys
import os
from expedient.clearinghouse.commands.utils import bootstrap_local_settings
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

def usage():
    print "%s <conf_dir>" % sys.argv[0]
    print "    <conf_dir> is the location where you want to create a"
    print "    skeleton localsettings.py file."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Wrong number of arguments."
        usage()
        
    if not os.path.isdir(sys.argv[1]) or not os.access(sys.argv[1], os.W_OK):
        print "Cannot access path %s" % sys.argv[1]
        usage()
        
    conf_dir = sys.argv[1]
    
    bootstrap_local_settings(conf_dir=conf_dir)
    
