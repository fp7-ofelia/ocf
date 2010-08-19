'''Settings for XML-RPC calls
Created on Aug 18, 2010

@author: jnaous
'''
from os.path import dirname, join
_SRC_DIR = join(dirname(__file__), '../../../../')

XMLRPC_TRUSTED_CA_PATH = join(_SRC_DIR, '../ssl.crt')
'''The path that contains the certificates for trusted CAs. This folder must
contain a Makefile to keep hashed symbolic links to the
certificates up-to-date.'''
