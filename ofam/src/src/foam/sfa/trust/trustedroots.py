import os.path
import glob

from foam.sfa.trust.gid import GID
#from foam.sfa.util.foam.sfa.ogging import logger

class TrustedRoots:
    
    # we want to avoid reading all files in the directory
    # this is because it's common to have backups of all kinds
    # e.g. *~, *.hide, *-00, *.bak and the like
    supported_extensions= [ 'gid', 'cert', 'pem' ]

    def __init__(self, dir):
        self.basedir = dir
        # create the directory to hold the files, if not existing
        if not os.path.isdir (self.basedir):
            os.makedirs(self.basedir)

    def add_gid(self, gid):
        fn = os.path.join(self.basedir, gid.get_hrn() + ".gid")
        gid.save_to_file(fn)

    def get_list(self):
        print 'self.get_file_list():',self.get_file_list()
        gid_list = [GID(filename=cert_file) for cert_file in self.get_file_list()]
        return gid_list

    def get_file_list(self):
        file_list  = []
        pattern=os.path.join(self.basedir,"*")
        for cert_file in glob.glob(pattern):
            if os.path.isfile(cert_file):
                if self.has_supported_extension(cert_file):
                    file_list.append(cert_file) 
                else:
                    print "File %s ignored - supported extensions are %r"%\
                                       (cert_file,TrustedRoots.supported_extensions)
        return file_list

    def has_supported_extension (self,path):
        (_,ext)=os.path.splitext(path)
        ext=ext.replace('.','').lower()
        return ext in TrustedRoots.supported_extensions
