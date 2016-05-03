from am.settings.src.settings import Settings
from django.conf import settings 

class VTAMConfig(Settings):

    """ Class to OVERRIDE the AMBASE Default Settings"""
    def __init__(self):
       super(Settings, self).__init__() 
    
    """Default Authority Settings"""
    HRN = "ocf.i2cat"
    SFA_INTERFACE_HRN = "ambase"

    # In MB, average HD size and memory offered by VTAM
    HD_SIZE_AVERAGE_MB = 8*1024
    MEMORY_AVERAGE_MB = 512
    
    TRUSTED_ROOTS_DIR = settings.SRC_DIR + "python/vt_manager/communication/geni/v3/trusted_roots/"
    SFA_CREDENTIAL_SCHEMA = settings.AM_LIB_LOCATION + "/ext/schemas/credential.xsd"
    ROOT_CERT_LOCATION = TRUSTED_ROOTS_DIR + "/topdomain.gid"
    CM_HRN = HRN + ".vtam"
    
    FOREIGN_HRN = "openflow." + HRN + ".ofam"
