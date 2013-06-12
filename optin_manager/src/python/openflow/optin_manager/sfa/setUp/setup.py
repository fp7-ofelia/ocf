from openflow.optin_manager.sfa.setUp.credential_create import create_credential
from openflow.optin_manager.sfa.setUp.authority_create import create_authority
from openflow.optin_manager.sfa.setUp import setup_config as conf

create_authority(conf.AUTHORITY_XRN,conf.SUBJECT)
create_credential(con.AUTHORITY_XRN.split('.')[0]) #creating credentials for top level authority avoiding problems for now.



