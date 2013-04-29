import os
from django.conf import settings

class MetaSfaRegistry:
  
    sfa_gid_location = '/sfa/trusted_roots/ocf_of.gid'

    def __init__(self, config=None):
        self.gid = settings.CONF_DIR + self.sfa_gid_location

    def get_trusted_certs(self,cert=None):
        f = open(self.gid,'r')
        gid = f.read()
        f.close()
        return [gid]
