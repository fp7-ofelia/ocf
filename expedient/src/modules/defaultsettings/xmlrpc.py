'''Settings for XML-RPC calls
Created on Aug 18, 2010

@author: jnaous
'''
from os.path import join
from django import CONF_DIR

XMLRPC_TRUSTED_CA_PATH = join(CONF_DIR, 'xmlrpc-ssl.crt')
'''The path that contains the certificates for trusted CAs. This folder must
contain a Makefile to keep hashed symbolic links to the
certificates up-to-date.

Use the management command install_cert_makefile to such a Makefile
in this directory.

Example: /etc/apache2/ssl.crt

'''
