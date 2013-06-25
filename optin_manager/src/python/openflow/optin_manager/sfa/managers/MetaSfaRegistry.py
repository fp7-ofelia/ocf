import os
from django.conf import settings

from openflow.optin_manager.sfa.trust.gid import GID
from openflow.optin_manager.sfa.trust.credential import Credential
from openflow.optin_manager.sfa.trust.certificate import Certificate, Keypair, convert_public_key
from openflow.optin_manager.sfa.trust.gid import create_uuid
from openflow.optin_manager.sfa.trust.auth import Auth
from openflow.optin_manager.sfa.trust.hierarchy import Hierarchy
from openflow.optin_manager.sfa.util.xrn import Xrn, get_authority, hrn_to_urn, urn_to_hrn


class MetaSfaRegistry:
  
    sfa_gid_location = '/sfa/jfed_roots/ocf_of.gid'

    def __init__(self, config=None):
        self.gid = settings.CONF_DIR + self.sfa_gid_location

    def get_trusted_certs(self,cert=None):
        f = open(self.gid,'r')
        gid = f.read()
        f.close()
        return [gid]


