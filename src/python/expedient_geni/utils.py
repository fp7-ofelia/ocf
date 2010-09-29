'''Utility functions.
Created on Sep 13, 2010

@author: jnaous
'''
import os
from django.conf import settings
from geni.util.urn_util import URN
from geni.util.cert_util import create_cert
from sfa.trust.certificate import Keypair
from sfa.trust.gid import GID

def get_user_cert_fname(user):
    """Get the filename of the user's GCF x509 certificate.
    
    @param user: The user whose certificate filename we want.
    @type user: L{django.contrib.auth.models.User}
    
    @return: The certificate absolute path
    @rtype: C{str}
    """
    
    return os.path.join(
        settings.GCF_X509_CERT_DIR,
        settings.GCF_X509_USER_CERT_FNAME_PREFIX + user.username + ".crt"
    )
    
def get_user_key_fname(user):
    """Get the filename of the user's GCF x509 certificate key.
    
    @param user: The user whose certificate key filename we want.
    @type user: L{django.contrib.auth.models.User}
    
    @return: The certificate key's absolute path
    @rtype: C{str}
    """
    
    return os.path.join(
        settings.GCF_X509_KEY_DIR,
        settings.GCF_X509_USER_CERT_FNAME_PREFIX + user.username + ".key"
    )

def get_user_urn(user):
    """Get a user's URN
    
    @param user: The user whose URN we want.
    @type user: L{django.contrib.auth.models.User}
    
    @return: The URN
    @rtype: C{str}
    """
    
    return URN(settings.GCF_BASE_NAME, "user", user.username).urn_string()

def create_x509_cert(urn, cert_fname, key_fname):
    """Create a GCF certificate and store it in a file.
    
    @param urn: The urn to use in the cert.
    @param cert_fname: The filename to store the cert in.
    @param key_fname: The filename to store the certificate key in.
    """
    cert, keys = create_cert(
        urn,
        settings.GCF_X509_CH_KEY,
        filename=settings.GCF_X509_CH_CERT)
    
    cert.save_to_file(cert_fname)
    keys.save_to_file(key_fname)
    
def read_cert_from_file(cert_fname):
    """Read a GCF certificate from a file.
    
    Read the certificate from a file and put it into a C{sfa.trust.gid.GID}
    object. The returned certificate is already decoded.
    
    @param cert_fname: The filename to read the cert from
    @type cert_fname: C{str}
    @return: The certificate stored in the file at C{cert_fname}
    @rtype: C{sfa.trust.gid.GID}
    """
    
    cert = GID(filename=cert_fname)
    cert.decode()
    return cert
