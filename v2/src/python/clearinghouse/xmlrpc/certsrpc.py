'''
Contains utilities for obtaining and storing CA information
and creating and signing x509 certs remotely from a CA.

Created on Apr 23, 2010

@author: jnaous
'''
from rpc4django.rpcdispatcher import rpcmethod

@rpcmethod(signature=['string', 'string', 'string', 'string'])
def sign_x509_cert(username, password, cert_req):
    '''
    Sign the certificate request in 'cert_req' as authorized by the user
    'username' with password 'password'. Returns a PEM encoded certificate.
    
    @param username: username of the user authorizing the signature request
    @paramtype username: string
    @param password: password of the user authorizing the request
    @paramtype password: string
    @param cert_req: PEM-encoded certificate request
    @param cert_req: string
    @return signed certificate
    @returntype string
    '''
    pass
