class Settings:
    import os
    OCF_PATH = os.getenv("OCF_PATH")
    
    SFA_DATA_DIR = os.path.join(OCF_PATH, "optin_manager/src/python/openflow/optin_manager/sfa/my_roots/")
    SFA_INTERFACE_HRN = "ambase"
    MY_ROOTS_DIR = os.path.join(OCF_PATH, "core/lib/am/ext/my_roots/")
    ROOT_CERT = os.path.join(MY_ROOTS_DIR, "topdomain.gid")
    TRUSTED_ROOTS_DIR = os.path.join(OCF_PATH, "core/lib/am/ext/trusted_roots/")
    SFA_CREDENTIAL_SCHEMA = os.path.join(OCF_PATH, "optin_manager/src/python/openflow/optin_manager/sfa/schemas/credential.xsd")

    """Default Authority Settings"""
    HRN = "MyAuthority"

    """ Delegate Settings """
    REQ_RSPEC_TYPE = "GENI"
    REQ_RSPEC_VERSION = 3
    REQ_RSPEC_SCHEMA = "http://www.geni.net/resources/rspec/3/request.xsd"
    REQ_RSPEC_NAMESPACE = "http://www.geni.net/resources/rspec/3"
    REQ_RSPEC_EXTENSIONS = []

    AD_RSPEC_TYPE = "GENI"
    AD_RSPEC_VERSION = 3
    AD_RSPEC_SCHEMA = "http://www.geni.net/resources/rspec/3/ad.xsd"
    AD_RSPEC_NAMESPACE = "http://www.geni.net/resources/rspec/3"
    AD_RSPEC_EXTENSIONS = []

    GENI_API_VERSION = 3
    AM_URL = "https://llull.ctx.i2cat.net:8445/xmlrpc/geni/3"
    CREDENTIAL_TYPE = "geni_sfa" 
    AM_TYPE = "GENI"
    AM_CODE_VERSION = 2.7
