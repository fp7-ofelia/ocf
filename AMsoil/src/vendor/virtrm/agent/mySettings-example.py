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
# Settings for virtualization AM server, to which the agent connects
# VTAM_PORT: it is usually '8445'
#
# WARNING: *same* settings as in vt_manager's 'mySettings.py' file
#
VTAM_IP = "192.168.254.193"
VTAM_PORT = "8445"
XMLRPC_USER = "changeMe"
XMLRPC_PASS = "changeMe"

#
# Password for the agent HTTP XML-RPC server. Use a STRONG password
#
XMLRPC_SERVER_PASSWORD = "changeMe"




### Section 2: Optional OXA settings
#
# Optional settings for the Agent.
# 
# WARNING: default values are commented. Uncomment and modify to override
# the static settings (file at 'settings/staticSettings.py').

#
# Network parameters.
# XMLRPC_SERVER_LISTEN_HOST: you should not use '' here unless you have a real FQDN.
# Defaults are as follows.
#
##XMLRPC_SERVER_LISTEN_HOST = "0.0.0.0"
##XMLRPC_SERVER_LISTEN_PORT = 9229

#
# Enable/Disable the usage of cache.
# Default is True.
#
##OXA_FILEHD_USE_CACHE = True

#
# Use sparse disks or not while cloning.
# Uncomment if willing to use Sparse disks.
# Default is False.
#
##OXA_FILEHD_CREATE_SPARSE_DISK = False

#
# Define machine SWAP size in MB.
# Default is 512.
#
##OXA_DEFAULT_SWAP_SIZE_MB = 512

#
# Level used for logging Agent messages.
# Possible values = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}.
# Default is "WARNING".
#
##LOG_LEVEL = "WARNING"
