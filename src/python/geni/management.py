'''
Created on Jul 10, 2010

@author: jnaous
'''
from django.conf import settings
import os
import logging
from django.db.models import signals
import uuid

logger = logging.getLogger("geni-syncdb")

def create_expedient_x509():
    """
    Create the expedient certificate and keys for use in GENI API.
    """
    from gcf.sfa.trust import gid, certificate
    urn = settings.GENI_URN
    newgid = gid.GID(create=True, subject=urn, urn=urn, uuid=gid.create_uuid())
    keys = certificate.Keypair(create=True)
    newgid.set_pubkey(keys)
    newgid.set_issuer(keys, subject=urn)
    newgid.encode()
    newgid.sign()
    newgid.save_to_file(settings.GENI_X509_CERT)
    keys.save_to_file(settings.GENI_X509_KEY)

def create_expedient_target_gid():
    """
    Create and return a GID with no target.
    """
    return create_slice_gid()

def create_expedient_cred():
    """
    Create a credential that allows Expedient to do everything.
    """
    from gcf.sfa.trust import gid, credential, rights
    gid = gid.GID(filename=settings.GENI_X509_CERT)
    ucred = credential.Credential()
    ucred.set_gid_caller(gid)
    ucred.set_gid_object(create_expedient_target_gid()[0])
    # TODO: This should be in settings.
    ucred.set_lifetime(36000)
    privileges = rights.determine_rights('sa', None)
    privileges.add('embed')
    privileges.add('refresh')
    privileges.add('resolve')
    privileges.add('info')
    ucred.set_privileges(privileges)
    ucred.encode()
    ucred.set_issuer_keys(settings.GENI_X509_KEY, settings.GENI_X509_CERT)
    ucred.sign()
    ucred.save_to_file(filename=settings.GENI_CRED)
    
def create_slice_gid():
    """
    Create a gid for a slice and return it and its keys.
    
    @return: new Slice GID and Slice keys.
    @rtype: (C{gcf.sfa.trust.gid.GID} instance, C{gcf.sfa.trust.certificate.Keypair} instance)
    """
    from gcf.sfa.trust import gid, certificate
    urn = "%s+slice+%s" % (settings.GENI_URN, uuid.uuid4())
    newgid = gid.GID(create=True, uuid=gid.create_uuid(), urn=urn)
    keys = certificate.Keypair(create=True)
    newgid.set_pubkey(keys)
    issuer_key = certificate.Keypair(filename=settings.GENI_X509_KEY)
    issuer_cert = gid.GID(filename=settings.GENI_X509_CERT)
    newgid.set_issuer(issuer_key, cert=issuer_cert)
    newgid.set_parent(issuer_cert)
    newgid.encode()
    newgid.sign()
    return newgid, keys
    
def create_slice_credential(user_gid, slice_gid):
    """
    Create credentials for the slice for user_gid to use.
    
    @param user_gid: The certificate of the user.
    @type user_gid: C{gcf.sfa.trust.gid.GID} instance
    @param slice_gid: the certificate of the slice.
    @return slice_gid: C{gcf.sfa.trust.gid.GID} instance
    """
    from gcf.sfa.trust import credential, rights
    ucred = credential.Credential()
    ucred.set_gid_caller(user_gid)
    ucred.set_gid_object(slice_gid)
    # TODO: this should be in settings
    ucred.set_lifetime(36000)
    privileges = rights.determine_rights('user', None)
    privileges.add('embed')
    # TODO: This should be 'control', not 'sa', but
    # renewsliver is only an 'sa' privilege at this time.
    privileges.add('sa')
    ucred.set_privileges(privileges)
    ucred.encode()
    ucred.set_issuer_keys(settings.GENI_X509_KEY, settings.GENI_X509_CERT)
    ucred.sign()
    return ucred        

def _mkdirs(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if "File exists" in e:
            pass
        else:
            raise
    
# Check if we already have cert and keys created for expedient
def check_and_create_auth(sender, **kwargs):
    """
    Check to see if the gid cert, keys, and credentials are readable, and
    create them if not.
    """
    if not os.access(settings.GENI_X509_CERT, os.R_OK):
        logger.info("Creating GENI API Certificate and KEY.")
        _mkdirs(os.path.dirname(settings.GENI_X509_KEY))
        create_expedient_x509()
    
    if not os.access(settings.GENI_CRED, os.R_OK):
        logger.info("Creating GENI API Credentials.")
        _mkdirs(os.path.dirname(settings.GENI_CRED))
        create_expedient_cred()

# Request to run check_and_create_auth after syncdb
signals.post_syncdb.connect(check_and_create_auth)
