import logging

##General Parameters

'''Base folder where vms and logs will be store.
All the rest of folder must be inside this folder'''

#Log level. Should be: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
#Default warning
LOG_LEVEL="WARNING"

'''XMLRPC over HTTPS server parameters'''
XMLRPC_SERVER_LISTEN_HOST='0.0.0.0' # You should not use '' here, unless you have a real FQDN.
XMLRPC_SERVER_LISTEN_PORT=9445

XMLRPC_SERVER_KEYFILE='security/certs/sr_am.key'    # Replace with your PEM formatted key file
XMLRPC_SERVER_CERTFILE='security/certs/sr_am.crt'  # Replace with your PEM formatted certificate file

