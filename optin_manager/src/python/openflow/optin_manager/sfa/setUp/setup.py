from openflow.optin_manager.sfa.setUp.credential_create import create_credential
from openflow.optin_manager.sfa.setUp.authority_create import create_authority
#XXX: Use the Clearinghouse
#from openflow.optin_manager.sfa.setUp import setup_config as conf


authority_list =  conf.AUTHORITY_XRN.split('.')
path =""
for auth in authority_list:
   path += auth
   create_authority(path)
   path += '.'



#create_credential(conf.AUTHORITY_XRN.split('.')[0]) #creating credentials for top level authority avoiding problems for now.



