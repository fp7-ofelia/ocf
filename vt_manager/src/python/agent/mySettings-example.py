'''
Ofelia XEN Agent user settings file. 

@author: msune, CarolinaFernandez
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: OXA settings
#
# Basic settings for the Ofelia XEN Agent

#
# Password for the HTTP XML-RPC Server. Use a STRONG password
#
XMLRPC_SERVER_PASSWORD="changeMe"




### Section 2: Optional OXA settings
#
# Optional settings for the Agent. Uncomment to override settings.

#
# Network parameters.
# XMLRPC_SERVER_LISTEN_HOST: you should not use '' here unless you have a real FQDN.
#
##XMLRPC_SERVER_LISTEN_HOST='0.0.0.0'
##XMLRPC_SERVER_LISTEN_PORT=9229

#
# Enable/Disable the usage of cache.
# Default is set to True (to use it).
#
##OXA_FILEHD_USE_CACHE=True

#
# Use sparse disks while cloning.
# Default is false. Uncomment to use Sparse disks.
#
##OXA_FILEHD_CREATE_SPARSE_DISK=False

#
# Define machine SWAP size in MB.
# Default is 512.
#
##OXA_DEFAULT_SWAP_SIZE_MB=512

#
# Level used for logging Agent messages.
# Possible values = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}.
# Default is "WARNING".
#
##LOG_LEVEL="DEBUG"
