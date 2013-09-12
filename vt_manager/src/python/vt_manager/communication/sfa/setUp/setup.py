from vt_manager.communication.sfa.setUp.authority_create import create_authority
#from vt_manager.communication.sfa.setUp import setup_config as conf


authority_list =  conf.AUTHORITY_XRN.split('.')
path =""
for auth in authority_list:
   path += auth
   create_authority(path)
   path += '.'






