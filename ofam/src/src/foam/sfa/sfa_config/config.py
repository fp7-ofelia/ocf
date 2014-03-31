import foam.ofeliasettings.localsettings as settings
#################
#Credential stuff
#################
SFA_DATA_DIR = "/opt/ofelia/ofam/local/lib/foam/sfa/my_roots/"
SFA_INTERFACE_HRN ="ocf.ofelia.i2cat"
MY_ROOTS_DIR = "/opt/ofelia/ofam/local/lib/foam/sfa/my_roots/"
TRUSTED_ROOTS_DIR = "/opt/ofelia/ofam/local/lib/foam/sfa/trusted_roots/"
SFA_CREDENTIAL_SCHEMA = "/opt/ofelia/ofam/local/lib/foam/sfa/schemas/credential.xsd"

###################
#Get Version Params
###################
#Main params
URN = 'urn:publicid:IDN+ocf:ofam+authority+sa' 
HOSTNAME = settings.SITE_DOMAIN
HRN = 'ocf.ofam'
TESTBED = 'Ofelia Control Framework'
#Geni API
GENI_API_VERSION = 2
GENI_API_URL = 'https://%s/sfa/2/' % settings.SITE_IP_ADDR
INTERFACE = 'aggregate'
CODE_URL = 'git://git.onelab.eu/sfa.git@sfa-2.1-24'
CODE_TAG = '2.1-24'
SFA_VERSION = 2
#Advertisement RSpec Version
AD_RS_VERSION_TYPE = 'OcfOf'
AD_RS_VERSION_NUMBER = '1'
AD_RS_VERSION_SCHEMA = 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/ad.xsd'
AD_RS_VERSION_EXTENSIONS = ['http://www.geni.net/resources/rspec/ext/openflow/3']
AD_RS_NAMESPACE = None
#Request RSpec Version
REQ_RS_VERSION_TYPE = 'GENI'
REQ_RS_VERSION_NUMBER = '3'
REQ_RS_VERSION_SCHEMA = 'http://www.geni.net/resources/rspec/3/request.xsd'
REQ_RS_VERSION_EXTENSIONS = ['http://www.geni.net/resources/rspec/ext/openflow/3']
REQ_RS_NAMESPACE = None

####################
#F4F Required Params
####################
DESCRIBE_TESTBED = "Ofelia Control Framework OpenFlow Aggregate Manager. With this AM the users can request FlowSpaces and makes experiment using OpenFlow resources" 
TESTBED_HOMEPAGE = "http://alpha.fp7-ofelia.eu"
TESTBED_PICTURE = "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQu0YdZrP5OXzO_ycZ-XSmKCbmk3M5aej59N31JyOMoXeLGB2smVg"
#Endorsed Tools
ENDORSED_TOOLS = [{
                    'f4f_tool_name': '',
                    'f4f_tool_logo' : '',
                    'f4f_tool_homepage' : '',
                    'f4f_tool_version' : '',
                  },
                 ]

###################
#Compressed Values----Recomended to use----- 
###################
GENI_API_VERSIONS = { str(GENI_API_VERSION):GENI_API_URL }


GENI_AD_RSPEC_VERSIONS = [{ 'namespace':AD_RS_NAMESPACE,
                            'version':str(AD_RS_VERSION_NUMBER),
                            'type':AD_RS_VERSION_TYPE,
                            'extensions':AD_RS_VERSION_EXTENSIONS,
                            'schema': AD_RS_VERSION_SCHEMA,},
                         ]   

GENI_REQUEST_RSPEC_VERSIONS = [{ 'namespace':REQ_RS_NAMESPACE,
                                 'version':str(REQ_RS_VERSION_NUMBER),
                                 'type':REQ_RS_VERSION_TYPE,
                                 'extensions':REQ_RS_VERSION_EXTENSIONS,
                                 'schema': REQ_RS_VERSION_SCHEMA,},
                               ] 








