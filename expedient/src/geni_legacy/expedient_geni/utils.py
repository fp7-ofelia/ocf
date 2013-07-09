'''Utility functions.
Created on Sep 13, 2010

@author: jnaous
'''
import os
import re
from django.conf import settings
from geni.util.urn_util import URN
from geni.util.cert_util import create_cert
from sfa.trust.gid import GID
from django.core.urlresolvers import reverse
from geni.util import cred_util
import uuid

def get_user_cert_fname(user):
    """Get the filename of the user's GCF x509 certificate.
    
    @param user: The user whose certificate filename we want.
    @type user: L{django.contrib.auth.models.User}
    
    @return: The certificate absolute path
    @rtype: C{str}
    """
    
    return os.path.join(
        settings.GCF_X509_USER_CERT_DIR,
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

def get_user_urn(username):
    """Get a user's URN
    
    @param username: The username of the user whose URN we want.
    @type username: C{str}
    
    @return: The URN
    @rtype: C{str}
    """
    
    return URN(
        str(settings.GCF_BASE_NAME), str("user"), str(username)
    ).urn_string()

def get_ch_urn():
    """Get the URN for Expedient as a clearinghouse.
    
    @return: The URN
    @rtype: C{str}
    """
    
    return URN(
        settings.GCF_BASE_NAME, "authority", "sa",
    ).urn_string()

def get_slice_urn(name):
    """Get the URN for a slice with name C{name}.
    
    @param name: Name of the slice. Must be unique.
    @type name: C{str}
    @return: a slice URN
    @rtype: C{str}
    
    """
    return URN(
        settings.GCF_BASE_NAME, "slice", name,
    ).urn_string()

def create_slice_urn():
    """Create a urn for the slice."""
    return get_slice_urn(uuid.uuid4().__str__()[4:12])

def create_x509_cert(urn, cert_fname=None, key_fname=None, is_self_signed=False):
    """Create a GCF certificate and store it in a file.
    
    @param urn: The urn to use in the cert.
    @type urn: C{str}
    @keyword cert_fname: The filename to store the cert in.
        If None (default), then don't store.
    @type cert_fname: C{str}
    @keyword key_fname: The filename to store the certificate key in.
        If None (default), then don't store.
    @type key_fname: C{str}
    @keyword is_self_signed: should the certificate be self-signed? Otherwise
        it will be signed by Expedient's CH certificate. Default False.
    @type is_self_signed: C{bool}
    @return: tuple (cert, keys)
    @rtype: (C{sfa.trust.gid.GID}, C{sfa.trust.certificate.Keypair})
    
    """
    if is_self_signed:
        cert, keys = create_cert(
            urn,
        )
    else:
        cert, keys = create_cert(
            urn,
            issuer_key=settings.GCF_X509_CH_KEY,
            issuer_cert=settings.GCF_X509_CH_CERT
        )
    
    cert.decode()
    
    if cert_fname: cert.save_to_file(cert_fname)
    if key_fname: keys.save_to_file(key_fname)
    
    return cert, keys
    
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

def describe_ui_plugin(slice):
    """Describes the UI plugin according to L{expedient.clearinghouse.defaultsettings.expedient.UI_PLUGINS}."""
    return ("GCF RSpec Plugin",
            "Allows the user to modify the slice by uploading"
            " RSpecs or to download an RSpec of the slice.",
            reverse("gcf_rspec_ui", slice.id))
    
def urn_to_username(urn):
    """Create a valid username from a URN.
    
    This creates the username by taking the authority part of
    the URN, and the name part of the URN and joining them with "@".
    
    Any characters other than letters, digits, '@', '-', '_', '+', and '.'
    are replace with '_'.
    
    e.g. "urn:publicid:IDN+stanford:expedient%26+user+jnaous" becomes 
    "jnaous@expedient_26.stanford"
    
    The authority part of the URN is truncated to 155 characters, and the
    name part is truncated to 100 characters.
    
    @param urn: a urn to turn into a username
    @type urn: C{str}
    @return: a valid username
    @rtype: C{str}
    """
    
    invalid_chars_re = re.compile(r"[^\w@+.-]")
    
    urn = URN(urn=str(urn))
    auth = urn.getAuthority()
    auth = auth.split("//")
    auth.reverse()
    auth = ".".join(auth)
    if len(auth) > 150:
        auth = auth[:150]
        
    name = urn.getName()
    if len(name) > 100:
        name =name[:100]
        
    username = name + "@" + auth
    
    # replace all invalid chars with _
    username = invalid_chars_re.sub("_", username)
    
    assert(len(username) <= 255)
    
    return username
    
def get_trusted_cert_filenames():
    """Return list of paths to files containing trusted certs."""

    filenames = os.listdir(settings.GCF_X509_TRUSTED_CERT_DIR)
    filenames = [os.path.join(settings.GCF_X509_TRUSTED_CERT_DIR, f) \
                 for f in filenames]
    trusted_certs = []
    for f in filenames:
        if f.endswith(".crt") and os.path.isfile(f):
            trusted_certs.append(f)
    
    return trusted_certs
    
def create_slice_credential(user_gid, slice_gid):
    '''Create a Slice credential object for this user_gid (object) on given slice gid (object)
    
    @param user_gid: The user's cert
    @type user_gid: C{sfa.trust.gid.GID}
    @param slice_gid: The slice's gid
    @type slice_gid: C{sfa.trust.gid.GID}
    @return: The credential
    @rtype: C{sfa.trust.credential.Credential}
    '''
    
    return cred_util.create_credential(
        user_gid, slice_gid, settings.GCF_SLICE_CRED_LIFE,
        'slice',
        settings.GCF_X509_CH_KEY, settings.GCF_X509_CH_CERT,
        get_trusted_cert_filenames(),
    )

def create_user_credential(user_gid):
    '''Create a user credential object for this user_gid
    
    @param user_gid: The user's cert
    @type user_gid: C{sfa.trust.gid.GID}
    @return: The credential
    @rtype: C{sfa.trust.credential.Credential}
    '''
    
    return cred_util.create_credential(
        user_gid, user_gid, settings.GCF_USER_CRED_LIFE,
        'user',
        settings.GCF_X509_CH_KEY, settings.GCF_X509_CH_CERT,
        get_trusted_cert_filenames(),
    )

def get_or_create_user_cert(user):
    """Get the user's cert, creating it if it doesn't exist."""
    
    cert_fname = get_user_cert_fname(user)
    key_fname = get_user_key_fname(user)
    urn = get_user_urn(user.username)
    if not os.access(cert_fname, os.R_OK):
        cert, _ = create_x509_cert(urn, cert_fname, key_fname)
    else:
        cert = read_cert_from_file(cert_fname)
    return cert
