"""
Basic settings for the dummy AM.

@date: Jul 3, 2013
@author: CarolinaFernandez
"""

#
# Authentication data. Set the user and password
# of your choice to communicate against the AM.
# Do NOT modify the rest.
#
XMLRPC_SERVER_USER = "user"
XMLRPC_SERVER_PASSWORD = "password"
XMLRPC_SERVER_KEYFILE = "security/certificates/sr_am.key"
XMLRPC_SERVER_CERTFILE = "security/certificates/sr_am.crt"

#
# Log level. Should be one of the following: 'DEBUG',
# 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
#
LOG_LEVEL = "WARNING"

#
# Network parameters.
#
# XMLRPC_SERVER_LISTEN_HOST: you should not use ''
# here, unless you have a real FQDM
#
XMLRPC_SERVER_LISTEN_HOST = "0.0.0.0"
XMLRPC_SERVER_LISTEN_PORT = 9445

