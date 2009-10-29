### $Id: trustedroot.py 15186 2009-09-30 23:20:21Z bakers $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/trust/trustedroot.py $

import os

from sfa.trust.gid import *

class TrustedRootList:
    def __init__(self, dir):
        self.basedir = dir
        
        # create the directory to hold the files
        try:
            os.makedirs(self.basedir)
        # if the path already exists then pass
        except OSError, (errno, strerr):
            if errno == 17:
                pass

    def add_gid(self, gid):
        fn = os.path.join(self.basedir, gid.get_hrn() + ".gid")

        gid.save_to_file(fn)

    def get_list(self):
        gid_list = []

        file_list = os.listdir(self.basedir)
        for gid_file in file_list:
            fn = os.path.join(self.basedir, gid_file)
            if os.path.isfile(fn):
                gid = GID(filename = fn)
                gid_list.append(gid)

        return gid_list

