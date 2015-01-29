from am.settings.src.settings import Settings
from django.conf import settings

class OptinConfig(Settings):

    """ Class to OVERRIDE the AMBASE Default Settings"""
    def __init__(self):
       super(Settings, self).__init__()

    """Default Authority Settings"""
    HRN = "ocf.i2cat"
    SFA_INTERFACE_HRN = "ambase"
    
    TRUSTED_ROOTS_DIR = settings.SRC_DIR + "/python/openflow/optin_manager/geni/v3/trusted_roots/"
    SFA_CREDENTIAL_SCHEMA = settings.AM_LIB_LOCATION + "/ext/schemas/credential.xsd"
    ROOT_CERT_LOCATION = TRUSTED_ROOTS_DIR + "/topdomain.gid"
    CM_HRN = HRN + ".ofam"
    
    AD_RSPEC_TYPE = "GENI"
    AD_RSPEC_VERSION = 3
    AD_RSPEC_SCHEMA = "http://www.geni.net/resources/rspec/3/ad.xsd"
    AD_RSPEC_NAMESPACE = "http://www.geni.net/resources/rspec/3"
    AD_RSPEC_EXTENSIONS = [{"openflow":"http://www.geni.net/resources/rspec/ext/openflow/3"}]
   
    REQ_RSPEC_EXTENSIONS = [{"openflow":"http://www.geni.net/resources/rspec/ext/openflow/3"}]
     
    GENI_API_VERSION = 3
    AM_URL = "https://137.222.204.27:8443/xmlrpc/geni/3/"
