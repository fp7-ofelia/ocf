'''
	@author: msune

	Ofelia XEN Agent user settings file. 
'''


'''HTTP XML-RPC Server. You must define it!!!'''
#YOU MUST PUT A STRONG PASSWORD
XMLRPC_SERVER_PASSWORD="changeMe"

'''[Optional]Network parameters. Uncomment only if you want to override settings'''
#XMLRPC_SERVER_LISTEN_HOST='0.0.0.0' # You should not use '' here, unless you have a real FQDN.
#XMLRPC_SERVER_LISTEN_PORT=9229

'''[Optional]Enable/disable the usage of Cache. If line is commented, default is to use it'''
#OXA_FILEHD_USE_CACHE=True

'''[Optional]Use sparse disks while cloning. Uncomment to use Sparse disks. Default is False'''
#OXA_FILEHD_CREATE_SPARSE_DISK=False

'''[Optional]Define machine SWAP size. Default'''
#OXA_DEFAULT_SWAP_SIZE_MB=512

#Possible values are "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL". If not specified default is "WARNING"
#LOG_LEVEL="DEBUG"
